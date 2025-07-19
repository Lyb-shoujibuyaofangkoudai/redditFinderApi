# Reddit Finder API 服务

这是Reddit Finder项目的API服务组件，基于FastAPI框架构建，提供了企业级的API架构设计。

## 功能特点

- 基于FastAPI构建的高性能API服务
- 企业级项目架构设计
- 完整的依赖注入系统
- 统一的异常处理
- 请求日志中间件
- 标准化的API响应格式
- 详细的API文档（基于OpenAPI）

## 目录结构

```
serve/
├── __init__.py          # 包初始化文件
├── api.py               # API应用创建和配置
├── main.py              # 应用入口点
├── README.md            # 文档
├── dependencies/        # 依赖注入模块
│   ├── __init__.py
│   └── services.py      # 服务依赖
├── exceptions/          # 异常处理模块
│   ├── __init__.py
│   └── handlers.py      # 异常处理器
├── middleware/          # 中间件模块
│   ├── __init__.py
│   └── logging.py       # 日志中间件
├── models/              # 数据模型模块
│   ├── __init__.py
│   ├── common.py        # 通用响应模型
│   └── reddit.py        # Reddit相关模型
├── routes/              # 路由模块
│   ├── __init__.py
│   ├── reddit.py        # Reddit相关路由
│   └── visualization.py # 可视化相关路由
└── services/            # 服务模块
    ├── __init__.py
    └── reddit_service.py # Reddit服务
```

## 安装依赖

确保已安装以下依赖：

```bash
pip install fastapi uvicorn pydantic
```

## 启动服务

从项目根目录运行：

```bash
python -m src.serve.main
```

或者使用uvicorn直接启动：

```bash
uvicorn src.serve.main:app --reload
```

## API文档

启动服务后，访问以下URL查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API端点

### Reddit相关

- `GET /reddit/trending` - 获取热门帖子
- `POST /reddit/search` - 根据关键词查找帖子
- `POST /reddit/analyze` - 分析帖子趋势
- `POST /reddit/insights` - 生成内容洞察
- `GET /reddit/post/{post_id}` - 获取帖子内容
- `GET /reddit/post/{post_id}/comments` - 获取帖子评论

### 可视化相关

- `POST /visualization/chart` - 生成图表
- `GET /visualization/chart-types` - 获取支持的图表类型

## 使用示例

### 获取热门帖子

```python
import requests

response = requests.get("http://localhost:8000/reddit/trending?limit=10")
data = response.json()
print(data)
```

### 根据关键词查找帖子

```python
import requests

payload = {
    "keywords": ["python", "programming"],
    "subreddits": ["python", "programming"],
    "limit": 10,
    "sort": "relevance"
}

response = requests.post("http://localhost:8000/reddit/search", json=payload)
data = response.json()
print(data)
```

### 生成图表

```python
import requests

# 首先获取一些帖子数据
response = requests.get("http://localhost:8000/reddit/trending?limit=20")
data = response.json()
posts = data["data"]

# 生成subreddit分布饼图
response = requests.post(
    "http://localhost:8000/visualization/chart?chart_type=subreddit_distribution&title=Subreddit分布",
    json=posts
)
print(response.json())
```