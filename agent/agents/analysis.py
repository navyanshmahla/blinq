import litellm
import yaml
import polars as pl
import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from prompts.prompts import PROMPT_ANALYSIS
from tools.tools import Tools

load_dotenv()

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs.yaml")
with open(config_path, "r") as f:
    configs = yaml.safe_load(f)

if configs['run_state'] == "integrated":
    from message_broker import KafkaProducer

MODEL_ANALYSIS_AGENT = configs['models']['MODEL_ANALYSIS_AGENT']

class analysisAgent():
    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.tools = Tools(df)
        if configs['run_state'] == "integrated":
            self.kafka_producer = KafkaProducer()

    async def sql(self, query: str):
        """Execute SQL query on dataframe"""
        return self.tools.sql(query)

    async def plot(self, code: str):
        """Execute matplotlib plotting code and return image bytes"""
        try:
            clean_code = code.strip()
            if clean_code.startswith('```python'):
                clean_code = clean_code[9:]
            if clean_code.startswith('```'):
                clean_code = clean_code[3:]
            if clean_code.endswith('```'):
                clean_code = clean_code[:-3]
            clean_code = clean_code.strip()

            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import io
            import base64

            env = {"df": self.df, "plt": plt, "io": io}
            exec(clean_code, env)

            if 'result' not in env:
                return {"error": "Code execution completed but 'result' variable was not assigned. Make sure to assign the matplotlib figure to 'result' variable.", "status": "failed"}

            fig = env['result']
            if fig is None:
                return {"error": "'result' variable is None. Make sure to assign a valid matplotlib figure object to 'result'.", "status": "failed"}
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            image_bytes = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)

            result = {
                "image_bytes": image_bytes,
                "status": "success",
                "message": "Plot created successfully"
            }

            if configs['run_state'] == "integrated":
                await self.kafka_producer.send_plot_notification(result)
            else:
                try:
                    output_path = os.path.join(os.path.dirname(__file__), "plot_output.png")
                    with open(output_path, "wb") as f:
                        f.write(base64.b64decode(image_bytes))
                    result["local_path"] = output_path
                    print(f"[DEBUG] Plot saved to: {output_path}")
                except Exception as save_err:
                    result["warning"] = f"Failed to save plot locally: {str(save_err)}"
                    print(f"[DEBUG] Failed to save plot: {str(save_err)}")

            return result
        except Exception as e:
            error_result = {"error": str(e), "status": "failed", "message": f"Plotting failed: {str(e)}"}
            print(f"[DEBUG] Plot error: {str(e)}")
            return error_result
            



TOOLS_ANALYSIS = [
    {
        "type": "function",
        "function": {
            "name": "sql",
            "description": "Execute a SQL query using polars",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The SQL query to execute on the dataframe"},
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "plot",
            "description": "Create a matplotlib visualization and return image bytes. The bytes are automatically sent to frontend via WebSocket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code that creates a matplotlib figure. Must use Polars DataFrame 'df' and assign final figure to 'result' variable. Returns base64-encoded PNG bytes."},
                },
                "required": ["code"]
            }
        }
    }
]

async def get_func_mapper_analysis_agent(df: pl.DataFrame):
    agent = analysisAgent(df)
    return {
        "sql": agent.sql,
        "plot": agent.plot
    }

async def run_analysis_agent(df: pl.DataFrame, input: str = None, messages: list = None, prompt: str = None):

    func_mapper = await get_func_mapper_analysis_agent(df)

    if input:
        if prompt is None:
            prompt = PROMPT_ANALYSIS
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": input
            }
        ]
    elif messages:
        messages = messages
    else:
        raise ValueError("No input or messages provided")

    context = messages.copy()
    response = await litellm.acompletion(
        model = MODEL_ANALYSIS_AGENT,
        messages = messages,
        tools = TOOLS_ANALYSIS,
        tool_choice = "auto",
        seed = 42
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls is None or len(tool_calls) == 0:
        return response_message.content

    if tool_calls is not None and len(tool_calls) > 0:
        context.append(response_message)
        for tool_call in tool_calls:
            import json
            print(f"Calling function: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}")
            func_mapper = await get_func_mapper_analysis_agent(df)
            function = func_mapper[tool_call.function.name]
            args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
            result = await function(**args)
            if tool_call.function.name == "plot":

                context.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": str({k: v for k, v in result.items() if k != "image_bytes"})
                    })
            else:
                context.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": str(result)
                    })

        final_result = await run_analysis_agent(df, messages=context)
        if final_result is None:
            raise ValueError("No result from the analysis agent")
        return final_result
    

ANALYSIS_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "run_analysis_agent",
        "description": "Execute the analysis agent to analyze the dataframe based on the user prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "The user prompt to analyze the dataframe"},
            },
            "required": ["input"]
        }
    }
}