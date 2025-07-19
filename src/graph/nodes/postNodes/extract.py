import json

from langchain_core.messages import HumanMessage
from langgraph.types import Command, interrupt
from typing import Literal
from src.graph.state import State
from src.llms.llm import get_llm_model
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output
from src.utils.logging import info


def extract_keywords(state: State) -> Command[Literal["reddit_data", "__end__"]]:
    if state["JUST_USE_AI_ANALYZE_BY_KEYWORDS"] is True:
        return Command(
            goto="reddit_data",
        )

    msg = apply_prompt_template("keyword_prompt", state)
    info(f"extract_keywords提取的模板信息{msg}")

    llm = get_llm_model()
    res = llm.invoke(msg)
    info(f"提取的结果{res}")

    extract_obj = json.loads(repair_json_output(res.content))
    info(f"字符串转化结果：{extract_obj}")

    kys = (state.get('KEYWORDS') or []) + (extract_obj.get('keywords') or [])
    subreddits = (state.get('SUBREDDITS') or []) + (extract_obj.get('subreddits') or [])

    info(f"提取到的子板块：{subreddits}，提取到的关键词：{kys}")

    if state["JUST_NEED_KEYWORDS_SUBREDDITS"] is False:
        return Command(
            goto="reddit_data",
            update={
                "messages": res,
                "KEYWORDS": kys,
                "SUBREDDITS": subreddits
            }
        )
    else:
        return Command(
            goto="__end__",
            update={
                "messages": res,
                "KEYWORDS": kys,
                "SUBREDDITS": subreddits
            }
        )
