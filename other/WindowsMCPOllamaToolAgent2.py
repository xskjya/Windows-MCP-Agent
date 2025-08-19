import asyncio
from OllamaAgent import OllamaToolAgent   # 导入上一步定义的基础 Agent
from fastmcp import Client                # MCP 客户端
from fastmcp.exceptions import ToolError  # 工具调用错误类型

# ========== 扩展 OllamaToolAgent，支持 MCP 工具调用 ==========
class WindowsMcpOllamaToolAgent(OllamaToolAgent):
    def __init__(self, **args):
        """
        初始化 Agent，继承自 OllamaToolAgent
        - client: MCP 客户端实例
        """
        super().__init__(**args)
        self.client = None  # 默认 MCP 客户端为空，后续在 main() 中赋值

    async def execute(self, tool: dict):
        """
        异步执行工具
        - tool: 解析出的 JSON 格式工具调用对象
        """
        if not tool:
            print("[INFO] tool is None, skip execution")
            return None
        return await self.calling_tool(tool)  # 调用工具执行逻辑

    async def run(self, user_input: str):
        """
        Agent 主执行函数
        - 构建 Prompt
        - 调用 LLM 判断是否需要工具
        - 如果需要：解析 JSON 并执行工具
        - 如果不需要：直接返回 LLM 输出
        """
        # 构建 Prompt
        prompt = self.build_prompt(user_input)
        print('【prompt】')
        print(prompt)

        # 调用大语言模型
        llm_output = self.llm.invoke(prompt)
        print("【thinking】:", llm_output)

        # 将 LLM 输出解析为 tool JSON
        tool = self.parse(llm_output)
        print("【tool json】:", tool)

        # 如果需要调用工具，则执行
        if tool and tool["tool_name"]:
            return await self.execute(tool)

        # 否则直接返回大语言模型的输出
        return self.llm.invoke(user_input)

    async def calling_tool(self, tool: dict):
        """
        调用 MCP 工具
        - 使用 fastmcp.Client 与 MCP 服务交互
        - tool["tool_name"]: 工具名称
        - tool["tool_args"]: 工具参数
        """
        try:
            async with self.client:
                # 调用 MCP 工具
                result = await self.client.call_tool(tool["tool_name"], {**tool["tool_args"]})
                return result

        except ToolError as e:
            # 捕获 MCP 工具调用异常
            print(f"Tool call failed: {e}")
            return None


# ========== 处理工具执行结果，根据类型做不同处理 ==========
def handler_result(result):
    """
    工具结果处理函数
    - 可根据返回的数据类型进行不同处理
    - 例如保存图片、解析文本等
    """
    # 这里预留了处理逻辑，可以根据工具返回的 result 结构来扩展
    # 例如如果 result.data 中有图片 (base64)，可以解码保存成文件

    pass
    #
    # import base64
    #
    # # 假设返回数据中包含截图 (base64 编码)
    # image_base64 = result.data["screenshot"]
    #
    # # 转回 byte 数据
    # image_bytes = base64.b64decode(image_base64)
    #
    # # 保存为文件
    # with open("output.png", "wb") as f:
    #     f.write(image_bytes)


# ========== 主程序入口 ==========
async def main():
    # 初始化 MCP 客户端，main.py 表示配置文件或服务入口
    client = Client("main.py")

    # 获取 MCP 提供的工具信息
    tools_info = {}
    async with client:
        tools = await client.list_tools()
        for tool in tools:
            # 保存工具描述信息
            tools_info[tool.name] = {"desc": tool.description}
            # 保存输入参数模式 (inputSchema)
            if tool.inputSchema:
                tools_info[tool.name]["params"] = tool.inputSchema

    # 初始化 Agent，指定 LLM 模型
    # 可切换为 deepseek-r1:1.5b / deepseek-r1:7b 等
    agent = WindowsMcpOllamaToolAgent(model_name="qwen3:1.7b")
    agent.client = client      # 绑定 MCP 客户端
    agent.tools = tools_info   # 更新工具字典为 MCP 工具列表

    # 循环交互，持续接受用户输入
    while True:
        query = input("user input: ")  # 等待用户输入
        result = await agent.run(query)

        # 根据不同类型的工具进一步处理
        result = handler_result(result)


# Python 程序入口
if __name__ == "__main__":
    asyncio.run(main())
