import pyautogui as pg


pg.FAILSAFE = False
pg.PAUSE = 1.0

def register_input_tools(mcp, desktop):
    @mcp.tool(name='Type-Tool', description='Type text into input fields.')
    def type_tool(loc: list[int], text: str, clear: bool = False, press_enter: bool = False) -> str:
        """
        在指定输入框或焦点位置输入文字
        :param loc: [x, y] 坐标
        :param text: 要输入的文字
        :param clear: True 清空原有文本, False 追加输入
        :param press_enter: 是否在输入后按下回车
        :return: 操作结果提示
        """
        if len(loc) != 2:
            raise ValueError("Location must be a list of exactly 2 integers [x, y]")
        x, y = loc[0], loc[1]
        pg.click(x=x, y=y)
        control = desktop.get_element_under_cursor()
        if clear == 'True':
            pg.hotkey('ctrl', 'a')
            pg.press('backspace')
        pg.typewrite(text, interval=0.1)
        if press_enter:
            pg.press('enter')
        return f'Typed {text} on {control.Name} Element with ControlType {control.ControlTypeName} at ({x},{y}).'

