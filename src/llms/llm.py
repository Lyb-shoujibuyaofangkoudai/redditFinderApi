import os
from typing import Dict, Optional, Any, List
from enum import Enum
from dotenv import load_dotenv
from langchain.schema.language_model import BaseLanguageModel
from langchain_openai import ChatOpenAI

from src.config.env import MODEL, API_KEY, BASE_URL, REQUEST_TIMEOUT
from src.llms.litellm_v2 import ChatLiteLLMV2 as ChatLiteLLM

from litellm import LlmProviders

from src.utils.logging import create_logger, info, error

# 加载环境变量
load_dotenv()

# 创建logger配置
logger_config = create_logger()

def is_local_free_proxy_api(model_name: str) -> bool:
    return (
        model_name
        and "/" in model_name
        and model_name.split("/")[0] == 'local_free_api'
    )

def is_openrouter_api_model(url) -> bool:
    """
    用于校验是否是openrouter api，这个第三方接口有些模型会导致使用ChatLiteLLM时使用到错误的方法
    :param url:
    :return: 是否是 openrouter api
    """
    return 'openrouter.ai' in url

def is_litellm_model(model_name: str) -> bool:
    """
    检查模型名称是否应该由LiteLLM处理

    Args:
        model_name: 要检查的模型名称

    Returns:
        bool: 如果模型应该由LiteLLM处理则为True，否则为False
    """
    return (
            model_name
            and "/" in model_name
            and model_name.split("/")[0] in [p.value for p in LlmProviders]
    )


class LLM:
    """大模型工厂类

    使用工厂模式创建不同提供商的大模型实例。
    根据环境变量自动选择合适的模型提供商。
    支持基础模型、推理模型和视觉模型三种类型。
    """

    @staticmethod
    def create_llm(
            streaming: bool = True,
            **kwargs: Any
    ) -> BaseLanguageModel:
        """创建大模型实例

        Args:
            provider: 模型提供商，可选值：'openai', 'deepseek', 'ollama', 'bailian'。
                      如果为None，则根据环境变量自动选择。
            streaming: 是否启用流式输出，默认为True
            **kwargs: 传递给模型的其他参数

        Returns:
            BaseLanguageModel: 大模型实例

        Raises:
            ValueError: 如果指定的模型类型不支持或无法创建模型实例
        """
        # 将streaming参数添加到kwargs中
        kwargs["streaming"] = streaming

        # 根据模型类型获取对应的配置
        model_name = MODEL
        api_key = API_KEY
        base_url = BASE_URL
        info(f"使用模型名称: {model_name}")
        # 设置模型参数
        kwargs["model"] = model_name
        # 设置模型重试次数
        kwargs["max_retries"] = 3
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url
        if is_local_free_proxy_api(model_name):
            kwargs["default_headers"] = {
                "Authorization": f"Bearer {api_key}"
            }
            kwargs["model"] = model_name.replace("local_free_api/", "", 1)

        # 根据模型名称判断使用哪种模型实例
        try:
            if not is_openrouter_api_model(base_url) and not is_local_free_proxy_api(model_name) and is_litellm_model(model_name):
                kwargs["request_timeout"] = REQUEST_TIMEOUT
                llm = LLM._create_litellm_model(**kwargs)
                info(f"成功创建LiteLLM 模型实例: {model_name}", logger_config)
                return llm
            else:
                kwargs["timeout"] = REQUEST_TIMEOUT
                llm = LLM._create_openai_llm(**kwargs)
                info(f"成功创建OpenAI 模型实例: {model_name}", logger_config)
                return llm
        except Exception as e:
            error(f"创建模型实例失败: {str(e)}", logger_config)
            raise

    @staticmethod
    def _get_model_config() -> tuple[Optional[str], Optional[str], Optional[str]]:
        model_name = MODEL
        api_key = API_KEY
        base_url = BASE_URL
        if not model_name or not base_url:
            error(
                f"模型名称或API密钥未配置，请检查环境变量设置。")
        return model_name, api_key, base_url

    @staticmethod
    def _create_openai_llm(**kwargs: Any) -> ChatOpenAI:
        """创建OpenAI模型实例"""
        default_params = {
            "temperature": 0.7,
            "streaming": True,
        }
        # 合并默认参数和自定义参数
        params = {**default_params, **kwargs}
        info(f"OpenAI模型参数: {params}", logger_config)
        return ChatOpenAI(**params)

    @staticmethod
    def _create_litellm_model(**kwargs: Any) -> ChatLiteLLM:
        """创建LiteLLM模型实例"""
        default_params = {
            "temperature": 0.7,
            "streaming": True,
        }
        # 合并默认参数和自定义参数
        params = {**default_params, **kwargs}
        info(f"LiteLLM模型参数: {params}", logger_config)
        return ChatLiteLLM(**params)


_llm_cache = None
def get_llm_model() -> BaseLanguageModel:
    """
    获取模型
    Returns:
        BaseLanguageModel: 模型实例
    """
    global _llm_cache
    if _llm_cache is not None:
        return _llm_cache

    # 创建新的模型实例
    llm = LLM.create_llm()

    # 缓存模型实例
    _llm_cache = llm

    return llm


if __name__ == "__main__":
    llm = get_llm_model()
    # 使用基础模型进行对话
    async def run():
        from langchain_core.messages import HumanMessage
        response3 = llm.astream(
            [HumanMessage(
                content=[
                    {"type": "text", "text": "这张图片中的是哪部动画片中的角色？"},
                    {
                        "type": "image_url", "image_url":
                        {
                            "url": f"data:image/jpeg;base64,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"}
                    }
                ]
            ),
            ])
        async for chunk in response3:
            print(chunk.content, end="", flush=True)


    import asyncio

    # 运行异步函数
    asyncio.run(run())
