import requests
from markdownify import markdownify

def register_web_tools(mcp):
    @mcp.tool(name='Scrape-Tool',description='Fetch and convert webpage content to markdown format. Provide full URL including protocol (http/https). Returns structured text content suitable for analysis.')
    def scrape_tool(url: str) -> str:
        """
        抓取网页内容并转换为 Markdown 文本
        :param url: 完整 URL (http/https)
        :return: Markdown 格式网页内容
        """
        response = requests.get(url, timeout=10)
        html = response.text
        content = markdownify(html=html)
        return f'Scraped the contents of the entire webpage:\n{content}'


