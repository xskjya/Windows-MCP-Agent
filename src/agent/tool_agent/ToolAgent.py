from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from typing import Dict, Any, Optional, Union, Callable
from fastmcp import Client
from src.agent.prompt.service import Prompt

class ToolAgent(ABC):
    """
    抽象基类：工具代理类
    支持 Ollama / API / 自定义模型 + MCP 工具调用
    子类必须实现 parse / decide_action / execute_tool / act 方法
    Attributes:
        model: 可调用对象或模型实例，用于生成回答
        tools: 工具字典
        client: 可选 MCP 客户端
        debug: 是否开启调试输出
    """
    def __init__(
            self,
            model: Optional[Union[OllamaLLM, Callable[[str], str]]] = None,
            tools: Optional[Dict[str, Dict[str, Any]]] = None,
            client: Optional[Client] = None,
            debug: bool = True
    ):
        self.model = model
        self.tools: Dict[str, Dict[str, Any]] = tools or Prompt.get_tools_default()
        self.client: Optional[Client] = client
        self.debug = debug

    @abstractmethod
    def parse(self, model_output: str) -> Optional[Dict[str, Any]]:
        """解析模型输出为 JSON"""

    @abstractmethod
    async def decide_action(self, user_input: str) -> Dict[str, Any]:
        """调用模型判断是否需要执行工具动作"""

    @abstractmethod
    async def execute_tool(self, tool: dict):
        """执行 MCP 工具"""

    @abstractmethod
    async def act(self, tool: Dict[str, Any], user_input: str):
        """根据解析出的 tool 执行动作"""

