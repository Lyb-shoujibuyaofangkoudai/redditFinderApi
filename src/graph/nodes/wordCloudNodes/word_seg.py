import json

from langchain_core.messages import HumanMessage
from langgraph.types import Command, interrupt
from typing import Literal
from src.graph.state import  WordCloudState
from src.llms.llm import get_llm_model
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output
from src.utils.logging import info


def word_seg(state: WordCloudState) -> Command[Literal["__end__"]]:
    info(f"开始进行分词{state}")
    msg = apply_prompt_template("word_seg_prompt", state)
    info(f"word_seg提取的模板信息{msg}")

    llm = get_llm_model()
    res = llm.invoke(msg)
    info(f"提取的结果{res}")

    extract_obj = json.loads(repair_json_output(res.content))
    info(f"字符串转化结果：{extract_obj}")


    return Command(
        goto="__end__",
        update={
            "messages": res,
            "WORD_SEG_RESULT": extract_obj
        }
    )
