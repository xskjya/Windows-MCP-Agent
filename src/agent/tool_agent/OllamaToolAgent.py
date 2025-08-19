from langchain_ollama import OllamaLLM
from typing import Dict, Any, Optional
from fastmcp import Client
from src.agent.tool_agent.GenericToolAgent import GenericToolAgent

"""
用法：
    agent = OllamaToolAgent(
        model_name="qwen3:1.7b",
        tools= tools_info,
        client= client,
        # 额外ollama的参数
    )
"""
class OllamaToolAgent(GenericToolAgent):
    """基于 GenericToolAgent 的 Ollama 专用工具代理类"""
    def __init__(
        self,
        model_name: str = "qwen3:1.7b",                  # Ollama 模型名称
        tools: Optional[Dict[str, Dict[str, Any]]] = None,
        client: Optional[Client] = None,
        debug: bool = True,
        **kwargs                                         # 可传给 OllamaLLM 的额外参数
    ):
        ollama_model = OllamaLLM(model=model_name, **kwargs)  # 初始化 Ollama 模型
        super().__init__(
            model=ollama_model,
            tools=tools,
            client=client,
            debug=debug
        )

