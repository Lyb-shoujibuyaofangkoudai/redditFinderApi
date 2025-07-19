from langgraph.types import Command, interrupt
from typing import Literal

from src.graph.state import State
from src.utils.logging import info


def reddit_data(state: State) -> Command[Literal["analyze","__end__"]]:
    info(f"获取数据的state：{state}")

    if state["KEYWORDS"] is None:
        return Command(
            goto="__end__",
        )

    # 采用局部导入，避免循环引用
    from src.utils.reddit_finder import RedditFinder
    rf = RedditFinder()
    res = rf.find_posts_by_keywords(
        keywords=state["KEYWORDS"],
        limit=state["LIMIT"],
        subreddits=state["SUBREDDITS"],
        time_filter=state["TIME_FILTER"],
    )
    # info(f"获取到的数据：{res}")
    if state["IS_AI_ANALYZE"]:
        return Command(
            goto="analyze",
            update={
                # "messages": res,
                "POSTS": list(map(lambda item: {
                    "title": item.get("title"),
                    "selftext": item.get("selftext"),
                    "id":  item.get("id"),
                    "subreddit": item.get("subreddit"),
                },res)),
                "ORIGIN_POSTS": res
            }
        )
    else:
        return Command(
            goto="__end__",
            update={
                # "messages": res,
                "POSTS": list(map(lambda item: {
                    "title": item.get("title"),
                    "selftext": item.get("selftext"),
                    "id":  item.get("id"),
                    "subreddit": item.get("subreddit"),
                },res)),
                "ORIGIN_POSTS": res
            }
        )