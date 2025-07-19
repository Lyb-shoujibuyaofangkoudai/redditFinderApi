# src/serve/services/reddit_service.py
from typing import Dict, List, Any, Optional, Literal
from functools import lru_cache

from src.graph.builder import build_graph
from src.utils.reddit_finder import RedditFinder
from src.utils.visualization import RedditVisualizer
from src.utils.logging import create_logger, info, error

# 配置日志
logger_config = create_logger("Reddit-Service")

class RedditService:
    """Reddit服务类
    
    封装对RedditFinder的调用，提供API所需的业务逻辑
    """
    
    def __init__(self):
        """初始化Reddit服务"""
        try:
            self.finder = RedditFinder()
            self.app = build_graph()
            self.visualizer = RedditVisualizer(output_dir="./static/charts")
            info("Reddit服务初始化成功", logger_config)
        except Exception as e:
            error(f"Reddit服务初始化失败: {e}", logger_config)
            raise

    def _check_match(self, item, map_data):
        """
        检查item是否与map_data中的某个记录匹配
        匹配条件：ID相同 或者 (title相同 且 selftext相同)
        """
        item_id = item.get("id")
        item_title = item.get("title", "")
        item_selftext = item.get("selftext", "")

        # 首先检查ID匹配
        if item_id and map_data.get(item_id):
            return map_data.get(item_id)

        # 如果ID不匹配，检查title和selftext匹配
        for key, value in map_data.items():
            if (value.get("title", "") == item_title and
                    value.get("selftext", "") == item_selftext and
                    item_title and item_selftext):  # 确保title和selftext不为空
                return value

        return None

    async def ai_analysis_by_desc(
            self,
            desc: str = '',
            just_use_ai_analyze_by_keywords: bool = False,
            just_need_keywords_subreddits: bool = False,
            time_filter: Literal["all", "day", "hour", "month", "week", "year"] = 'day',
            is_ai_analyze: bool = False,
            keywords: Optional[List[str]] = None,
            subreddits: Optional[List[str]] = None,
            limit_count: int = 20,
            limit: int = None
    ) -> Dict[str, Any]:
        """使用AI对描述进行分析，并返回结果

        Args:
            desc: 描述文本
            just_use_ai_analyze_by_keywords: 直接使用提供的关键字进行AI分析帖子（跳过AI提取关键字阶段）
            just_need_keywords_subreddits: 是否只返回关键词和subreddits
            time_filter: 时间过滤器
            is_ai_analyze: 是否使用AI进行分析
            keywords: 关键词列表
            subreddits: subreddit列表
            limit_count:
            limit: 返回的帖子数量限制

        Returns:
            list[Dict[str, Any]]: 分析结果列表
        """
        res = self.app.invoke({
            "JUST_USE_AI_ANALYZE_BY_KEYWORDS": just_use_ai_analyze_by_keywords,
            "KEYWORDS": keywords if keywords is not None else [],
            "SUBREDDITS": subreddits,
            "JUST_NEED_KEYWORDS_SUBREDDITS": just_need_keywords_subreddits,
            "IS_AI_ANALYZE": is_ai_analyze,
            "TIME_FILTER": time_filter,
            "LIMIT": limit_count,
            "POSTS": [],
            "ORIGIN_POSTS": [],
            "user_query": desc})
        # info(f"ai分析结果：{res}")
        if just_need_keywords_subreddits is True:
            return {
                "analyze_posts": {
                    "r_data": [],
                    "nr_data": []
                },
                "keywords": res["KEYWORDS"],
                "subreddits": subreddits if subreddits is not None else ["all"]
            }
        if "ANALYZE_POSTS" in res and res["ANALYZE_POSTS"] and  "ORIGIN_POSTS" in res and res["ORIGIN_POSTS"]:
            info(f"ai分析结果1：{res["ANALYZE_POSTS"]}")
            info(f"ai分析结果2：{res["ORIGIN_POSTS"]}")
            map_data = {
                item["id"]: item
                for item in res["ORIGIN_POSTS"]
                if isinstance(item, dict) and "id" in item
            }

            r = {
                "r_data": [
                    dict(matched_data)
                    for item in res["ANALYZE_POSTS"]["r_data"]
                    if (matched_data := self._check_match(item, map_data)) is not None
                ],
                "nr_data": [
                    dict(matched_data)
                    for item in res["ANALYZE_POSTS"]["nr_data"]
                    if (matched_data := self._check_match(item, map_data)) is not None
                ]
            }


            # 处理 limit 限制
            if limit is not None:
                r["r_data"] = r["r_data"][:limit]
                r["nr_data"] = r["nr_data"][:limit]
            return {
                "analyze_posts": r,
                "keywords": res["KEYWORDS"],
                "subreddits": subreddits if subreddits is not None else ["all"]
            }
        else:
            return {
                "analyze_posts": {
                    "r_data": [],
                    "nr_data": []
                },
                "keywords": [],
                "subreddits": subreddits if subreddits is not None else ["all"]
            }

    async def get_trending_posts(self, limit: int = 5, time_filter: Optional[str] = None, subreddits: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """获取热门帖子
        
        Args:
            limit: 返回的帖子数量限制
            time_filter: 时间过滤器
            subreddits: 要搜索的subreddit列表
            
        Returns:
            List[Dict[str, Any]]: 热门帖子列表
        """
        try:
            info(f"获取热门帖子，限制: {limit}, 时间过滤器: {time_filter}, subreddits: {subreddits}", logger_config)
            posts = self.finder.find_trending_posts(subreddits=subreddits, limit=limit)
            return posts
        except Exception as e:
            error(f"获取热门帖子失败: {e}", logger_config)
            raise
    
    async def find_posts_by_keywords(self, 
                                    keywords: Optional[List[str]] = None, 
                                    subreddits: Optional[List[str]] = None, 
                                    limit: int = 20, 
                                    sort: str = 'relevance') -> List[Dict[str, Any]]:
        """根据关键词查找帖子
        
        Args:
            keywords: 关键词列表
            subreddits: 要搜索的subreddit列表
            limit: 返回的帖子数量限制
            sort: 排序方式
            
        Returns:
            List[Dict[str, Any]]: 包含关键词的帖子列表
        """
        try:
            if not keywords:
                # 如果没有提供关键词，使用默认空列表
                keywords = []
                info("未提供关键词，使用空列表", logger_config)
            
            info(f"根据关键词查找帖子，关键词：{keywords}, 限制: {limit}, 排序: {sort}", logger_config)
            posts = self.finder.find_posts_by_keywords(keywords=keywords, subreddits=subreddits, limit=limit, sort=sort)
            info(f"帖子列表获取成功: {posts}")
            return posts
        except Exception as e:
            error(f"根据关键词查找帖子失败: {e}", logger_config)
            raise
    
    async def analyze_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析帖子趋势
        
        Args:
            posts: 帖子列表
            
        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        try:
            info(f"分析帖子趋势，帖子数量: {len(posts)}", logger_config)
            trends = self.finder.analyze_trends(posts)
            return trends
        except Exception as e:
            error(f"分析帖子趋势失败: {e}", logger_config)
            raise

    async def analyze_trends_professional(self,posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """专业版分析帖子趋势

        Args:
            posts: 帖子列表

        Returns:
            Dict[str, Any]: 趋势分析结果
        """
        try:
            info(f"专业版分析帖子趋势，帖子数量: {len(posts)}", logger_config)
            trends = self.finder.analyze_trends_professional(posts)
            return trends
        except Exception as e:
            error(f"专业版分析帖子趋势失败: {e}", logger_config)
            raise
    

    async def get_post_content(self, post_id: str) -> Dict[str, Any]:
        """获取帖子内容
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 帖子内容
        """
        try:
            info(f"获取帖子内容，ID: {post_id}", logger_config)
            content = self.finder.get_post_content(post_id)
            return content
        except Exception as e:
            error(f"获取帖子内容失败: {e}", logger_config)
            raise
    
    async def get_post_comments(self, post_id: str, limit: int = 10,sort: str = 'best') -> List[Dict[str, Any]]:
        """获取帖子评论
        
        Args:
            post_id: 帖子ID
            limit: 返回的评论数量限制
            sort: 排序方式（可选），支持以下值：
                - 'best'（默认）：按热度排序
                - 'new': 按时间排序（最新）
                - 'top': 按得分排序（最高）
                - 'controversial': 按争议度排序
                - 'old': 按时间排序（最旧）
                - 'random': 随机排序
            
        Returns:
            List[Dict[str, Any]]: 评论列表
        """
        try:
            info(f"获取帖子评论，ID: {post_id}, 限制: {limit}", logger_config)
            comments = self.finder.get_post_comments(post_id, limit=limit,sort=sort)
            return comments
        except Exception as e:
            error(f"获取帖子评论失败: {e}", logger_config)
            raise
    
@lru_cache()
def get_reddit_service() -> RedditService:
    """获取Reddit服务实例，使用lru_cache缓存结果
    
    Returns:
        RedditService: Reddit服务实例
    """
    return RedditService()