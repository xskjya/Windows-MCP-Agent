from fastmcp import FastMCP
from contextlib import asynccontextmanager
from platform import system, release
from textwrap import dedent
import asyncio
import ctypes
from live_inspect.watch_cursor import WatchCursor
from humancursor import SystemCursor

from src.agent.tools import register_all_tools
from src.desktop import Desktop

# ============ 初始化 ============ #
os = system()
version = release()
desktop = Desktop()
default_language = desktop.get_default_language()
cursor = SystemCursor()
watch_cursor = WatchCursor()
ctypes.windll.user32.SetProcessDPIAware()

instructions = dedent(f"""
Windows MCP server provides tools to interact directly with the {os} {version} desktop, 
thus enabling to operate the desktop on the user's behalf.
""")

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastMCP):
    try:
        watch_cursor.start()
        await asyncio.sleep(1)
        yield
    finally:
        watch_cursor.stop()

# 创建 MCP 实例
mcp = FastMCP(name="windows-mcp", instructions=instructions, lifespan=lifespan)

# 注册所有工具
register_all_tools(mcp, desktop, default_language)

# 启动
if __name__ == "__main__":
    mcp.run()
