import litellm
import yaml
import polars as pl
from functools import partial
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from agents.analysis import ANALYSIS_AGENT_TOOL, analysisAgent, run_analysis_agent
from prompts.prompts import PROMPT_MAIN, PROMPT_ANALYSIS

config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs.yaml")
with open(config_path, "r") as f:
    configs = yaml.safe_load(f)

MODEL_MAIN = configs['models']['MODEL_MAIN']

class MainAgent():
    def __init__(self, df: pl.DataFrame):
        self.df = df
        self.analysis = analysisAgent(df)

    async def accumulate_context(self):
        """Accumulate context from dataframe analysis"""
        import asyncio
        exploration_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.explore))
        columns_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.columns))
        shape_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.shape))
        head_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.head))
        tail_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.tail))
        info_task = asyncio.create_task(asyncio.to_thread(self.analysis.tools.info))

        exploration = await exploration_task
        columns = await columns_task
        shape = await shape_task
        head = await head_task
        tail = await tail_task
        info = await info_task

        context_string = f"""
        Exploration: {str(exploration)}
        Columns: {str(columns)}
        Shape: {shape}
        Head: {str(head)}
        Tail: {str(tail)}
        Info: {info}
        """
        return context_string

    async def get_enriched_prompt(self, base_prompt: str):
        """Get prompt enriched with dataframe context"""
        context = await self.accumulate_context()
        return base_prompt + "\n\n Here is some CONTEXT regarding the uploaded CSV file:\n" + context


async def run_main_agent(df: pl.DataFrame, input: str = None, messages: list = None):
    main_agent = MainAgent(df)
    enriched_prompt = await main_agent.get_enriched_prompt(PROMPT_ANALYSIS)
    enriched_prompt_main = await main_agent.get_enriched_prompt(PROMPT_MAIN)
    FUNC_MAPPER = {
        "run_analysis_agent": partial(run_analysis_agent, df=df, prompt=enriched_prompt),
    }
    if input:
        messages = [
            {
                "role": "system",
                "content": PROMPT_MAIN
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
        model = MODEL_MAIN,
        messages = messages,
        tools = [ANALYSIS_AGENT_TOOL],
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
            
            args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
            function = FUNC_MAPPER[tool_call.function.name]
            result = await function(**args)
            context.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": str(result)
            })

    final_result = await run_main_agent(df, messages=context)
    if final_result is None:
        raise ValueError("No result from the main agent")
    return final_result

if __name__ == "__main__":
    import asyncio
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data.csv")
    df = pl.read_csv(data_path)
    result = asyncio.run(run_main_agent(df, input="How much have i spent flight bookings?"))
    print(result)