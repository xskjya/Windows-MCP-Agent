from langchain_ollama import OllamaLLM
import re
import json
import asyncio
from typing import Dict, Any, Optional, Union, Callable
from fastmcp import Client
from fastmcp.exceptions import ToolError
from src.agent.prompt.service import Prompt
from src.agent.tool_agent.ToolAgent import ToolAgent

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



class GenericToolAgent(ToolAgent):
    """
    通用工具代理类，支持 Ollama / API / 自定义模型 + MCP 工具调用。
    Attributes:
        model: 可调用对象或模型实例，用于生成回答
        tools: 工具字典
        client: 可选 MCP 客户端
        debug: 是否开启调试输出
    """

    def __init__(
        self,
        model: Optional[Union[OllamaLLM, Callable[[str], str]]] = None,  # 模型实例或可调用函数
        tools: Optional[Dict[str, Dict[str, Any]]] = None,               # 工具字典
        client: Optional[Client] = None,                                 # MCP客户端
        debug: bool = True                                               # 是否打印调试信息
    ):
        self.model = model
        self.tools: Dict[str, Dict[str, Any]] = tools or Prompt.get_tools_default()  # 初始化工具字典
        self.client: Optional[Client] = client
        self.debug = debug

    def log(self, *args, **kwargs):
        """统一打印调试信息，debug 为 True 才输出"""
        if self.debug:
            print(*args, **kwargs)

    def parse(self, model_output: str) -> Optional[Dict[str, Any]]:
        """
        尝试解析模型输出 JSON
        - 去掉 <think> 标签及其内容
        - 优先直接解析为 JSON
        - 如果失败，提取第一个 JSON 对象再解析
        """
        output_clean = re.sub(r"<think>.*?</think>", "", model_output, flags=re.DOTALL).strip()
        try:
            return json.loads(output_clean)  # 尝试直接解析
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", output_clean, re.DOTALL)  # 提取第一个 JSON 对象
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError as e:
                    self.log(f"[ERROR] JSON解析失败: {e}\n原始输出: {output_clean}")
                    return None
            else:
                self.log(f"[ERROR] 未找到 JSON: {output_clean}")
                return None

    async def call_model(self, prompt_or_input: str) -> str:
        """
        根据模型类型调用模型生成输出
        - OllamaLLM 实例使用 invoke 方法
        - 可调用对象（函数或API）直接调用
        - fallback 返回输入
        """
        loop = asyncio.get_running_loop()  # 获取当前事件循环
        if isinstance(self.model, OllamaLLM):
            return await loop.run_in_executor(None, self.model.invoke, prompt_or_input)  # Ollama 调用
        elif callable(self.model):
            return await loop.run_in_executor(None, self.model, prompt_or_input)        # 自定义函数调用
        else:
            return prompt_or_input  # fallback，直接返回输入

    async def decide_action(self, user_input: str) -> Dict[str, Any]:
        """
        调用模型判断是否需要执行工具动作
        返回字典: {"tool_name": str|None, "tool_args": dict, "answer": str|None}
        """
        prompt = Prompt.action_prompt(tools=self.tools, user_input=user_input)  # 构建 Prompt
        self.log("【prompt】\n", prompt)

        output = await self.call_model(prompt)  # 调用模型
        self.log("【model output】", output)

        tool = self.parse(output)  # 尝试解析 JSON
        return tool or {"tool_name": None, "tool_args": {}, "answer": output}  # fallback 返回回答

    async def execute_tool(self, tool: dict):
        """
        执行 MCP 工具
        - 异步调用 client.call_tool
        - 捕获 ToolError 或未知异常
        """
        if not tool:
            self.log("[INFO] tool is None, skip execution")
            return None

        if not self.client:
            self.log("[WARN] MCP client 未初始化，模拟返回 tool_args")
            return {"tool_args": tool.get("tool_args", {}), "simulated": True}

        try:
            async with self.client:  # 确保异步上下文
                result = await self.client.call_tool(
                    tool["tool_name"], {**tool.get("tool_args", {})}  # 传递工具参数
                )
                return result
        except ToolError as e:
            self.log(f"[ERROR] Tool call failed: {e}")
            return {"error": str(e), "fallback": True}
        except Exception as e:
            self.log(f"[ERROR] 未知异常: {e}")
            return {"error": str(e), "fallback": True}

    async def act(self, tool: Dict[str, Any], user_input: str):
        """
        根据解析出的 tool 执行动作
        - 如果工具存在，执行工具
        - 工具执行超时或异常，回退使用模型生成回答
        """
        if tool and tool.get("tool_name"):
            try:
                return await asyncio.wait_for(self.execute_tool(tool), timeout=10.0)  # 设置超时
            except asyncio.TimeoutError:
                self.log("[WARN] 工具执行超时，回退为模型回答")

        # fallback：使用模型生成回答
        return await self.call_model(user_input)

    async def run(self, user_input: str):
        """
        主执行函数
        - 决定动作
        - 执行动作或调用模型生成回答
        - 返回最终结果
        """
        tool = await self.decide_action(user_input)
        result = await self.act(tool, user_input)
        return result

