# src/serve/routes/reddit.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from src.serve.dependencies.services import get_reddit_service_dependency
from src.serve.models.reddit import (
    RedditPost, TrendAnalysis, ContentInsight,
    TrendingPostsRequest, KeywordPostsRequest, AIAnalysisResultRequest, TrendAnalysisProfessional,
    AIExtractKeywordsRequest, AnalysisRequest
)
from src.serve.models.common import DataResponse, PaginatedResponse, ErrorResponse
from src.serve.services.reddit_service import RedditService
from src.utils.logging import create_logger, info, error
import json
from pydantic import parse_obj_as
from fastapi import Form, Body

# 配置日志
logger_config = create_logger("Reddit-API-Routes")

# 创建路由
router = APIRouter()


@router.post("/ai-extract-keywords",
             response_model=DataResponse[Dict[str, Any]],
             summary="AI提取关键词和子版块")
async def ai_extract_keywords(
        req: AIExtractKeywordsRequest,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """使用AI对描述进行分析，仅提取关键词和子版块"""
    try:
        info(f"AI提取关键词请求: desc={req.desc}", logger_config)
        # AI提取关键字
        data = await reddit_service.ai_analysis_by_desc(
            desc=req.desc,
            just_use_ai_analyze_by_keywords=False,
            just_need_keywords_subreddits=True,
            is_ai_analyze=False,
        )


        return DataResponse(data=data, message="成功提取关键词和子版块")
    except Exception as e:
        error(f"AI提取关键词失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail="AI提取失败，请稍候重试")


@router.post("/ai-analyze-posts-by-keywords",
             response_model=DataResponse[Dict[str, Any]],
             summary="根据关键词获取帖子并进行AI分析")
async def ai_analyze_posts(
        request: AIAnalysisResultRequest,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """
        根据提供的关键词和子版块进行AI分析
        keywords: Optional[str] = Form(None, title="关键词列表", description="逗号分隔的关键词列表"),
        subreddits: Optional[str] = Form(None, title="子版块列表", description="逗号分隔的subreddit列表"),
        time_filter: Optional[str] = Form("day", title="时间过滤器", description="时间过滤器（如'day','week'）"),
        limit_count: int = Form(20, title="帖子数量限制", description="返回的帖子数量限制"),
        limit: int = Form(10, title="帖子分页数量限制", description="最终返回的条目数，数量要小于limit_count"),
    """
    try:
        data = await reddit_service.ai_analysis_by_desc(
            keywords=request.keywords,
            subreddits=request.subreddits,
            time_filter=request.time_filter,
            is_ai_analyze=True,
            limit_count=request.limit_count,
            just_use_ai_analyze_by_keywords=True,
            limit=request.limit
        )

        info(
            f"AI分析帖子请求: keywords={request.keywords}, subreddits={request.subreddits}, limit={request.limit}, limit_count={request.limit_count}",
            logger_config)

        return DataResponse(data=data, message="完成分析")
    except Exception as e:
        error(f"AI分析帖子失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=f"AI分析帖子失败: {e}")


@router.post("/ai-analysis",
             response_model=DataResponse[Dict[str, Any]],
             summary="AI分析Reddit数据")
async def ai_analysis(
        request: AIAnalysisResultRequest,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """使用AI对描述进行分析，提取关键词、子版块并返回分析结果
    desc: str = Form(...,title="产品描述", description="产品描述内容"),
        just_use_ai_analyze_by_keywords: bool = Form(False,  title="是否直接使用关键词进行AI帖子分析（跳过AI提取关键字阶段）", description="跳过AI提取关键字阶段，使用提供的关键字搜索帖子并AI分析"),
        just_need_keywords_subreddits: bool = Form(False,  title="是否只返回关键词和子版块", description="调用AI提取用户描述中的关键词和生成相应有关联的子版块"),
        time_filter: Optional[str] = Form(None,  title="时间过滤器", description="时间过滤器（如'day','week'）"),
        is_ai_analyze: bool = Form(False,  title="是否使用AI分析", description="使用AI分析帖子内容与用户描述的相关性"),
        keywords: Optional[str] = Form(None,  title="关键词列表", description="指定关键词列表，逗号分隔，会与AI提取的关键字进行合并"),
        subreddits: Optional[str] = Form(None,  title="子版块列表", description="指定子版块列表，逗号分隔，会与AI生成的子版块进行合并"),
        limit_count: int  = Form(5, title="帖子数量限制", description="返回的帖子数量限制,注意：此数量与分页数量不同，这个数量会和关键字相关联，如关键字有5个时，获取帖子数量为5，则会获取5x5=25个帖子,如果使用了AI分析，返回的结果可能会小于此数量"),
        limit: int = Form(20, title="帖子分页数量限制", description="返回的帖子数量限制，这个限制为最终返回条目"),

    """
    try:
        info(f"AI分析请求: {request}", logger_config)

        data = await reddit_service.ai_analysis_by_desc(
            desc=request.desc,
            just_use_ai_analyze_by_keywords=request.just_use_ai_analyze_by_keywords,
            just_need_keywords_subreddits=request.just_need_keywords_subreddits,
            time_filter=request.time_filter,
            is_ai_analyze=request.is_ai_analyze,
            keywords=request.keywords,
            subreddits=request.subreddits,
            limit_count=request.limit_count,
            limit=request.limit
        )

        # 测试数据包装为列表以匹配响应模型
        return DataResponse(
            data=data,  # 修改为字典列表
            message=f"完成分析"
        )
    except Exception as e:
        error(f"AI分析失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=f"AI分析帖子失败: {e}")


@router.get("/posts", response_model=DataResponse[List[RedditPost]], summary="获取热门帖子")
async def get_trending_posts(
        limit: int = Query(5, ge=1, le=100, title="帖子数量限制", description="返回的帖子数量限制"),
        time_filter: Optional[str] = Query("day", title="时间过滤器", description="时间过滤器（如'day','week'）"),
        subreddits: Optional[str] = Query("all", title="子版块列表", description="逗号分隔的subreddit列表"),
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """获取热门帖子（支持GET请求和逗号分隔的subreddits参数）"""
    try:
        # 将逗号分隔的字符串转换为列表
        subreddit_list = subreddits.split(',') if subreddits else None
        info(f"获取热门帖子: subreddit_list={subreddit_list}")
        posts = await reddit_service.get_trending_posts(
            limit=limit,
            time_filter=time_filter,
            subreddits=subreddit_list
        )
        return DataResponse(data=posts, message=f"成功获取{len(posts)}个热门帖子")
    except Exception as e:
        error(f"获取热门帖子失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=DataResponse[List[RedditPost]], summary="根据关键词查找帖子")
async def find_posts_by_keywords(
        keywords: Optional[str] = Form(None, title="关键词列表", description="关键词列表，逗号分隔"),
        subreddits: Optional[str] = Form(None, title="子版块列表", description="要搜索的subreddit列表，逗号分隔"),
        limit: int = Form(20, ge=1, le=100, title="帖子数量限制", description="返回的帖子数量限制"),
        sort: str = Form("relevance", title="排序方式",
                         description="排序方式，可选值：relevance, hot, top, new, comments"),
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """根据关键词查找帖子
    
    根据指定的关键词和subreddit查找帖子，支持排序
    """
    try:
        info(f"根据关键词查找帖子: keywords={keywords}, subreddits={subreddits}, limit={limit}, sort={sort}")
        # 将逗号分隔的字符串转换为列表
        keywords_list = keywords.split(',') if keywords else None
        subreddit_list = subreddits.split(',') if subreddits else None

        # 验证排序方式
        allowed_sorts = ['relevance', 'hot', 'top', 'new', 'comments']
        if sort not in allowed_sorts:
            raise HTTPException(status_code=400, detail=f"排序方式必须是以下之一: {', '.join(allowed_sorts)}")

        posts = await reddit_service.find_posts_by_keywords(
            keywords=keywords_list,
            subreddits=subreddit_list,
            limit=limit,
            sort=sort
        )
        return DataResponse(data=posts, message=f"成功获取{len(posts)}个包含关键词的帖子")
    except Exception as e:
        error(f"根据关键词查找帖子失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DataResponse[TrendAnalysis], summary="分析关联的多个帖子趋势")
async def analyze_trends(
        req: AnalysisRequest,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """分析帖子趋势

    分析提供的帖子数据，提取趋势信息
    """
    try:
        # 解析JSON字符串为字典列表
        info(f"分析帖子趋势: posts_json={req.posts_json}")
        posts_data = json.loads(req.posts_json)
        posts = parse_obj_as(List[RedditPost], posts_data)
        posts_dict = [post.dict() for post in posts]
        trends = await reddit_service.analyze_trends(posts_dict)
        info(f"分析结果: {trends}", logger_config)
        return DataResponse(data=trends, message=f"成功分析{trends['total_posts']}个帖子的趋势")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="无效的JSON格式")
    except Exception as e:
        error(f"分析帖子趋势失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze_professional", response_model=DataResponse[TrendAnalysisProfessional],
             summary="更专业的分析关联的多个帖子趋势")
async def analyze_trends_professional(
        req: AnalysisRequest,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """专业版：分析帖子趋势

    分析提供的帖子数据，提取趋势信息
    """
    try:
        info(f"专业版：分析帖子趋势: posts_json={req.posts_json}")
        posts_data = json.loads(req.posts_json)
        posts = parse_obj_as(List[RedditPost], posts_data)
        posts_dict = [post.dict() for post in posts]
        trends = await reddit_service.analyze_trends_professional(posts_dict)
        info(f"专业版：分析结果: {trends}", logger_config)
        return DataResponse(data=trends, message=f"成功分析帖子的趋势")
    except Exception as e:
        error(f"专业版：分析帖子趋势失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/post/{post_id}", response_model=DataResponse[dict], summary="获取帖子内容")
async def get_post_content(
        post_id: str,
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """获取帖子内容
    
    根据帖子ID获取完整内容
    """
    try:
        content = await reddit_service.get_post_content(post_id)
        return DataResponse(data=content, message=f"成功获取帖子内容")
    except Exception as e:
        error(f"获取帖子内容失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/post/{post_id}/comments", response_model=DataResponse[List[dict]], summary="获取帖子评论")
async def get_post_comments(
        post_id: str,
        limit: Optional[int] = Query(10, ge=1, le=100, description="返回的评论数量限制"),
        sort: str = Query("best", description="""sort: 排序方式（可选），支持以下值：
                - 'best'（默认）：按热度排序
                - 'new': 按时间排序（最新）
                - 'top': 按得分排序（最高）
                - 'controversial': 按争议度排序
                - 'old': 按时间排序（最旧）
                - 'random': 随机排序"""),
        reddit_service: RedditService = Depends(get_reddit_service_dependency)
):
    """获取帖子评论
    
    根据帖子ID获取评论
    """
    try:
        info(f"获取帖子 '{post_id}' 的评论，最多获取 {limit} 条，排序方式: {sort}", logger_config)
        comments = await reddit_service.get_post_comments(post_id, limit=limit, sort=sort)
        return DataResponse(data=comments, message=f"成功获取{len(comments)}条评论")
    except Exception as e:
        error(f"获取帖子评论失败: {e}", logger_config)
        raise HTTPException(status_code=500, detail=str(e))
