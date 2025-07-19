# Reddit Finder
## 项目简介
Reddit Finder 是一个强大的 Reddit 内容发现和分析工具，专为内容创作者、营销人员和数据分析师设计。它能够帮助用户发现 Reddit 上的热门话题和讨论，分析内容趋势，并提供有价值的内容洞察，从而帮助用户找到有价值的内容灵感。

## 功能特点
- 内容发现 ：查找热门帖子和基于关键词的内容搜索
- 趋势分析 ：分析帖子趋势，包括活跃度、情感分析和病毒传播潜力
- 内容洞察 ：生成内容模式分析和建议
- 数据可视化 ：支持多种图表展示数据分析结果
- 词云生成 ：基于 AI 分析的情感词和需求词词云
- API 服务 ：提供完整的 RESTful API 接口
## 技术栈
- Python 3.12+
- PRAW (Python Reddit API Wrapper)
- FastAPI
- LangChain 和 LangGraph
- Matplotlib 和 Pandas
- 支持 OpenAI 和 Ollama 等 LLM 集成
## 安装说明
### 前置条件
- Python 3.12 或更高版本
- Reddit API 凭证（Client ID、Client Secret 和 User Agent）
- （可选）OpenAI API 密钥（用于 AI 内容分析）
### 安装步骤
1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/reddit-finder.git
   cd reddit-finder
   ```
2. 创建虚拟环境并安装依赖(建议使用UV)
   ```bash
   uv sync
   ```
3. 配置环境变量
   复制 .env.example 文件为 .env ，并填入你的 Reddit API 凭证和其他配置(其中使用的大模型建议使用GPT)
   ```bash
   cp .env.example .env
   ```
4. 运行程序
   ```bash
   uv python main.py

   # 或者
   python -m src.serve.main

   # 或者使用 uvicorn 直接启动
   uvicorn src.serve.main:app --reload
   ```
   启动后，可以通过以下 URL 访问 API 文档：

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 作为python库使用
```python
from src.utils.reddit_finder import RedditFinder

# 初始化 RedditFinder
finder = RedditFinder()

# 查找热门帖子
trending_posts = finder.find_trending_posts(limit=10)

# 根据关键词查找帖子
keyword_posts = finder.find_posts_by_keywords(
    keywords=["python", "data analysis"],
    subreddits=["python", "datascience"],
    limit=20,
    sort="relevance"
)

# 分析趋势
trends = finder.analyze_trends(trending_posts)
# 生成内容洞察
insights = finder.generate_content_insights(trending_posts)

```


## 其他
1. 本项目目前只是一个demo，切勿用在商业用途。
2. 项目可能存在一些不合理的地方，如专业分析帖子时的一些算法不符合实际或参考价值不是很大。
