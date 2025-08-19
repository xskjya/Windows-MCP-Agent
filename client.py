import asyncio
import base64
from typing import Dict, Any, Optional
from fastmcp import Client
from fastmcp.exceptions import ToolError
from src.agent.prompt.service import Prompt
from src.agent.service import OllamaToolAgent


# ========== 扩展 OllamaToolAgent，支持 MCP 工具调用 ==========
class WindowsMcpOllamaToolAgent(OllamaToolAgent):
    def __init__(self, **args):
        """
        初始化 Agent，继承自 OllamaToolAgent
        - client: MCP 客户端实例
        """
        super().__init__(**args)
        self.client: Optional[Client] = None  # 默认 MCP 客户端为空

    async def decide_action(self, user_input: str) -> Dict[str, Any]:
        """
        调用 LLM 判断是否需要工具
        返回: JSON 对象 {"tool_name": str|None, "tool_args": dict, "answer": str|None}
        """
        # 构建 Prompt
        prompt = Prompt.action_prompt(tools=self.tools, user_input=user_input)
        print("【prompt】\n", prompt)

        # 调用 LLM (同步接口 → 异步包装，避免阻塞 asyncio loop)
        loop = asyncio.get_running_loop()
        llm_output = await loop.run_in_executor(None, self.llm.invoke, prompt)
        print("【thinking】", llm_output)

        # 将 LLM 输出解析为 JSON
        tool = self.parse(llm_output)
        print("【parsed tool json】", tool)
        return tool

    async def act(self, tool: Dict[str, Any], user_input: str):
        """
        根据 tool JSON 执行动作
        - 如果 tool_name 存在 → 调用 MCP 工具
        - 否则 → 返回大语言模型的自然语言回答
        """
        if tool and tool.get("tool_name"):
            return await self.execute(tool)
        else:
            # 回退为普通对话
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self.llm.invoke, user_input)

    async def execute(self, tool: dict):
        """
        执行 MCP 工具
        """
        if not tool:
            print("[INFO] tool is None, skip execution")
            return None
        return await self.calling_tool(tool)

    async def calling_tool(self, tool: dict):
        """
        调用 MCP 工具
        """
        try:
            async with self.client:
                result = await self.client.call_tool(
                    tool["tool_name"], {**tool["tool_args"]}
                )
                return result
        except ToolError as e:
            print(f"[ERROR] Tool call failed: {e}")
            return {"error": str(e), "fallback": True}


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

    # 初始化 Agent
    agent = WindowsMcpOllamaToolAgent(model_name="qwen3:1.7b")
    agent.client = client
    agent.tools = tools_info

    # 循环交互
    while True:
        query = input("user input: ")
        tool = await agent.decide_action(query)  # 判断动作
        result = await agent.act(tool, query)    # 执行动作
        handler_result(result)                   # 处理结果


if __name__ == "__main__":
    asyncio.run(main())
