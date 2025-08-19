from fastmcp import Client
from src.agent.tool_agent.GenericToolAgent import GenericToolAgent
from typing import Dict, Any, Callable, Optional

"""
用法：
    # API或函数调用
    # 定义一个简单 API 函数
    def my_api(prompt: str) -> str:
        return '{"tool_name": "open_browser", "tool_args": {"url": "https://github.com"}, "answer": "Opening GitHub"}'
    
    agent = APIToolAgent(
        api_callable=my_api,
        tools= tools_info,
        client= client,
    )
"""

class APIToolAgent(GenericToolAgent):
    """
    API 工具代理类
    - 继承 GenericToolAgent
    - 使用任意可调用的 API 或函数作为模型
    - 保留 MCP 工具调用能力
    """

    def __init__(
        self,
        api_callable: Callable[[str], str],
        tools: Optional[Dict[str, Dict[str, Any]]] = None,
        client: Optional[Client] = None,
        debug: bool = True
    ):
        """
        初始化 API 工具代理
        Args:
            api_callable: 任意接收字符串输入并返回字符串的函数或 API
            tools: 可选工具字典
            client: 可选 MCP 客户端
            debug: 是否打印调试信息
        """
        super().__init__(model=api_callable, tools=tools, client=client, debug=debug)

    # 如果需要，可覆盖 decide_action 或 parse 方法，实现特定 API 输出解析
    async def decide_action(self, user_input: str) -> Dict[str, Any]:
        """
        调用 API 判断是否需要工具动作
        - 默认逻辑使用 GenericToolAgent 的 decide_action
        - 可根据 API 输出格式自定义解析
        """
        return await super().decide_action(user_input)

    def parse(self, model_output: str) -> Optional[Dict[str, Any]]:
        """
        API 输出解析，可根据 API 返回 JSON 或自定义格式覆盖
        """
        # 默认沿用 GenericToolAgent 的解析
        return super().parse(model_output)


