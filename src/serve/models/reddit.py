# src/serve/models/reddit.py
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator, field_validator, model_validator

class AnalysisRequest(BaseModel):
    posts_json: str = Field(..., title="帖子JSON", description="帖子JSON内容")

class AIExtractKeywordsRequest(BaseModel):
    desc: str = Field(..., title="产品描述", description="产品描述内容")

    @field_validator("desc")
    def check_desc_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("desc 字段不能为空或空白字符串")
        return v


class AIAnalysisResultRequest(BaseModel):
    """AI分析结果请求"""
    desc: str = Field(None, description="描述")
    just_use_ai_analyze_by_keywords: bool = Field(False, description="是否不使用AI提取")
    just_need_keywords_subreddits: bool = Field(False, description="是否只提取关键词和子版块")
    time_filter: Optional[str] = Field("day", description="时间过滤器")
    is_ai_analyze: bool = Field(False, description="是否需要AI分析")
    keywords: Optional[str] = Field(None, description="关键词，多个以逗号分隔")
    subreddits: Optional[str] = Field(None, description="子版块，多个以逗号分隔")
    limit_count: int = Field(20, description="返回的帖子数量限制")
    limit: int = Field(10, description="返回最终帖子数量限制")

    @model_validator(mode="after")
    def convert_string_to_list(self):
        def ensure_list(value: Union[str, List[str], None]) -> Optional[List[str]]:
            if value is None:
                return []
            if isinstance(value, str):
                return [item.strip() for item in value.split(",") if item.strip()]
            return value

        self.keywords = ensure_list(self.keywords)
        self.subreddits = ensure_list(self.subreddits)

        return self

    @classmethod
    def from_form_data(
            cls,
            desc: str = '',
            just_use_ai_analyze_by_keywords: bool = False,
            just_need_keywords_subreddits: bool = False,
            time_filter: Optional[str] = None,
            is_ai_analyze: bool = False,
            keywords: Optional[str] = None,
            subreddits: Optional[str] = None,
            limit_count: int = 5,
            limit: int = 5
    ):
        """从表单数据构建请求模型"""

        def parse_list_str(s: Optional[str]) -> Optional[List[str]]:
            if not s:
                return []
            return [item.strip() for item in s.split(",") if item.strip()]

        return cls(
            desc=desc,
            just_use_ai_analyze_by_keywords=just_use_ai_analyze_by_keywords,
            just_need_keywords_subreddits=just_need_keywords_subreddits,
            time_filter=time_filter,
            is_ai_analyze=is_ai_analyze,
            keywords=keywords,
            subreddits=subreddits,
            limit_count=limit_count,
            limit=limit
        )


# 请求模型
class TrendingPostsRequest(BaseModel):
    """获取热门帖子请求"""
    limit: int = Field(20, description="返回的帖子数量限制", ge=1, le=100)
    time_filter: Optional[str] = Field(None, description="时间过滤器")
    subreddits: Optional[List[str]] = Field(None, description="要搜索的subreddit列表")


class KeywordPostsRequest(BaseModel):
    """根据关键词查找帖子请求"""
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    subreddits: Optional[List[str]] = Field(None, description="要搜索的subreddit列表")
    limit: int = Field(20, description="返回的帖子数量限制", ge=1, le=100)
    sort: str = Field("relevance", description="排序方式")

    @validator('sort')
    def validate_sort(cls, v):
        allowed_sorts = ['relevance', 'hot', 'top', 'new', 'comments']
        if v not in allowed_sorts:
            raise ValueError(f"排序方式必须是以下之一: {', '.join(allowed_sorts)}")
        return v


class SubredditMonitorRequest(BaseModel):
    """监控subreddit活动请求"""
    subreddit: str = Field(..., description="要监控的subreddit")
    interval: int = Field(3600, description="检查间隔（秒）", ge=60)
    duration: int = Field(86400, description="监控持续时间（秒）", ge=60)


