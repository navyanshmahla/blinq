from uuid import uuid4
import litellm
from litellm import completion_cost
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
    def __init__(self, df: pl.DataFrame, request_id: str):
        self.df = df
        self.analysis = analysisAgent(df, request_id)

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


async def run_main_agent(df: pl.DataFrame, input: str = None, messages: list = None, is_plotting: bool = False, request_id: str = None):
    total_cost = 0
    if request_id is None:
        request_id = str(uuid4())

    main_agent = MainAgent(df, request_id)
    enriched_prompt = await main_agent.get_enriched_prompt(PROMPT_ANALYSIS)
    enriched_prompt_main = await main_agent.get_enriched_prompt(PROMPT_MAIN)
    
    FUNC_MAPPER = {
        "run_analysis_agent": partial(run_analysis_agent, df=df, req_id=request_id, prompt=enriched_prompt),
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

    cost = completion_cost(completion_response=response)
    total_cost+=cost

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls is None or len(tool_calls) == 0:
        return response_message.content, total_cost, is_plotting, request_id

    if tool_calls is not None and len(tool_calls) > 0:
        context.append(response_message)
        for tool_call in tool_calls:
            import json
            print(f"Calling function: {tool_call.function.name}")
            print(f"Arguments: {tool_call.function.arguments}")
            
            args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
            function = FUNC_MAPPER[tool_call.function.name]
            result, cost_nested, plot_what = await function(**args)
            is_plotting = plot_what
            total_cost += cost_nested
            context.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_call.function.name,
                "content": str(result)
            })

    final_result, cost_nested, is_plotting_nested, _ = await run_main_agent(df, messages=context, is_plotting=is_plotting, request_id=request_id)
    is_plotting = is_plotting_nested
    total_cost+=cost_nested
    if final_result is None:
        raise ValueError("No result from the main agent")
    return final_result, total_cost, is_plotting, request_id

if __name__ == "__main__":
    import asyncio
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "data.csv")
    df = pl.read_csv(data_path)
    result = asyncio.run(run_main_agent(df, input="Plot me my food vs shopping spends on a bar graph"))
    print(result)