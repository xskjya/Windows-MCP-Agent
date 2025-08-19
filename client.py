import asyncio
import base64
from fastmcp import Client

from src.agent import OllamaToolAgent
from src.agent.tool_agent.ApiToolAgent import APIToolAgent


# ========== 通用结果处理 ==========
def handler_result(result):
    """
    工具结果处理函数
    - 文本: 直接打印
    - 图片: 解码保存
    - 其他: 打印原始内容
    """
    if result is None:
        print("[INFO] No result")
        return None

    # 如果是字符串，直接输出
    if isinstance(result, str):
        print("【LLM回答】", result)
        return result

    # 如果返回对象带 data 字段
    if hasattr(result, "data"):
        data = result.data
        if "screenshot" in data:  # 假设工具返回截图
            image_base64 = data["screenshot"]
            image_bytes = base64.b64decode(image_base64)
            with open("output.png", "wb") as f:
                f.write(image_bytes)
            print("【保存截图】 output.png")
            return "image_saved"
        else:
            print("【工具返回数据】", data)
            return data

    # 默认打印
    print("【未知返回类型】", result)
    return result


# ========== 主程序入口 ==========
async def main():
    # 初始化 MCP 客户端
    client = Client("server.py")

    # 获取 MCP 提供的工具信息，整理成描述字典
    tools_info = {}
    async with client:
        tools = await client.list_tools()
        for tool in tools:
            tools_info[tool.name] = {
                "desc": tool.description,
                "params": tool.inputSchema or {}
            }
    ########################模型示例####################################
    # 1.初始化 OllamaToolAgent： 继承GenericToolAgent
    # agent = OllamaToolAgent(
    #     model_name="qwen3:1.7b",
    #     tools= tools_info,
    #     client= client,
    #     # 额外ollama的参数
    # )

    # 2.API或函数调用
    # 定义一个简单 API 函数
    def my_api(prompt: str) -> str:
        return '{"tool_name": "Launch-Tool", "tool_args": {"name": "chrome"}}'
    agent = APIToolAgent(
        api_callable=my_api,
        tools= tools_info,
        client= client,
    )

    # 循环交互
    while True:
        query = input("user input: ")
        tool = await agent.decide_action(query)  # 判断动作
        result = await agent.act(tool, query)    # 执行动作
        handler_result(result)                   # 处理结果


if __name__ == "__main__":
    asyncio.run(main())
