from platform import system, release
from textwrap import dedent
from typing import Literal
import uiautomation as ua
import pyperclip as pc
import pyautogui as pg

pg.FAILSAFE = False
pg.PAUSE = 1.0

os = system()
version = release()

instructions = dedent(f'''
Windows MCP server provides tools to interact directly with the {os} {version} desktop, 
thus enabling to operate the desktop on the user's behalf.
''')


def register_system_tools(mcp, desktop, default_language):
    @mcp.tool(name='Clipboard-Tool', description='Copy text to clipboard or retrieve current clipboard content.')
    def clipboard_tool(mode: Literal['copy', 'paste'], text: str = None) -> str:
        """
        操作系统剪贴板
        :param mode: 'copy' 表示复制文本到剪贴板, 'paste' 表示读取剪贴板内容
        :param text: 在 copy 模式下要复制的文本
        :return: 操作结果提示
        """
        if mode == 'copy':
            if text:
                pc.copy(text)
                return f'Copied "{text}" to clipboard'
            else:
                raise ValueError("No text provided to copy")
        elif mode == 'paste':
            clipboard_content = pc.paste()
            return f'Clipboard Content: "{clipboard_content}"'
        else:
            raise ValueError('Invalid mode. Use "copy" or "paste".')

    @mcp.tool(name='Move-Tool',description='Move mouse cursor to specific coordinates without clicking. Useful for hovering over elements or positioning cursor before other actions.')
    def move_tool(to_loc: list[int]) -> str:
        """
        移动鼠标光标到指定坐标（不点击）
        :param to_loc: [x, y] 目标坐标
        :return: 操作结果提示
        """
        if len(to_loc) != 2:
            raise ValueError("to_loc must be a list of exactly 2 integers [x, y]")
        x, y = to_loc[0], to_loc[1]
        pg.moveTo(x, y)
        return f'Moved the mouse pointer to ({x},{y}).'

    @mcp.tool(name='Shortcut-Tool',description='Execute keyboard shortcuts using key combinations. Pass keys as list (e.g., ["ctrl", "c"] for copy, ["alt", "tab"] for app switching, ["win", "r"] for Run dialog).')
    def shortcut_tool(shortcut: list[str]):
        """
        执行快捷键组合
        :param shortcut: 键位列表，例如 ["ctrl","c"] 或 ["alt","tab"]
        :return: 操作结果提示
        """
        pg.hotkey(*shortcut)
        return f"Pressed {'+'.join(shortcut)}."

    @mcp.tool(name='Powershell-Tool', description='Execute PowerShell commands and return the output with status code')
    def powershell_tool(command: str) -> str:
        """
        执行 PowerShell 命令并返回执行结果
        :param command: PowerShell 命令字符串
        :return: 状态码和响应输出
        """
        response, status = desktop.execute_command(command)
        return f'Status Code: {status}\nResponse: {response}'

    @mcp.tool(name='State-Tool',
              description='Capture comprehensive desktop state including default language used by user interface, focused/opened applications, interactive UI elements (buttons, text fields, menus), informative content (text, labels, status), and scrollable areas. Optionally includes visual screenshot when use_vision=True. Essential for understanding current desktop context and available UI interactions.')
    def state_tool(use_vision: bool = False) -> dict:
        """
        获取桌面状态，包括：
          - 默认语言
          - 当前聚焦应用
          - 打开的应用列表
          - 可交互元素（按钮、输入框等）
          - 信息性元素（文本、状态标签等）
          - 可滚动区域
        可选：返回桌面截图 (base64)
        :param use_vision: 是否包含截图
        :return: 包含桌面状态的 dict
        """
        desktop_state = desktop.get_state(use_vision=use_vision)
        interactive_elements = desktop_state.tree_state.interactive_elements_to_string()
        informative_elements = desktop_state.tree_state.informative_elements_to_string()
        scrollable_elements = desktop_state.tree_state.scrollable_elements_to_string()
        apps = desktop_state.apps_to_string()
        active_app = desktop_state.active_app_to_string()

        text_output = dedent(f'''
        Default Language of User Interface:
        {default_language}

        Focused App:
        {active_app}

        Opened Apps:
        {apps}

        List of Interactive Elements:
        {interactive_elements or 'No interactive elements found.'}

        List of Informative Elements:
        {informative_elements or 'No informative elements found.'}

        List of Scrollable Elements:
        {scrollable_elements or 'No scrollable elements found.'}
        ''')

        result = {"text": text_output}

        # 如果需要截图，附加 base64 编码图像
        if use_vision:
            import base64
            screenshot_bytes = desktop_state.screenshot
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            result["screenshot"] = screenshot_b64

        return result

    @mcp.tool(name='Scroll-Tool',description='Scroll at specific coordinates or current mouse position. Use wheel_times to control scroll amount (1 wheel = ~3-5 lines). Essential for navigating lists, web pages, and long content.')
    def scroll_tool(loc: list[int] = None, type: Literal['horizontal', 'vertical'] = 'vertical',
                    direction: Literal['up', 'down', 'left', 'right'] = 'down', wheel_times: int = 1) -> str:
        """
        在指定坐标或当前位置滚动页面
        :param loc: [x, y] 坐标（可选）
        :param type: 滚动方向类型（horizontal/vertical）
        :param direction: 具体方向（up/down/left/right）
        :param wheel_times: 滚动次数
        :return: 操作结果提示
        """
        if loc:
            if len(loc) != 2:
                raise ValueError("Location must be a list of exactly 2 integers [x, y]")
            x, y = loc[0], loc[1]
            pg.moveTo(x, y)

        match type:
            case 'vertical':
                match direction:
                    case 'up':
                        ua.WheelUp(wheel_times)
                    case 'down':
                        ua.WheelDown(wheel_times)
                    case _:
                        return 'Invalid direction. Use "up" or "down".'
            case 'horizontal':
                match direction:
                    case 'left':
                        pg.keyDown('Shift');
                        pg.sleep(0.05)
                        ua.WheelUp(wheel_times)
                        pg.sleep(0.05);
                        pg.keyUp('Shift')
                    case 'right':
                        pg.keyDown('Shift');
                        pg.sleep(0.05)
                        ua.WheelDown(wheel_times)
                        pg.sleep(0.05);
                        pg.keyUp('Shift')
                    case _:
                        return 'Invalid direction. Use "left" or "right".'
            case _:
                return 'Invalid type. Use "horizontal" or "vertical".'
        return f'Scrolled {type} {direction} by {wheel_times} wheel times.'

    @mcp.tool(name='Key-Tool',description='Press individual keyboard keys. Supports special keys like "enter", "escape", "tab", "space", "backspace", "delete", arrow keys ("up", "down", "left", "right"), function keys ("f1"-"f12").')
    def key_tool(key: str = '') -> str:
        """
        按下单个按键
        :param key: 键位名，例如 "enter","escape","tab"
        :return: 操作结果提示
        """
        pg.press(key)
        return f'Pressed the key {key}.'

    @mcp.tool(name='Click-Tool', description='Click on UI elements at specific coordinates.')
    def click_tool(loc: list[int], button: Literal['left', 'right', 'middle'] = 'left', clicks: int = 1) -> str:
        """
        在指定屏幕坐标点击鼠标
        :param loc: [x, y] 坐标
        :param button: 鼠标按钮类型（左/右/中）
        :param clicks: 点击次数（1/2/3）
        :return: 操作结果提示
        """
        if len(loc) != 2:
            raise ValueError("Location must be a list of exactly 2 integers [x, y]")
        x, y = loc[0], loc[1]
        pg.moveTo(x, y)
        control = desktop.get_element_under_cursor()
        parent_control = control.GetParentControl()

        # 判断是否直接在桌面上点击
        if parent_control.Name == "Desktop":
            pg.click(x=x, y=y, button=button, clicks=clicks)
        else:
            pg.mouseDown()
            pg.click(button=button, clicks=clicks)
            pg.mouseUp()

        num_clicks = {1: 'Single', 2: 'Double', 3: 'Triple'}
        return f'{num_clicks.get(clicks)} {button} Clicked on {control.Name} Element with ControlType {control.ControlTypeName} at ({x},{y}).'

    @mcp.tool(name='Drag-Tool',
              description='Drag and drop operation from source coordinates to destination coordinates. Useful for moving files, resizing windows, or drag-and-drop interactions.')
    def drag_tool(from_loc: list[int], to_loc: list[int]) -> str:
        if len(from_loc) != 2:
            raise ValueError("from_loc must be a list of exactly 2 integers [x, y]")
        if len(to_loc) != 2:
            raise ValueError("to_loc must be a list of exactly 2 integers [x, y]")
        x1, y1 = from_loc[0], from_loc[1]
        x2, y2 = to_loc[0], to_loc[1]
        pg.drag(x1, y1, x2, y2, duration=0.5)
        control = desktop.get_element_under_cursor()
        return f'Dragged {control.Name} element with ControlType {control.ControlTypeName} from ({x1},{y1}) to ({x2},{y2}).'

    @mcp.tool(name='Wait-Tool',
              description='Pause execution for specified duration in seconds. Useful for waiting for applications to load, animations to complete, or adding delays between actions.')
    def wait_tool(duration: int) -> str:
        pg.sleep(duration)
        return f'Waited for {duration} seconds.'