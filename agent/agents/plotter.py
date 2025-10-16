import litellm
from dotenv import load_dotenv
import polars as pl
import yaml
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from prompts.prompts import PROMPT_PLOTTER

load_dotenv()

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs.yaml")
with open(config_path, "r") as f:
    configs = yaml.safe_load(f)

if configs['run_state'] == "integrated":
    from message_broker import KafkaProducer

MODEL_PLOTTER_AGENT = configs['models']['MODEL_PLOTTER_AGENT']

class plottingAgent():
    def __init__(self, df: pl.DataFrame):
        self.df = df
        if configs['run_state'] == "integrated":    
            self.kafka_producer = KafkaProducer()

    async def plot_plotly(self, code: str):
        """Plot based on user prompt"""
        try:
            clean_code = code.strip()
            if clean_code.startswith('```python'):
                clean_code = clean_code[9:]
            if clean_code.startswith('```'):
                clean_code = clean_code[3:]
            if clean_code.endswith('```'):
                clean_code = clean_code[:-3]
            clean_code = clean_code.strip()

            env = {"df": self.df}
            exec(clean_code, env)
            return env['result']
        except Exception as e:
            return {"error": str(e), "status": "failed", "message": "Code execution failed. Please retry with corrected code."}
    
    async def plot_plotly_image(self, code: str):
        """Plot based on user prompt and return both plotly JSON and image bytes"""
        try:
            plotly_result = await self.plot_plotly(code)
            if isinstance(plotly_result, dict) and plotly_result.get("status") == "failed":
                return plotly_result

            import plotly.io as pio
            import io
            import base64

            buffer = io.BytesIO()
            plotly_result.write_image(buffer, format='png')
            buffer.seek(0)
            image_bytes = base64.b64encode(buffer.getvalue()).decode('utf-8')

            result = {
                "plotly_json": plotly_result.to_json(),
                "image_bytes": image_bytes,
                "status": "success"
            }
            if configs['run_state'] == "integrated":
                await self.kafka_producer.send_plot_notification(result)

            return result
        except Exception as e:
            return {"error": str(e), "status": "failed", "message": "Image conversion failed. Please retry with corrected code."}


TOOL_PLOTTER_IMAGE = {
    "type": "function",
    "function": {
        "name": "plot_plotly_image",
        "description": "Plot based on user prompt and return both plotly JSON and image bytes",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The code to plot"},
            },
            "required": ["code"]
            }
        }
}


async def get_func_mapper_plotter_agent(df: pl.DataFrame):
    return {
        "plot_plotly_image": plottingAgent(df).plot_plotly_image
    }

async def run_plotter_agent(df: pl.DataFrame, input: str = None, messages: list = None):
    func_mapper = await get_func_mapper_plotter_agent(df)

    if input:
        messages = [
            {
                "role": "system",
                "content": PROMPT_PLOTTER
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
        model = MODEL_PLOTTER_AGENT,
        messages = messages,
        tools = [TOOL_PLOTTER_IMAGE],
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
            if tool_call.function.name == "plot_plotly_image":
                import json
                print(f"Calling function: {tool_call.function.name}")
                print(f"Arguments: {tool_call.function.arguments}")
                func_mapper = await get_func_mapper_plotter_agent(df)
                function = func_mapper[tool_call.function.name]
                args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                result = await function(**args)
                context.append(
                    {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": "Function executed successfully and the plots are sent to the frontend"
                })

        final_result = await run_plotter_agent(df, messages=context)
        if final_result is None:
            raise ValueError("No result from the plotter agent")
        return final_result

PLOTTER_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "run_plotter_agent",
        "description": "Execute the graph plotting agent to plot the graph based on the user prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "input": {"type": "string", "description": "The user prompt to plot the graph of"},
            },
            "required": ["input"]
        }
    }
}