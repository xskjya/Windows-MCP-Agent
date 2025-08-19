from .app_tools import register_app_tools
from .input_tools import register_input_tools
from .system_tools import register_system_tools
from .web_tools import register_web_tools

def register_windows_all_tools(mcp, desktop, default_language):
    register_app_tools(mcp, desktop, default_language)
    register_input_tools(mcp, desktop)
    register_system_tools(mcp, desktop, default_language)
    register_web_tools(mcp)
