import json

from langgraph.types import Command
from typing import Literal
from src.graph.state import State
from src.llms.llm import get_llm_model
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output
from src.utils.logging import info

def analyze(state: State) -> Command[Literal["__end__"]]:
    msg = apply_prompt_template("analyze", state)
    # info(f"analyze提取的模板信息{msg}")

    llm = get_llm_model()
    res = llm.invoke(msg)
    # info(f"重新排序结果：{res}")

    return Command(
        goto="__end__",
        update={
            "messages": res,
            "ANALYZE_POSTS": json.loads(repaired) if (repaired := repair_json_output(res.content)) else {}
        }
    )