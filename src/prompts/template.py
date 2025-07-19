import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.prebuilt.chat_agent_executor import AgentState

from src.graph.state import State, WordCloudState
from src.utils.logging import info

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    使用Jinja2加载并渲染指定名称的.md模板文件，返回替换变量后的字符串。
    若加载失败抛出带错误信息的ValueError。
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(prompt_name: str, state: AgentState | State | WordCloudState) -> list:
    """
       1. 合并当前时间和state字段作为模板变量
       2. 渲染指定模板生成system提示词
       3. 将system提示词与历史消息组合返回
       示例输出: [{"role":"system","content":"..."}] + state["messages"]
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        # info(f"获取模板提示词：{system_prompt} 传入的state：{state}")
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"获取模板错误： {prompt_name}: {e}")


if __name__ == "__main__":
    # Example usage
    prompt_name = "reception"
    state = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
        ],
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
    }
    messages = apply_prompt_template(prompt_name, state)
    print(messages)