# 响应模型
class RedditPost(BaseModel):
    """Reddit帖子模型"""
    id: str = Field(..., description="帖子ID")
    title: str = Field(..., description="帖子标题")
    author: str = Field(..., description="作者")
    subreddit: str = Field(..., description="所属subreddit")
    score: int = Field(..., description="得分")
    upvote_ratio: float = Field(..., description="上投比例")
    num_comments: int = Field(..., description="评论数")
    created_utc: int = Field(..., description="创建时间（UTC时间戳）")
    url: str = Field(..., description="帖子URL")
    permalink: str = Field(..., description="永久链接")
    is_self: bool = Field(..., description="是否为文本帖子")
    selftext: Optional[str] = Field(None, description="帖子内容")
    keyword: Optional[str] = Field(None, description="匹配的关键词")

    @validator('created_utc', pre=True)
    def format_datetime(cls, v):
        if isinstance(v, datetime):
            return int(v.timestamp())
        return v


class SubredditStat(BaseModel):
    """Subreddit统计信息"""
    count: int = Field(..., description="帖子数量")
    avg_score: float = Field(..., description="平均得分")
    avg_comments: float = Field(..., description="平均评论数")
    total_comments: int = Field(..., description="总评论数")
    total_score: int = Field(..., description="总得分")


class TrendAnalysis(BaseModel):
    """趋势分析结果"""
    total_posts: int = Field(..., description="总帖子数")
    subreddit_stats: Dict[str, SubredditStat] = Field(..., description="各subreddit统计")
    most_active_subreddits: List[List[Any]] = Field(..., description="最活跃的subreddit")
    top_posts_by_score: List[RedditPost] = Field(..., description="得分最高的帖子")
    top_posts_by_comments: List[RedditPost] = Field(..., description="评论最多的帖子")


class TrendAnalysisProfessional(BaseModel):
    """专业趋势分析结果"""
    analysis_metadata: Dict[str, Any] = Field(
        None,
        description="分析元数据，包含总帖子数、时间戳和数据质量评分"
    )
    statistical_summary: Dict[str, Any] = Field(
        None,
        description="统计摘要，包含关键指标的均值、中位数、标准差等统计量"
    )
    temporal_trends: Dict[str, Any] = Field(
        None,
        description="时间趋势分析，展示帖子频率和参与度随时间的变化模式"
    )
    engagement_metrics: Dict[str, Any] = Field(
        None,
        description="参与度指标分析，包含点赞、评论、分享等互动数据的深入分析"
    )
    viral_potential: Dict[str, Any] = Field(
        None,
        description="病毒传播潜力评估，识别可能病毒式传播的内容特征"
    )
    content_insights: Dict[str, Any] = Field(
        None,
        description="内容洞察，包含关键词分析、情感分析和主题建模结果"
    )
    predictions: Dict[str, Any] = Field(
        None,
        description="预测分析，基于历史数据的未来参与度和流行度预测"
    )
    actionable_insights: List[str] = Field(
        None,
        description="可操作建议，针对内容优化的具体建议列表"
    )
    words_cloud: Dict[str, Any] = Field(
        None,
        description="AI分析 词云结果，包含词云图片和词频信息"
    )
    fallback_analysis: Dict[str, Any] = Field(
        None,
        description="回退分析，针对无法进行专业分析的场景，提基础回退分析 - 当专业分析失败时使用"
    )
    error: str = Field(
        None,
        description="错误信息"
    )


class ContentTheme(BaseModel):
    """内容主题"""
    theme: str = Field(..., description="主题名称")
    frequency: int = Field(..., description="出现频率")


class ContentIdea(BaseModel):
    """内容创意"""
    title: str = Field(..., description="创意标题")
    description: str = Field(..., description="创意描述")


class ContentInsight(BaseModel):
    """内容洞察"""
    content_themes: List[ContentTheme] = Field(..., description="内容主题")
    content_ideas: List[ContentIdea] = Field(..., description="内容创意")
    related_keywords: List[str] = Field(..., description="相关关键词")
