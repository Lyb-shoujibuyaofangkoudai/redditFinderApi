
from src.config.env import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, API_KEY, REDDIT_API_TIMEOUT
from src.graph.builder import build_word_cloud_graph
from src.utils.logging import create_logger, info, debug, warning, error, critical, u_log
import time
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import math

import praw
from dotenv import load_dotenv

# 配置日志
logger_config = create_logger("Reddit-Finder")

class RedditFinder:
    """Reddit内容发现工具
    
    用于发现Reddit上的热门话题和讨论，帮助内容创作者和营销人员找到有价值的内容灵感。
    """
    
    def __init__(self, env_path: str = None):
        """初始化RedditFinder
        
        Args:
            env_path: .env文件路径，默认为None，会自动查找项目根目录下的.env文件
        """
        # 加载环境变量
        info(f"加载环境变量地址：{env_path}", logger_config)
        self.word_cloud_app = build_word_cloud_graph()
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()
            
        # 初始化Reddit API客户端
        self._init_reddit_client()
        
        info(f"RedditFinder初始化完成", logger_config)
    
    def _init_reddit_client(self):
        """初始化Reddit API客户端"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
            )
            info(f"Reddit API客户端初始化成功，只读模式: {self.reddit.read_only}", logger_config)
        except Exception as e:
            error(f"Reddit API客户端初始化失败: {e}", logger_config)
            raise
    
    def find_trending_posts(self, subreddits: List[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """查找热门帖子
        
        Args:
            subreddits: 要搜索的subreddit列表，默认为['all']
            limit: 返回的帖子数量限制

        Returns:
            热门帖子列表
        """
        trending_posts = []
        
        # 如果没有提供subreddits，使用默认值
        if not subreddits:
            subreddits = ['all']
            warning("subreddits 为空，使用默认值 'all'", logger_config)
        
        # 合并多个subreddit，用+连接
        subreddit_str = '+'.join(subreddits)
        info(f"正在获取subreddit '{subreddit_str}'的热门帖子...", logger_config)
        
        try:
            # 获取热门帖子
            submissions = self.reddit.subreddit(subreddit_str).hot(limit=limit)
            
            for submission in submissions:
                post = {
                    'id': submission.id,
                    'title': submission.title,
                    'author': str(submission.author),
                    'subreddit': submission.subreddit.display_name,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'permalink': f"https://www.reddit.com{submission.permalink}",
                    'is_self': submission.is_self,
                }
                info(f"Submission 属性: {vars(submission)}", logger_config)
                # 如果是文本帖子，添加内容
                if submission.is_self and hasattr(submission, 'selftext'):
                    post['selftext'] = submission.selftext
                
                trending_posts.append(post)
                # 避免API速率限制
                time.sleep(REDDIT_API_TIMEOUT)
                
            info(f"成功获取到{len(trending_posts)}个热门帖子", logger_config)
            info(f"热门帖子示例: {trending_posts[0]}", logger_config)
            return trending_posts
            
        except praw.exceptions.RedditAPIException as e:
            error(f"Reddit API异常: {e}", logger_config)
            raise
        except Exception as e:
            error(f"获取热门帖子时发生错误: {e}", logger_config)
            raise

    def find_posts_by_keywords(self, keywords: List[str], subreddits: List[str] = None, limit: int = 20, sort: str = 'relevance',time_filter: str = 'all') -> List[
        Dict[str, Any]]:
        """根据关键词查找帖子，并支持排序

        Args:
            keywords: 要搜索的关键词列表
            subreddits: 要搜索的subreddit列表，默认为['all']
            limit: 返回的帖子数量限制
            sort: 排序方式（可选），支持以下值：
                - 'relevance'（默认）：按相关性排序
                - 'hot': 按热度排序
                - 'top': 按得分排序（最高）
                - 'new': 按时间排序（最新）
                - 'comments': 按评论数量排序
            time_filter：
                - all
                - day
                - hour
                - month
                - week
                - year
        Returns:
            包含关键词的帖子列表
        """
        warning(f"开始搜索关键词: {keywords}，subreddits: {subreddits}，排序方式: {sort}，时间过滤: {time_filter}，数量: {limit}")
        if not keywords:
            warning("未提供关键词，无法进行关键词搜索", logger_config)
            return []

        # 如果没有提供subreddits，使用默认值
        if not subreddits:
            subreddits = ['all']
            warning("subreddits 为空，使用默认值 'all'", logger_config)
            
        subreddit_str = '+'.join(subreddits)

        keyword_posts = []

        try:
            for keyword in keywords:
                info(f"正在搜索关键词 '{keyword}' 在 '{subreddit_str}' 中的帖子，排序方式: {sort}", logger_config)

                # 使用Reddit搜索功能并设置排序方式
                search_results = self.reddit.subreddit(subreddit_str).search(
                    keyword,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
                info(f"搜索子模块 {subreddit_str}，处理中...")

                for submission in search_results:
                    info(f"处理帖子：{submission.title}")
                    post = {
                        'id': submission.id,
                        'title': submission.title,
                        'author': str(submission.author),
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'permalink': f"https://www.reddit.com{submission.permalink}",
                        'is_self': submission.is_self,
                        'keyword': keyword
                    }

                    # 如果是文本帖子，添加内容
                    if submission.is_self and hasattr(submission, 'selftext'):
                        post['selftext'] = submission.selftext

                    keyword_posts.append(post)

                time.sleep(REDDIT_API_TIMEOUT)

            info(f"成功获取到{len(keyword_posts)}个包含关键词的帖子", logger_config)
            return keyword_posts

        except Exception as e:
            error(f"关键词搜索时发生错误: {e}", logger_config)
            raise

    def analyze_trends(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析帖子趋势
        
        Args:
            posts: 帖子列表
            
        Returns:
            趋势分析结果
        """
        if not posts:
            warning("没有提供帖子数据，无法进行趋势分析", logger_config)
            return {}
            
        # 按subreddit分组统计
        subreddit_stats = {}
        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_stats:
                subreddit_stats[subreddit] = {
                    'count': 0,
                    'total_score': 0,
                    'total_comments': 0,
                    'avg_score': 0,
                    'avg_comments': 0
                }
            
            subreddit_stats[subreddit]['count'] += 1
            subreddit_stats[subreddit]['total_score'] += post['score']
            subreddit_stats[subreddit]['total_comments'] += post['num_comments']
        
        # 计算平均值
        for subreddit, stats in subreddit_stats.items():
            stats['avg_score'] = stats['total_score'] / stats['count']
            stats['avg_comments'] = stats['total_comments'] / stats['count']
        
        # 找出最活跃的subreddit
        most_active_subreddits = sorted(
            subreddit_stats.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )
        
        # 找出最受欢迎的帖子
        top_posts_by_score = sorted(posts, key=lambda x: x['score'], reverse=True)[:5]
        top_posts_by_comments = sorted(posts, key=lambda x: x['num_comments'], reverse=True)[:5]
        
        trends = {
            'total_posts': len(posts),
            'subreddit_stats': subreddit_stats,
            'most_active_subreddits': most_active_subreddits,
            'top_posts_by_score': top_posts_by_score,
            'top_posts_by_comments': top_posts_by_comments
        }
        
        info(f"趋势分析完成，分析了{len(posts)}个帖子", logger_config)
        return trends

    def _preprocess_posts_data(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """数据预处理和清洗

        Args:
            posts: 原始帖子数据

        Returns:
            清洗后的数据字典，包含原始数据和统计信息
        """
        if not posts:
            return {'posts': [], 'stats': {}}

        # 数据清洗
        cleaned_posts = []
        for post in posts:
            # 基础数据验证
            if post.get('score', 0) >= 0 and post.get('num_comments', 0) >= 0:
                # 添加计算字段
                post['engagement_ratio'] = post['num_comments'] / max(post['score'], 1)
                post['created_datetime'] = datetime.fromtimestamp(post['created_utc'])
                post['age_hours'] = (time.time() - post['created_utc']) / 3600

                # 计算病毒传播速度
                if post['age_hours'] > 0:
                    post['viral_velocity'] = post['score'] / post['age_hours']
                else:
                    post['viral_velocity'] = 0

                cleaned_posts.append(post)

        # 异常值检测（使用IQR方法）
        scores = [p['score'] for p in cleaned_posts]
        if len(scores) > 4:  # 至少需要4个数据点进行IQR计算
            q1 = statistics.quantiles(scores, n=4)[0]
            q3 = statistics.quantiles(scores, n=4)[2]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # 标记异常值但不移除
            for post in cleaned_posts:
                post['is_outlier'] = post['score'] < lower_bound or post['score'] > upper_bound
        else:
            for post in cleaned_posts:
                post['is_outlier'] = False

        return {
            'posts': cleaned_posts,
            'original_count': len(posts),
            'cleaned_count': len(cleaned_posts),
            'outlier_count': sum(1 for p in cleaned_posts if p['is_outlier'])
        }

    def _statistical_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """统计学基础分析

        Args:
            data: 预处理后的数据

        Returns:
            统计分析结果
        """
        posts = data['posts']
        if not posts:
            return {}

        scores = [p['score'] for p in posts]
        comments = [p['num_comments'] for p in posts]
        engagement_ratios = [p['engagement_ratio'] for p in posts]

        def calculate_stats(values):
            if not values:
                return {}
            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values),
                'q1': statistics.quantiles(values, n=4)[0] if len(values) > 3 else min(values),
                'q3': statistics.quantiles(values, n=4)[2] if len(values) > 3 else max(values)
            }

        # 计算相关性（简化版皮尔逊相关系数）
        def correlation(x, y):
            if len(x) != len(y) or len(x) < 2:
                return 0

            mean_x = statistics.mean(x)
            mean_y = statistics.mean(y)

            numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
            sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(len(x)))
            sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(len(y)))

            denominator = math.sqrt(sum_sq_x * sum_sq_y)
            return numerator / denominator if denominator != 0 else 0

        return {
            'score_stats': calculate_stats(scores),
            'comment_stats': calculate_stats(comments),
            'engagement_stats': calculate_stats(engagement_ratios),
            'correlations': {
                'score_comments': correlation(scores, comments),
                'score_engagement': correlation(scores, engagement_ratios)
            },
            'distribution_analysis': {
                'score_skewness': self._calculate_skewness(scores),
                'outlier_percentage': (data['outlier_count'] / data['cleaned_count']) * 100 if data[
                                                                                                   'cleaned_count'] > 0 else 0
            }
        }

    def _temporal_trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """时间序列趋势分析

        Args:
            data: 预处理后的数据

        Returns:
            时间趋势分析结果
        """
        posts = data['posts']
        if not posts:
            return {}

        # 按小时统计
        hourly_stats = {}
        daily_stats = {}

        for post in posts:
            dt = post['created_datetime']
            hour = dt.hour
            day = dt.strftime('%Y-%m-%d')

            # 小时统计
            if hour not in hourly_stats:
                hourly_stats[hour] = {'count': 0, 'total_score': 0, 'total_comments': 0}
            hourly_stats[hour]['count'] += 1
            hourly_stats[hour]['total_score'] += post['score']
            hourly_stats[hour]['total_comments'] += post['num_comments']

            # 日统计
            if day not in daily_stats:
                daily_stats[day] = {'count': 0, 'total_score': 0, 'total_comments': 0}
            daily_stats[day]['count'] += 1
            daily_stats[day]['total_score'] += post['score']
            daily_stats[day]['total_comments'] += post['num_comments']

        # 计算平均值
        for hour_data in hourly_stats.values():
            hour_data['avg_score'] = hour_data['total_score'] / hour_data['count']
            hour_data['avg_comments'] = hour_data['total_comments'] / hour_data['count']

        for day_data in daily_stats.values():
            day_data['avg_score'] = day_data['total_score'] / day_data['count']
            day_data['avg_comments'] = day_data['total_comments'] / day_data['count']

        # 找出活跃时段
        peak_hour = max(hourly_stats.items(), key=lambda x: x[1]['count'])
        peak_day = max(daily_stats.items(), key=lambda x: x[1]['count']) if daily_stats else None

        return {
            'hourly_patterns': hourly_stats,
            'daily_patterns': daily_stats,
            'peak_activity': {
                'hour': peak_hour[0],
                'hour_posts': peak_hour[1]['count'],
                'day': peak_day[0] if peak_day else None,
                'day_posts': peak_day[1]['count'] if peak_day else 0
            },
            'time_span': {
                'earliest': min(p['created_datetime'] for p in posts).isoformat(),
                'latest': max(p['created_datetime'] for p in posts).isoformat()
            }
        }

    def _engagement_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """活跃度综合分析

        Args:
            data: 预处理后的数据

        Returns:
            活跃度分析结果
        """
        posts = data['posts']
        if not posts:
            return {}

        # 按subreddit分组分析
        subreddit_engagement = {}

        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_engagement:
                subreddit_engagement[subreddit] = {
                    'posts': [],
                    'total_score': 0,
                    'total_comments': 0,
                    'total_engagement_ratio': 0,
                    'count': 0
                }

            subreddit_engagement[subreddit]['posts'].append(post)
            subreddit_engagement[subreddit]['total_score'] += post['score']
            subreddit_engagement[subreddit]['total_comments'] += post['num_comments']
            subreddit_engagement[subreddit]['total_engagement_ratio'] += post['engagement_ratio']
            subreddit_engagement[subreddit]['count'] += 1

        # 计算综合评分
        for subreddit, data in subreddit_engagement.items():
            count = data['count']

            # 基础指标
            avg_score = data['total_score'] / count
            avg_comments = data['total_comments'] / count
            avg_engagement = data['total_engagement_ratio'] / count

            # 一致性评分（标准差的倒数）
            scores = [p['score'] for p in data['posts']]
            consistency = 1 / (statistics.stdev(scores) + 1) if len(scores) > 1 else 1

            # 综合活跃度评分 (0-100)
            engagement_score = min(100, (
                    avg_score * 0.3 +
                    avg_comments * 0.3 +
                    avg_engagement * 20 * 0.2 +
                    consistency * 10 * 0.1 +
                    math.log(count + 1) * 5 * 0.1
            ))

            data['metrics'] = {
                'avg_score': avg_score,
                'avg_comments': avg_comments,
                'avg_engagement_ratio': avg_engagement,
                'consistency_score': consistency,
                'engagement_score': engagement_score
            }

        # 排序subreddit
        ranked_subreddits = sorted(
            subreddit_engagement.items(),
            key=lambda x: x[1]['metrics']['engagement_score'],
            reverse=True
        )

        return {
            'subreddit_rankings': [(name, data['metrics']) for name, data in ranked_subreddits],
            'top_engaging_subreddit': ranked_subreddits[0][0] if ranked_subreddits else None,
            'overall_engagement_score': statistics.mean([
                data['metrics']['engagement_score']
                for _, data in subreddit_engagement.items()
            ])
        }

    def _viral_potential_analysis(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """病毒传播潜力分析

        Args:
            posts: 帖子列表

        Returns:
            病毒传播分析结果
        """
        if not posts:
            return {}

        viral_indicators = []

        for post in posts:
            # 计算病毒指标
            age_hours = max(post.get('age_hours', 1), 0.1)  # 避免除零
            score = post.get('score', 0)
            comments = post.get('num_comments', 0)

            # 传播速度 (分数/小时)
            viral_velocity = post.get('viral_velocity', score / age_hours)

            # 互动强度
            interaction_intensity = comments / max(score, 1)

            # 早期动量 (前6小时的表现预测)
            if age_hours <= 6:
                early_momentum = viral_velocity * 2  # 早期帖子加权
            else:
                early_momentum = viral_velocity

            # 综合病毒指数 (0-100)
            viral_score = min(100, (
                    viral_velocity * 0.4 +
                    interaction_intensity * 20 * 0.3 +
                    early_momentum * 0.2 +
                    min(score / 100, 10) * 0.1
            ))

            viral_indicators.append({
                'post_id': post['id'],
                'title': post['title'][:100] + '...' if len(post['title']) > 100 else post['title'],
                'subreddit': post['subreddit'],
                'viral_score': round(viral_score, 2),
                'viral_velocity': round(viral_velocity, 2),
                'interaction_intensity': round(interaction_intensity, 3),
                'early_momentum': round(early_momentum, 2),
                'age_hours': round(age_hours, 1),
                'current_score': score,
                'current_comments': comments
            })

        # 排序并分类
        viral_indicators.sort(key=lambda x: x['viral_score'], reverse=True)

        # 分类病毒潜力
        high_potential = [p for p in viral_indicators if p['viral_score'] >= 70]
        medium_potential = [p for p in viral_indicators if 40 <= p['viral_score'] < 70]
        low_potential = [p for p in viral_indicators if p['viral_score'] < 40]

        # 计算整体统计
        viral_scores = [p['viral_score'] for p in viral_indicators]
        avg_viral_score = statistics.mean(viral_scores) if viral_scores else 0

        # 识别超级病毒帖子（前10%或病毒指数超过80）
        super_viral_threshold = max(80, statistics.quantiles(viral_scores, n=10)[8] if len(viral_scores) >= 10 else 80)
        super_viral_posts = [p for p in viral_indicators if p['viral_score'] >= super_viral_threshold]

        return {
            'total_analyzed': len(viral_indicators),
            'average_viral_score': round(avg_viral_score, 2),
            'distribution': {
                'high_potential': {
                    'count': len(high_potential),
                    'percentage': round(len(high_potential) / len(viral_indicators) * 100,
                                        1) if viral_indicators else 0,
                    'posts': high_potential[:5]  # 只返回前5个
                },
                'medium_potential': {
                    'count': len(medium_potential),
                    'percentage': round(len(medium_potential) / len(viral_indicators) * 100,
                                        1) if viral_indicators else 0,
                    'posts': medium_potential[:3]  # 只返回前3个
                },
                'low_potential': {
                    'count': len(low_potential),
                    'percentage': round(len(low_potential) / len(viral_indicators) * 100, 1) if viral_indicators else 0
                }
            },
            'super_viral_posts': super_viral_posts,
            'top_viral_posts': viral_indicators[:10],  # 前10个最具病毒潜力的帖子
            'viral_trends': {
                'fastest_growing': max(viral_indicators,
                                       key=lambda x: x['viral_velocity']) if viral_indicators else None,
                'most_engaging': max(viral_indicators,
                                     key=lambda x: x['interaction_intensity']) if viral_indicators else None,
                'early_stage_leaders': [p for p in viral_indicators if p['age_hours'] <= 2 and p['viral_score'] >= 60]
            }
        }

    def _calculate_skewness(self, values: List[float]) -> float:
        """计算偏度（偏态系数）

        Args:
            values: 数值列表

        Returns:
            偏度值
        """
        if len(values) < 3:
            return 0

        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)

        if std_val == 0:
            return 0

        # 计算三阶中心矩
        third_moment = sum((x - mean_val) ** 3 for x in values) / len(values)
        skewness = third_moment / (std_val ** 3)

        return round(skewness, 3)

    def _content_sentiment_analysis(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """内容和情感趋势分析

        Args:
            posts: 帖子列表

        Returns:
            内容分析结果
        """
        if not posts:
            return {}

        # 简化的情感分析（基于关键词）
        positive_keywords = ['good', 'great', 'amazing', 'awesome', 'excellent', 'love', 'best', 'fantastic']
        negative_keywords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disgusting']

        sentiment_scores = []
        topic_keywords = {}

        for post in posts:
            title = post['title'].lower()
            text = post.get('selftext', '').lower() if post.get('selftext') is not None else ''
            combined_text = f"{title} {text}"

            # 简单的情感评分
            positive_count = sum(1 for word in positive_keywords if word in combined_text)
            negative_count = sum(1 for word in negative_keywords if word in combined_text)
            sentiment_score = positive_count - negative_count
            sentiment_scores.append(sentiment_score)

            # 提取关键词（简化版）
            words = combined_text.split()
            for word in words:
                if len(word) > 4 and word.isalpha():  # 过滤短词和非字母
                    topic_keywords[word] = topic_keywords.get(word, 0) + 1

        # 计算平均情感
        avg_sentiment = statistics.mean(sentiment_scores) if sentiment_scores else 0

        # 确定情感趋势
        if avg_sentiment > 0.5:
            sentiment_trend = 'positive'
        elif avg_sentiment < -0.5:
            sentiment_trend = 'negative'
        else:
            sentiment_trend = 'neutral'

        # 热门话题
        trending_topics = sorted(topic_keywords.items(), key=lambda x: x[1], reverse=True)[:15]

        return {
            'average_sentiment': round(avg_sentiment, 2),
            'sentiment_trend': sentiment_trend,
            'sentiment_distribution': {
                'positive': len([s for s in sentiment_scores if s > 0]),
                'neutral': len([s for s in sentiment_scores if s == 0]),
                'negative': len([s for s in sentiment_scores if s < 0])
            },
            'trending_topics': [{'keyword': word, 'frequency': count} for word, count in trending_topics],
            'content_themes': self._extract_content_themes(posts)
        }

    def _extract_content_themes(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取内容主题

        Args:
            posts: 帖子列表

        Returns:
            主题列表
        """
        # 简化的主题提取
        subreddit_themes = {}

        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_themes:
                subreddit_themes[subreddit] = {
                    'post_count': 0,
                    'avg_score': 0,
                    'total_score': 0,
                    'sample_titles': []
                }

            subreddit_themes[subreddit]['post_count'] += 1
            subreddit_themes[subreddit]['total_score'] += post['score']

            if len(subreddit_themes[subreddit]['sample_titles']) < 3:
                subreddit_themes[subreddit]['sample_titles'].append(post['title'])

        # 计算平均分数
        for theme_data in subreddit_themes.values():
            theme_data['avg_score'] = theme_data['total_score'] / theme_data['post_count']

        # 转换为列表格式
        themes = []
        for subreddit, data in subreddit_themes.items():
            themes.append({
                'theme': subreddit,
                'post_count': data['post_count'],
                'avg_score': round(data['avg_score'], 1),
                'sample_titles': data['sample_titles']
            })

        return sorted(themes, key=lambda x: x['post_count'], reverse=True)

    def _generate_predictions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """生成预测和建议

        Args:
            data: 预处理后的数据

        Returns:
            预测结果
        """
        posts = data['posts']
        if not posts:
            return {}

        # 基于历史数据的简单预测
        scores = [p['score'] for p in posts]
        comments = [p['num_comments'] for p in posts]
        viral_velocities = [p.get('viral_velocity', 0) for p in posts]
        engagement_ratios = [p.get('engagement_ratio', 0) for p in posts]

        # 计算趋势方向
        def calculate_trend(values):
            if len(values) < 2:
                return 'stable'
            recent_avg = statistics.mean(values[-len(values) // 3:]) if len(values) >= 3 else values[-1]
            early_avg = statistics.mean(values[:len(values) // 3]) if len(values) >= 3 else values[0]

            if recent_avg > early_avg * 1.1:
                return 'increasing'
            elif recent_avg < early_avg * 0.9:
                return 'decreasing'
            else:
                return 'stable'

        # 预测未来表现
        avg_score = statistics.mean(scores)
        avg_comments = statistics.mean(comments)
        avg_viral_velocity = statistics.mean(viral_velocities)

        # 基于当前趋势预测下一周期
        score_trend = calculate_trend(scores)
        multiplier = {'increasing': 1.15, 'stable': 1.0, 'decreasing': 0.85}[score_trend]

        return {
            'score_predictions': {
                'next_period_avg': round(avg_score * multiplier, 1),
                'trend': score_trend,
                'confidence': 'medium' if len(posts) >= 10 else 'low'
            },
            'engagement_forecast': {
                'expected_comments': round(avg_comments * multiplier, 1),
                'viral_potential': 'high' if avg_viral_velocity > 10 else 'moderate' if avg_viral_velocity > 5 else 'low',
                'engagement_trend': calculate_trend(engagement_ratios)
            },
            'peak_timing_prediction': self._predict_peak_timing(posts),
            'growth_forecast': {
                'expected_growth_rate': round((multiplier - 1) * 100, 1),
                'risk_level': 'high' if score_trend == 'decreasing' else 'medium' if score_trend == 'stable' else 'low'
            }
        }

    def _generate_ai_word_cloud(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.word_cloud_app.invoke({
            "WORD_SEG_RESULT": {},
            "data": data
        })
        if "WORD_SEG_RESULT" in res and res["WORD_SEG_RESULT"]:
            return res["WORD_SEG_RESULT"]

        else:
            return {}
    def _predict_peak_timing(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """预测最佳发布时机

        Args:
            posts: 帖子列表

        Returns:
            时机预测结果
        """
        if not posts:
            return {}

        # 按小时统计表现
        hourly_performance = {}
        for post in posts:
            hour = post['created_datetime'].hour
            if hour not in hourly_performance:
                hourly_performance[hour] = {'scores': [], 'comments': []}
            hourly_performance[hour]['scores'].append(post['score'])
            hourly_performance[hour]['comments'].append(post['num_comments'])

        # 计算每小时的平均表现
        hour_rankings = []
        for hour, data in hourly_performance.items():
            avg_score = statistics.mean(data['scores'])
            avg_comments = statistics.mean(data['comments'])
            combined_score = avg_score * 0.6 + avg_comments * 0.4
            hour_rankings.append((hour, combined_score))

        hour_rankings.sort(key=lambda x: x[1], reverse=True)

        return {
            'best_hours': [h[0] for h in hour_rankings[:3]],
            'worst_hours': [h[0] for h in hour_rankings[-3:]],
            'optimal_time_range': f"{hour_rankings[0][0]:02d}:00 - {(hour_rankings[0][0] + 2) % 24:02d}:00"
        }

    def _calculate_data_quality(self, data: Dict[str, Any]) -> float:
        """计算数据质量评分

        Args:
            data: 预处理后的数据

        Returns:
            质量评分 (0-100)
        """
        if not data or not data.get('posts'):
            return 0

        posts = data['posts']
        total_posts = data['original_count']
        cleaned_posts = data['cleaned_count']
        outliers = data['outlier_count']

        # 1. 数据完整性评分 (40分)
        completeness_score = (cleaned_posts / total_posts) * 40 if total_posts > 0 else 0

        # 2. 数据质量评分 (30分)
        # 检查必要字段的完整性
        required_fields = ['id', 'title', 'score', 'num_comments', 'created_utc', 'subreddit']
        field_completeness = 0
        for post in posts[:min(10, len(posts))]:  # 检查前10个帖子作为样本
            complete_fields = sum(1 for field in required_fields if field in post and post[field] is not None)
            field_completeness += complete_fields / len(required_fields)

        field_quality_score = (field_completeness / min(10, len(posts))) * 30 if posts else 0

        # 3. 异常值处理评分 (15分) - 异常值越少质量越高
        outlier_penalty = min((outliers / cleaned_posts) * 15, 15) if cleaned_posts > 0 else 0
        outlier_score = 15 - outlier_penalty

        # 4. 数据多样性评分 (15分)
        subreddits = set(p['subreddit'] for p in posts if 'subreddit' in p)
        authors = set(p.get('author', 'unknown') for p in posts)

        diversity_score = min(len(subreddits) * 2, 10) + min(len(authors) * 0.5, 5)

        # 综合质量评分
        total_score = completeness_score + field_quality_score + outlier_score + diversity_score

        return round(min(100, max(0, total_score)), 1)

    def _generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """生成可执行洞察

        Args:
            data: 分析数据

        Returns:
            洞察列表
        """
        posts = data['posts']
        insights = []

        if not posts:
            return ["数据不足，无法生成有效洞察"]

        # 基础统计分析
        scores = [p['score'] for p in posts]
        comments = [p['num_comments'] for p in posts]
        engagement_ratios = [p.get('engagement_ratio', 0) for p in posts]

        avg_score = statistics.mean(scores)
        avg_comments = statistics.mean(comments)
        avg_engagement = statistics.mean(engagement_ratios)

        # 1. 内容表现洞察
        if avg_score < 50:
            insights.append("内容得分偏低，建议优化内容质量和标题吸引力")
        elif avg_score > 500:
            insights.append("内容表现优秀，当前策略值得保持和复制")

        # 2. 互动性洞察
        if avg_comments < 10:
            insights.append("用户互动不活跃，建议增加问题引导和争议性话题")
        elif avg_engagement > 0.5:
            insights.append("用户互动度很高，内容引发了强烈讨论")

        # 3. 时间策略洞察
        hourly_stats = {}
        for post in posts:
            hour = post['created_datetime'].hour
            hourly_stats[hour] = hourly_stats.get(hour, []) + [post['score']]

        if hourly_stats:
            best_hours = sorted(hourly_stats.items(),
                                key=lambda x: statistics.mean(x[1]), reverse=True)[:3]
            best_hour_list = [f"{h:02d}:00" for h, _ in best_hours]
            insights.append(f"最佳发布时间为: {', '.join(best_hour_list)}")

        # 4. Subreddit表现洞察
        subreddit_performance = {}
        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_performance:
                subreddit_performance[subreddit] = []
            subreddit_performance[subreddit].append(post['score'])

        if len(subreddit_performance) > 1:
            best_subreddit = max(subreddit_performance.items(),
                                 key=lambda x: statistics.mean(x[1]))
            insights.append(f"在 r/{best_subreddit[0]} 中表现最佳，平均得分 {statistics.mean(best_subreddit[1]):.1f}")

        # 5. 内容策略洞察
        high_performers = [p for p in posts if p['score'] > avg_score * 1.5]
        if high_performers:
            common_patterns = self._analyze_content_patterns(high_performers)
            if common_patterns:
                insights.append(f"高表现内容特征: {common_patterns}")

        # 6. 风险提醒
        outliers = [p for p in posts if p.get('is_outlier', False)]
        if len(outliers) > len(posts) * 0.2:
            insights.append("数据中异常值较多，建议检查内容质量一致性")

        return insights[:10]  # 最多返回10条洞察

    def _analyze_content_patterns(self, posts: List[Dict[str, Any]]) -> str:
        """分析内容模式

        Args:
            posts: 高表现帖子列表

        Returns:
            内容模式描述
        """
        if not posts:
            return ""

        # 分析标题长度
        title_lengths = [len(post['title']) for post in posts]
        avg_length = statistics.mean(title_lengths)

        # 分析常见词汇
        all_titles = ' '.join([post['title'].lower() for post in posts])
        words = [word for word in all_titles.split() if len(word) > 3]

        if len(words) > 0:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            common_word_list = [word for word, _ in common_words]

            return f"标题长度约{avg_length:.0f}字符，常用词汇: {', '.join(common_word_list)}"

        return f"标题长度约{avg_length:.0f}字符"

    def _basic_fallback_analysis(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """基础回退分析 - 当专业分析失败时使用

        Args:
            posts: 帖子列表

        Returns:
            基础分析结果
        """
        if not posts:
            return {'message': '无帖子数据可供分析'}

        try:
            # 使用现有的基础分析方法
            basic_trends = self.analyze_trends(posts)

            # 添加一些简单的额外统计
            scores = [p.get('score', 0) for p in posts]
            comments = [p.get('num_comments', 0) for p in posts]

            # 计算基础统计
            total_score = sum(scores)
            total_comments = sum(comments)
            avg_score = statistics.mean(scores) if scores else 0
            avg_comments = statistics.mean(comments) if comments else 0

            # 识别热门帖子
            hot_threshold = avg_score * 2 if avg_score > 0 else 100
            hot_posts = [p for p in posts if p.get('score', 0) > hot_threshold]

            # 时间分布简析
            if posts and 'created_utc' in posts[0]:
                timestamps = [p['created_utc'] for p in posts if 'created_utc' in p]
                if timestamps:
                    time_span = max(timestamps) - min(timestamps)
                    hours_span = time_span / 3600
                else:
                    hours_span = 0
            else:
                hours_span = 0

            # 简单的内容分析
            title_lengths = [len(p.get('title', '')) for p in posts]
            avg_title_length = statistics.mean(title_lengths) if title_lengths else 0

            # 作者多样性分析
            authors = set(p.get('author', 'unknown') for p in posts)
            author_diversity = len(authors)

            # subreddit分布
            subreddits = set(p.get('subreddit', 'unknown') for p in posts)
            subreddit_diversity = len(subreddits)

            fallback_analysis = {
                **basic_trends,  # 包含基础趋势分析
                'fallback_metrics': {
                    'analysis_type': 'basic_fallback',
                    'total_engagement': total_score + total_comments,
                    'average_score': round(avg_score, 1),
                    'average_comments': round(avg_comments, 1),
                    'hot_posts_count': len(hot_posts),
                    'hot_posts_percentage': round(len(hot_posts) / len(posts) * 100, 1) if posts else 0,
                    'time_span_hours': round(hours_span, 1),
                    'posting_frequency': round(len(posts) / max(hours_span, 1), 2) if hours_span > 0 else 0,
                    'content_metrics': {
                        'avg_title_length': round(avg_title_length, 1),
                        'author_diversity': author_diversity,
                        'subreddit_diversity': subreddit_diversity,
                        'engagement_rate': round((total_comments / max(total_score, 1)), 3)
                    }
                },
                'simple_recommendations': self._generate_simple_recommendations(posts, avg_score, avg_comments),
                'data_summary': {
                    'total_posts_analyzed': len(posts),
                    'score_range': f"{min(scores)} - {max(scores)}" if scores else "N/A",
                    'comments_range': f"{min(comments)} - {max(comments)}" if comments else "N/A",
                    'most_active_subreddit': max(basic_trends.get('subreddit_stats', {}).items(),
                                                 key=lambda x: x[1]['count'])[0] if basic_trends.get(
                        'subreddit_stats') else "N/A"
                }
            }

            info(f"基础回退分析完成，分析了{len(posts)}个帖子", logger_config)
            return fallback_analysis

        except Exception as e:
            error(f"基础回退分析也失败了: {e}", logger_config)
            return {
                'error': f'所有分析方法都失败了: {str(e)}',
                'basic_stats': {
                    'total_posts': len(posts),
                    'analysis_attempted': 'basic_fallback',
                    'status': 'failed'
                }
            }

    def _generate_simple_recommendations(self, posts: List[Dict[str, Any]], avg_score: float, avg_comments: float) -> \
    List[str]:
        """生成简单的建议

        Args:
            posts: 帖子列表
            avg_score: 平均得分
            avg_comments: 平均评论数

        Returns:
            简单建议列表
        """
        recommendations = []

        if not posts:
            return ["没有足够的数据来生成建议"]

        # 基于平均分数的建议
        if avg_score < 10:
            recommendations.append("内容得分较低，建议提高内容质量")
        elif avg_score > 100:
            recommendations.append("内容表现良好，保持当前策略")

        # 基于评论数的建议
        if avg_comments < 5:
            recommendations.append("互动较少，考虑增加引导性问题")
        elif avg_comments > 50:
            recommendations.append("互动很活跃，内容引起了热烈讨论")

        # 基于发布时间的简单建议
        if len(posts) > 1:
            timestamps = [p.get('created_utc', 0) for p in posts if 'created_utc' in p]
            if timestamps:
                # 简单的时间分析
                hours = [datetime.fromtimestamp(ts).hour for ts in timestamps]
                most_common_hour = max(set(hours), key=hours.count)
                recommendations.append(f"您经常在{most_common_hour}点发布内容")

        # 基于subreddit多样性的建议
        subreddits = set(p.get('subreddit', '') for p in posts)
        if len(subreddits) == 1:
            recommendations.append("考虑在更多不同的subreddit中发布内容")
        elif len(subreddits) > 5:
            recommendations.append("您在多个subreddit中都有发布，保持多样性")

        return recommendations[:5]  # 最多返回5条建议

    def analyze_trends_professional(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """专业级Reddit趋势分析

        Returns:
            包含多维度分析结果的详细趋势报告
        """
        if not posts:
            return {'error': 'No posts provided for analysis'}

        try:
            # 数据预处理
            df = self._preprocess_posts_data(posts)

            # 1. 统计学基础分析
            statistical_analysis = self._statistical_analysis(df)

            # 2. 时间序列趋势
            temporal_trends = self._temporal_trend_analysis(df)

            # 3. 活跃度综合评分
            engagement_analysis = self._engagement_analysis(df)

            # 4. 病毒传播潜力
            viral_analysis = self._viral_potential_analysis(posts)

            # 5. 内容和情感趋势
            content_trends = self._content_sentiment_analysis(posts)

            # 6. 预测和建议
            predictions = self._generate_predictions(df)

            # 7. AI分词分析 词云图
            words_cloud = self._generate_ai_word_cloud({
                "posts": list(map(lambda item: {
                    "title": item.get("title"),
                    "selftext": item.get("selftext")
                },posts))
            })

            return {
                'analysis_metadata': {
                    'total_posts': len(posts),
                    'analysis_timestamp': time.time(),
                    'data_quality_score': self._calculate_data_quality(df)
                },
                'statistical_summary': statistical_analysis,
                'temporal_trends': temporal_trends,
                'engagement_metrics': engagement_analysis,
                'viral_potential': viral_analysis,
                'content_insights': content_trends,
                'predictions': predictions,
                'actionable_insights': self._generate_insights(df),
                'words_cloud': words_cloud
            }

        except Exception as e:
            error(f"Professional trend analysis failed: {e}", logger_config)
            return {'error': str(e), 'fallback_analysis': self._basic_fallback_analysis(posts)}


    
    def monitor_subreddit_activity(self, subreddit: str, interval: int = 3600, duration: int = 86400) -> List[Dict[str, Any]]:
        """监控特定subreddit的活动
        
        Args:
            subreddit: 要监控的subreddit名称
            interval: 检查间隔（秒），默认为1小时
            duration: 监控持续时间（秒），默认为24小时
            
        Returns:
            监控期间的帖子列表
        """
        info(f"开始监控subreddit '{subreddit}'，间隔{interval}秒，持续{duration}秒", logger_config)
        
        start_time = time.time()
        end_time = start_time + duration
        all_posts = []
        seen_ids = set()
        
        try:
            while time.time() < end_time:
                # 获取最新帖子
                new_posts = []
                submissions = self.reddit.subreddit(subreddit).new(limit=20)
                
                for submission in submissions:
                    if submission.id in seen_ids:
                        continue
                        
                    post = {
                        'id': submission.id,
                        'title': submission.title,
                        'author': str(submission.author),
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'upvote_ratio': submission.upvote_ratio,
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'permalink': f"https://www.reddit.com{submission.permalink}",
                        'is_self': submission.is_self,
                        'timestamp': time.time()
                    }
                    
                    # 如果是文本帖子，添加内容
                    if submission.is_self and hasattr(submission, 'selftext'):
                        post['selftext'] = submission.selftext
                    
                    new_posts.append(post)
                    seen_ids.add(submission.id)
                    # 避免API速率限制
                    time.sleep(REDDIT_API_TIMEOUT)
                
                if new_posts:
                    info(f"发现{len(new_posts)}个新帖子", logger_config)
                    all_posts.extend(new_posts)
                
                # 等待下一个检查间隔
                elapsed = time.time() - start_time
                remaining = end_time - time.time()
                
                if remaining <= 0:
                    break
                    
                sleep_time = min(interval, remaining)
                info(f"已监控{elapsed:.1f}秒，休眠{sleep_time:.1f}秒后继续", logger_config)
                time.sleep(sleep_time)
            
            info(f"监控完成，共收集到{len(all_posts)}个帖子", logger_config)
            return all_posts
            
        except KeyboardInterrupt:
            info("监控被用户中断", logger_config)
            return all_posts
        except Exception as e:
            error(f"监控过程中发生错误: {e}", logger_config)
            return all_posts

    def get_post_comments(self, post_id: str, limit: int = 20, sort: str = 'best') -> List[Dict[str, Any]]:
        """获取指定帖子的所有评论，并支持排序

        Args:
            post_id: 帖子 ID
            limit: 返回的评论数量限制
            sort: 排序方式（可选），支持以下值：
                - 'best'（默认）：按热度排序
                - 'new': 按时间排序（最新）
                - 'top': 按得分排序（最高）
                - 'controversial': 按争议度排序
                - 'old': 按时间排序（最旧）
                - 'random': 随机排序

        Returns:
            评论列表
        """
        info(f"正在获取帖子 '{post_id}' 的评论，获取 {limit} 条，排序方式: {sort}", logger_config)

        try:
            # 获取帖子对象并设置评论排序方式
            submission = self.reddit.submission(id=post_id)
            submission.comment_sort = sort  # 设置排序方式

            # 预加载所有评论
            submission.comments.replace_more(limit=limit)

            comments = []
            for comment in submission.comments.list():
                comment_data = {
                    'id': comment.id,
                    'author': str(comment.author),
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'permalink': f"https://www.reddit.com{comment.permalink}",
                    'post_id': post_id,
                }
                comments.append(comment_data)

            info(f"成功获取到 {len(comments)} 条评论", logger_config)
            return comments

        except praw.exceptions.RedditAPIException as e:
            error(f"Reddit API 异常: {e}", logger_config)
            raise
        except Exception as e:
            error(f"获取评论时发生错误: {e}", logger_config)
            raise

    def get_post_content(self, post_id: str) -> Dict[str, Any]:
        """获取指定帖子的完整内容

        Args:
            post_id: 帖子 ID

        Returns:
            包含帖子内容的字典
        """
        info(f"正在获取帖子 '{post_id}' 的内容", logger_config)

        try:
            # 获取帖子对象
            submission = self.reddit.submission(id=post_id)

            # 构造返回数据
            post_data = {
                'id': submission.id,
                'title': submission.title,
                'author': str(submission.author),
                'subreddit': submission.subreddit.display_name,
                'score': submission.score,
                'upvote_ratio': submission.upvote_ratio,
                'num_comments': submission.num_comments,
                'created_utc': submission.created_utc,
                'url': submission.url,
                'permalink': f"https://www.reddit.com{submission.permalink}",
                'is_self': submission.is_self,
                'over_18': submission.over_18,
                'stickied': submission.stickied,
                'locked': submission.locked,
                'spoiler': submission.spoiler,
                'gilded': submission.gilded,
                'view_count': getattr(submission, 'view_count', None),  # 可能不存在
            }

            # 如果是自述帖，添加正文内容
            if submission.is_self and hasattr(submission, 'selftext'):
                post_data['selftext'] = submission.selftext

            info(f"成功获取到帖子内容: {post_data['title']}", logger_config)
            return post_data

        except praw.exceptions.RedditAPIException as e:
            error(f"Reddit API 异常: {e}", logger_config)
            raise
        except Exception as e:
            error(f"获取帖子内容时发生错误: {e}", logger_config)
            raise
