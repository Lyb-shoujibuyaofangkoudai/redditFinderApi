import json
import json_repair

# from src.utils.logging import error


def repair_json_output(content: str) -> str:
    """
    修复和规范化 JSON 输出。

    Args:
        content (str): 可能包含 JSON 的字符串内容

    Returns:
        str: 修复后的 JSON 字符串，如果不是 JSON 则返回原始内容
    """
    content = content.strip()
    if content == "":
        return "{}"
    if content.startswith(("{", "[")) or "```json" in content or content.startswith("json"):
        try:
            # 如果内容被包裹在```json代码块中，提取JSON部分
            if content.startswith("```json"):
                content = content.removeprefix("```json")

            if content.startswith("json"):
                content = content.removeprefix("json")

            if content.endswith("```"):
                content = content.removesuffix("```")

            # 尝试修复并解析JSON
            repaired_content = json_repair.loads(content)
            return json.dumps(repaired_content)
        except Exception as e:
            # error(f"JSON repair failed: {e}")
            print(f"JSON repair failed: {e}")
    return content


if  __name__ == "__main__":
    print(repair_json_output(''))