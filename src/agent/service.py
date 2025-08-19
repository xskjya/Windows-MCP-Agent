from langchain_ollama import OllamaLLM
import re
import json
import asyncio
from typing import Dict, Any, Optional
from fastmcp import Client
from fastmcp.exceptions import ToolError
from src.agent.prompt.service import Prompt

class OllamaToolAgent:
    def __init__(self, model_name: str = "qwen3:1.7b"):
        """
        异步 Agent 初始化
        - model_name: Ollama 模型名称
        - llm: Ollama LLM
        - tools: 可调用工具字典
        """
        self.llm = OllamaLLM(model=model_name)
        self.tools: Dict[str, Dict[str, Any]] = Prompt.get_tools_default()
        self.client: Optional[Client] = None  # MCP 客户端，可在子类或外部设置

    def parse(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """
        解析 LLM 输出 JSON
        """
        llm_output_clean = re.sub(r"<think>.*?</think>", "", llm_output, flags=re.DOTALL).strip()
        try:
            return json.loads(llm_output_clean)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", llm_output_clean, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 解析失败: {e}\n原始输出: {llm_output_clean}")
                    return None
            else:
                print(f"[ERROR] 未找到 JSON: {llm_output_clean}")
                return None

    async def decide_action(self, user_input: str) -> Dict[str, Any]:
        """
        异步调用 LLM 判断是否需要工具
        返回: {"tool_name": str|None, "tool_args": dict, "answer": str|None}
        """
        prompt = Prompt.action_prompt(tools=self.tools, user_input=user_input)
        print("【prompt】\n", prompt)

        loop = asyncio.get_running_loop()
        llm_output = await loop.run_in_executor(None, self.llm.invoke, prompt)
        print("【thinking】", llm_output)

        tool = self.parse(llm_output)
        print("【parsed tool json】", tool)
        return tool

    async def act(self, tool: Dict[str, Any], user_input: str):
        """
        根据解析出的 tool 执行动作
        """
        if tool and tool.get("tool_name"):
            return await self.execute(tool)
        else:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(None, self.llm.invoke, user_input)

    async def execute(self, tool: dict):
        """
        执行工具（异步）
        """
        if not tool:
            print("[INFO] tool is None, skip execution")
            return None

        if not self.client:
            print("[WARN] MCP client 未初始化，返回 tool_args")
            return {"tool_args": tool.get("tool_args", {})}

        return await self.calling_tool(tool)

    async def calling_tool(self, tool: dict):
        """
        真正调用 MCP 工具
        """
        try:
            async with self.client:
                result = await self.client.call_tool(
                    tool["tool_name"], {**tool.get("tool_args", {})}
                )
                return result
        except ToolError as e:
            print(f"[ERROR] Tool call failed: {e}")
            return {"error": str(e), "fallback": True}

    async def run(self, user_input: str):
        """
        Agent 主执行函数
        """
        tool = await self.decide_action(user_input)
        return await self.act(tool, user_input)
