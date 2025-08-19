import json

class Prompt:
    # tools工具模版
    @staticmethod
    def get_tools_default():
        return {
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

    @staticmethod
    def action_prompt(tools, user_input: str) -> str:
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
                for name, info in tools.items()
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

    
