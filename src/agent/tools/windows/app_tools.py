
def register_app_tools(mcp, desktop, default_language):
    @mcp.tool(name='Launch-Tool',
              description='Launch an application from the Windows Start Menu by name (e.g., "notepad", "calculator", "chrome")')
    def launch_tool(name: str) -> str:
        """
        启动指定应用程序（通过开始菜单搜索并打开）
        :param name: 应用程序的名字（支持英文和系统默认语言）
        :return: 启动结果提示字符串
        """
        response, status = desktop.launch_app(name)
        if status != 0:
            return f'Failed to launch {name.title()}. Try to use the app name in the default language ({default_language}).'
        else:
            return response

    @mcp.tool(name='Switch-Tool',description='Switch to a specific application window (e.g., "notepad", "calculator", "chrome", etc.) and bring to foreground.')
    def switch_tool(name: str) -> str:
        """
        切换到指定应用程序窗口并置顶
        :param name: 应用程序名
        :return: 操作结果提示
        """
        response, status = desktop.switch_app(name)
        if status != 0:
            return f'Failed to switch to {name.title()} window. Try to use the app name in the default language ({default_language}).'
        else:
            return response

    @mcp.tool(name='Resize-Tool', description='Resize or move a specific application window.')
    def resize_tool(name: str, size: list[int] = None, loc: list[int] = None) -> str:
        """
        调整应用程序窗口的大小或位置
        :param name: 应用程序名
        :param size: [width, height] 窗口大小
        :param loc: [x, y] 窗口位置
        :return: 操作结果提示
        """
        if size is not None and len(size) != 2:
            raise ValueError("Size must be a list of exactly 2 integers [width, height]")
        if loc is not None and len(loc) != 2:
            raise ValueError("Location must be a list of exactly 2 integers [x, y]")

        size_tuple = tuple(size) if size is not None else None
        loc_tuple = tuple(loc) if loc is not None else None

        response, status = desktop.resize_app(name, size_tuple, loc_tuple)
        if status != 0:
            return f'Failed to resize {name.title()} window. Try to use the app name in the default language ({default_language}).'
        else:
            return response


