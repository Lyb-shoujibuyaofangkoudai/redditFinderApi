import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

from src.utils.logging import create_logger, info, debug, warning, error, critical, u_log

# 配置日志
logger_config = create_logger("Reddit-Visualizer")

class RedditVisualizer:
    """Reddit数据可视化工具
    
    用于将Reddit Finder获取的数据以图表形式展示，支持多种可视化方式。
    """
    
    def __init__(self, output_dir: str = "./charts"):
        """初始化可视化工具
        
        Args:
            output_dir: 图表输出目录，默认为./charts
        """
        self.output_dir = output_dir
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        info(f"可视化工具初始化完成，图表将保存到: {output_dir}", logger_config)
    
    def plot_subreddit_distribution(self, posts: List[Dict[str, Any]], title: str = "Subreddit分布", 
                                   save: bool = True, filename: str = None) -> None:
        """绘制subreddit分布饼图
        
        Args:
            posts: 帖子列表
            title: 图表标题
            save: 是否保存图表
            filename: 保存的文件名，默认为subreddit_distribution_{timestamp}.png
        """
        if not posts:
            warning("没有提供帖子数据，无法绘制图表", logger_config)
            return
        
        # 统计每个subreddit的帖子数量
        subreddit_counts = {}
        for post in posts:
            subreddit = post['subreddit']
            if subreddit not in subreddit_counts:
                subreddit_counts[subreddit] = 0
            subreddit_counts[subreddit] += 1
        
        # 转换为DataFrame
        df = pd.DataFrame(list(subreddit_counts.items()), columns=['Subreddit', 'Count'])
        df = df.sort_values('Count', ascending=False)
        
        # 如果subreddit太多，只显示前10个，其余归为"其他"
        if len(df) > 10:
            top_10 = df.iloc[:10]
            others = pd.DataFrame([['其他', df.iloc[10:]['Count'].sum()]], columns=['Subreddit', 'Count'])
            df = pd.concat([top_10, others])
        
        # 绘制饼图
        plt.figure(figsize=(10, 8))
        plt.pie(df['Count'], labels=df['Subreddit'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # 保持饼图为圆形
        plt.title(title)
        
        if save:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"subreddit_distribution_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            info(f"饼图已保存到: {filepath}", logger_config)
        
        plt.show()
    
    def plot_engagement_metrics(self, posts: List[Dict[str, Any]], title: str = "帖子互动指标", 
                               save: bool = True, filename: str = None) -> None:
        """绘制帖子互动指标散点图
        
        Args:
            posts: 帖子列表
            title: 图表标题
            save: 是否保存图表
            filename: 保存的文件名，默认为engagement_metrics_{timestamp}.png
        """
        if not posts:
            warning("没有提供帖子数据，无法绘制图表", logger_config)
            return
        
        # 提取得分和评论数
        scores = [post['score'] for post in posts]
        comments = [post['num_comments'] for post in posts]
        subreddits = [post['subreddit'] for post in posts]
        
        # 绘制散点图
        plt.figure(figsize=(12, 8))
        scatter = plt.scatter(scores, comments, alpha=0.6, s=100, c=pd.factorize(subreddits)[0])
        
        # 添加图例
        unique_subreddits = list(set(subreddits))
        if len(unique_subreddits) <= 10:  # 只有当subreddit数量不多时才添加图例
            plt.legend(handles=scatter.legend_elements()[0], labels=unique_subreddits, 
                      title="Subreddit", loc="upper right")
        
        plt.xlabel('得分')
        plt.ylabel('评论数')
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 添加趋势线
        if len(posts) > 1:
            z = np.polyfit(scores, comments, 1)
            p = np.poly1d(z)
            plt.plot(scores, p(scores), "r--", alpha=0.8)
        
        if save:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"engagement_metrics_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            info(f"散点图已保存到: {filepath}", logger_config)
        
        plt.show()
    
    def plot_time_distribution(self, posts: List[Dict[str, Any]], title: str = "帖子时间分布", 
                             save: bool = True, filename: str = None) -> None:
        """绘制帖子发布时间分布直方图
        
        Args:
            posts: 帖子列表
            title: 图表标题
            save: 是否保存图表
            filename: 保存的文件名，默认为time_distribution_{timestamp}.png
        """
        if not posts:
            warning("没有提供帖子数据，无法绘制图表", logger_config)
            return
        
        # 转换时间戳为datetime对象
        timestamps = [datetime.fromtimestamp(post['created_utc']) for post in posts]
        
        # 绘制直方图
        plt.figure(figsize=(12, 6))
        plt.hist(timestamps, bins=20, alpha=0.7, color='skyblue')
        plt.xlabel('发布时间')
        plt.ylabel('帖子数量')
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        if save:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"time_distribution_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            info(f"直方图已保存到: {filepath}", logger_config)
        
        plt.show()
    
    def plot_keyword_frequency(self, posts: List[Dict[str, Any]], title: str = "关键词频率", 
                             top_n: int = 15, save: bool = True, filename: str = None) -> None:
        """绘制关键词频率条形图
        
        Args:
            posts: 帖子列表
            title: 图表标题
            top_n: 显示的关键词数量
            save: 是否保存图表
            filename: 保存的文件名，默认为keyword_frequency_{timestamp}.png
        """
        if not posts:
            warning("没有提供帖子数据，无法绘制图表", logger_config)
            return
        
        # 提取所有标题中的单词
        import re
        from collections import Counter
        
        # 停用词列表（可以根据需要扩展）
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'with', 
                     'by', 'about', 'like', 'through', 'over', 'before', 'after', 'between', 'under', 'during',
                     'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                     'of', 'from', 'as', 'i', 'me', 'we', 'us', 'you', 'he', 'she', 'it', 'they', 'them'}
        
        words = []
        for post in posts:
            title = post['title'].lower()
            # 使用正则表达式提取单词
            title_words = re.findall(r'\b[a-z]{3,}\b', title)
            # 过滤停用词
            title_words = [word for word in title_words if word not in stop_words]
            words.extend(title_words)
        
        # 统计词频
        word_counts = Counter(words)
        top_words = word_counts.most_common(top_n)
        
        # 转换为DataFrame
        df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
        
        # 绘制条形图
        plt.figure(figsize=(12, 8))
        bars = plt.barh(df['Word'], df['Frequency'], color='skyblue')
        plt.xlabel('频率')
        plt.ylabel('关键词')
        plt.title(title)
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # 在条形上添加数值标签
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width}', 
                    ha='left', va='center')
        
        if save:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"keyword_frequency_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            info(f"条形图已保存到: {filepath}", logger_config)
        
        plt.show()
    
    def plot_trend_over_time(self, posts: List[Dict[str, Any]], metric: str = 'score', 
                           title: str = None, save: bool = True, filename: str = None) -> None:
        """绘制指标随时间变化的趋势线
        
        Args:
            posts: 帖子列表
            metric: 要分析的指标，可选值: 'score', 'num_comments', 'upvote_ratio'
            title: 图表标题，默认根据metric自动生成
            save: 是否保存图表
            filename: 保存的文件名，默认为trend_{metric}_{timestamp}.png
        """
        if not posts:
            warning("没有提供帖子数据，无法绘制图表", logger_config)
            return
        
        # 验证指标是否有效
        valid_metrics = {'score', 'num_comments', 'upvote_ratio'}
        if metric not in valid_metrics:
            error(f"无效的指标: {metric}，有效值为: {valid_metrics}", logger_config)
            return
        
        # 准备数据
        timestamps = [datetime.fromtimestamp(post['created_utc']) for post in posts]
        values = [post[metric] for post in posts]
        
        # 创建DataFrame并按时间排序
        df = pd.DataFrame({'timestamp': timestamps, 'value': values})
        df = df.sort_values('timestamp')
        
        # 设置标题
        if not title:
            metric_names = {
                'score': '得分',
                'num_comments': '评论数',
                'upvote_ratio': '点赞比例'
            }
            title = f"{metric_names.get(metric, metric)}随时间的变化趋势"
        
        # 绘制趋势线
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['value'], marker='o', linestyle='-', alpha=0.7)
        plt.xlabel('时间')
        plt.ylabel(metric)
        plt.title(title)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        # 添加趋势线
        import numpy as np
        if len(posts) > 1:
            # 将时间转换为数值以便拟合
            x = np.array([(t - df['timestamp'].min()).total_seconds() for t in df['timestamp']])
            y = np.array(df['value'])
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(df['timestamp'], p(x), "r--", alpha=0.8)
        
        if save:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trend_{metric}_{timestamp}.png"
            filepath = os.path.join(self.output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            info(f"趋势图已保存到: {filepath}", logger_config)
        
        plt.show()