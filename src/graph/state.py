from langgraph.graph import MessagesState
from typing_extensions import TypedDict
from typing import Literal


class State(MessagesState):
    # 常量
    # 直接使用关键字搜索并使用AI分析帖子
    JUST_USE_AI_ANALYZE_BY_KEYWORDS: bool
    # 只需要关键词和子模块
    JUST_NEED_KEYWORDS_SUBREDDITS: bool
    # 子模块
    SUBREDDITS: list[str]
    # 关键字
    KEYWORDS: list[str]
    # 处理后的搜索结果
    POSTS: list[TypedDict]
    # 原始搜索结果
    ORIGIN_POSTS: list[TypedDict]
    # AI分析
    IS_AI_ANALYZE: bool
    # AI 排序结果
    ANALYZE_POSTS: list[TypedDict]
    # 获取reddit帖子数据的时间过滤器
    TIME_FILTER: Literal["all", "day", "hour", "month", "week", "year"]
    # 获取reddit帖子数量 注意这个数量会和关键字相关联，如关键字有5个时，获取帖子数量为5，则会获取5x5=25个帖子
    LIMIT: int

    user_query: str


class WordCloudState(MessagesState):
    WORD_SEG_RESULT: dict[str,str]

    data: str
