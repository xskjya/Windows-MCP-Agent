import json
import re
from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM


# ===== 定义一个封装了工具调用能力的 Agent 类 =====
class OllamaToolAgent:
    def __init__(self, model_name: str = "qwen3:1.7b"):
        """
        初始化 Agent：
        - model_name: 默认使用 "qwen3:1.7b" 模型
        - llm: 使用 Ollama LLM
        - tools: 定义可调用的工具字典，每个工具包含:
            * func: 工具执行函数
            * desc: 工具功能描述
            * params: 参数列表
        """
        # 初始化 Ollama LLM
        self.llm = OllamaLLM(model=model_name)

        # 定义可用工具字典
        self.tools: Dict[str, Dict[str, Any]] = {
            "open_browser": {
                "func": lambda url: print(f"[TOOL] 打开浏览器: {url}"),  # 工具执行函数
                "desc": "打开一个网页，url 为网页地址",                  # 工具描述
                "params": ["url"]                                        # 工具参数列表
            },
            "search_google": {
                "func": lambda query: print(f"[TOOL] Google 搜索: {query}"),
                "desc": "在 Google 搜索指定内容，query 为搜索关键词",
                "params": ["query"]
            },
            "click_button": {
                "func": lambda selector: print(f"[TOOL] 点击网页上的按钮: {selector}"),
                "desc": "点击网页上的指定按钮，selector 为按钮选择器",
                "params": ["selector"]
            }
        }

    def build_prompt(self, user_input: str) -> str:
        """
        构建用于 LLM 的 Prompt
        - 包含工具列表及描述（带参数信息）
        - Few-shot 示例（输入→JSON输出）帮助模型理解格式
        - 用户输入在最后作为上下文
        """
        # 拼接工具描述（包含 desc 和 params）
        tool_descriptions = "\n".join(
            [
                f"{name}: {{\n"
                f"  desc: '{info['desc']}',\n"
                f"  params: {json.dumps(info.get('params', {}), ensure_ascii=False)}\n"
                f"}}"
                for name, info in self.tools.items()
            ]
        )

        # Few-shot 示例，给模型参考，帮助模型输出 JSON 格式
        examples = """
        示例：
        用户输入: 打开百度首页
        输出:
        {"tool_name": "open_browser", "tool_args": {"url": "https://www.baidu.com"}}

        用户输入: 搜索天气
        输出:
        {"tool_name": "search_google", "tool_args": {"query": "北京天气"}}
        """

        # 完整 Prompt 模板
        prompt = f"""
        你是智能助理，根据用户指令判断是否需要调用工具。
        如果需要调用工具，请严格输出 JSON:
        {{
            "tool_name": "工具名称",
            "tool_args": {{}}
        }}
        如果不需要调用工具，直接输出答案:
        {{
            "tool_name": null,
            "tool_args": {{}},
            "answer":    答案
        }}

        可用工具列表：
        {tool_descriptions}

        {examples}

        用户输入: {user_input}
        """

        return prompt

    def parse(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """
        解析 LLM 输出的 JSON
        - 去掉 <think>...</think> 部分
        - 提取第一个 JSON 对象
        - 返回解析后的字典
        """
        # 去掉 <think>...</think> 标签及其内容，避免污染 JSON 解析
        llm_output_clean = re.sub(r"<think>.*?</think>", "", llm_output, flags=re.DOTALL).strip()

        # 尝试直接解析为 JSON
        try:
            data: Dict[str, Any] = json.loads(llm_output_clean)
            return data
        except json.JSONDecodeError:
            # 如果失败，尝试提取第一个 JSON 对象再解析
            match = re.search(r"\{.*\}", llm_output_clean, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    return data
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON 解析失败: {e}")
                    print(f"原始输出: {llm_output_clean}")
                    return None
            else:
                # 如果没找到 JSON，直接报错
                print(f"[ERROR] 未找到 JSON: {llm_output_clean}")
                return None

    def execute(self, tool: dict):
        """
        执行工具
        - 传入的 tool 是解析后的 JSON 对象
        - 根据 tool_name 找到对应的工具函数并执行
        """
        pass  # 这里留空，后续实现

    def run(self, user_input: str):
        """
        Agent 主执行函数
        - 构建 Prompt
        - 调用 LLM 获取工具判断 JSON
        - 打印 LLM 输出
        - 调用 parse_and_execute 执行工具
        """
        # 构建 Prompt
        prompt = self.build_prompt(user_input)
        # 调用 LLM
        llm_output = self.llm.invoke(prompt)
        # 调用解析和执行流程（待补充实现 parse_and_execute）
        self.parse_and_execute(llm_output)
