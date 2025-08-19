<div align="center">

  <h1>🪟 Windows-MCP-Agent</h1>

  <a href="https://github.com/CursorTouch/Windows-MCP/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.13%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/platform-Windows%207–11-blue" alt="Platform: Windows 7 to 11">
  <img src="https://img.shields.io/github/last-commit/CursorTouch/Windows-MCP" alt="Last Commit">
  <br>
  <a href="https://x.com/CursorTouch">
    <img src="https://img.shields.io/badge/follow-%40CursorTouch-1DA1F2?logo=twitter&style=flat" alt="Follow on Twitter">
  </a>
  <a href="https://discord.com/invite/Aue9Yj2VzS">
    <img src="https://img.shields.io/badge/Join%20on-Discord-5865F2?logo=discord&logoColor=white&style=flat" alt="Join us on Discord">
  </a>

</div>

<br>

Windows-MCP-Agent 是基于 Windows-MCP 的强大自动化代理智能体，在保留其核心特性的同时优化了项目结构，并提供更强的扩展能力。通过将 Windows 端工具统一整理为集合，并支持用户自定义扩展（如 Web 浏览器集成），它全面提升了大语言模型在 Windows 系统中的自动化 易用性、可扩展性与可维护性。

<br>
特别感谢开源项目 [Windows-MCP](https://github.com/CursorTouch/Windows-MCP) 与 [Windows-Use](https://github.com/CursorTouch/Windows-Use) 的支持！

## Updates

- 优化了项目结构
- 封装了工具与LLM之间的调用接口
- 拓展了工具的接口实现

### Supported Operating Systems
- Windows 7
- Windows 8, 8.1
- Windows 10
- Windows 11  

## 🎥 Demos
<https://github.com/user-attachments/assets/85de649b-f012-408f-ae0b-eecaeb043bc4>


## ✨ Key Features
- **对于Windows工具继承了Windows-MCP的所有特性**
Windows-MCP中windows工具作为Windows-MCP-Agent的一种类型工具集合,对其代码进行整理，并未修改。
- **可拓展式工具设计**
按照工具的类型进行工具集合的管理，用于自行拓展其他工具的实现。
- **支持任意 LLM(比如api调用、ollama等)**
相比于Windows-MCP的支持任意 LLM, 还是难以进行上手实现,Windows-MCP-Agent真正带通了tool与LLM的鸿沟，对其进行了封装简化，任意LLM都可用(支持api调用等任何形式)
- **丰富的 UI 自动化工具集**
包括Windows-MCP可用的所有Windows端工具集在内的所有，后续会持续更新的其他工具集。
- **轻量开源较少**
依赖最，易于部署，完整源代码遵循 MIT 协议开源。
- **可定制与可扩展**
用户可轻松调整或扩展工具，以满足独特的自动化或 AI 集成需求。

### Prerequisites
- Python 3.13+
- 支持任何LLM能够理解的语言，但在操作具体事项时，English作为默认语言(比如windows的具体应用名称等)


## 🏁 Getting Started

### 1.克隆项目

1. 克隆项目：`https://github.com/xskjya/Windows-MCP-Agent.git`，`cd Windows-MCP-Agent `.

2. 安装相关依赖：`pip install -r requirements.txt`.

3. 运行MCP服务器.注意：涉及到windows工具需要管理员运行

   `python server.py`

4. 运行MCP客户端.

   `python client.py`

---

## 🛠️MCP Tools

1. #### **Windows相关工具**
   - `Click-Tool`: Click on the screen at the given coordinates.
   - `Type-Tool`: Type text on an element (optionally clears existing text).
   - `Clipboard-Tool`: Copy or paste using the system clipboard.
   - `Scroll-Tool`: Scroll vertically or horizontally on the window or specific regions.
   - `Drag-Tool`: Drag from one point to another.
   - `Move-Tool`: Move mouse pointer.
   - `Shortcut-Tool`: Press keyboard shortcuts (`Ctrl+c`, `Alt+Tab`, etc).
   - `Key-Tool`: Press a single key.
   - `Wait-Tool`: Pause for a defined duration.
   - `State-Tool`: Combined snapshot of default language, browser, active apps and interactive, textual and scrollable elements along with screenshot of the desktop.
   - `Resize-Tool`: Used to change the window size or location of an app.
   - `Launch-Tool`: To launch an application from the start menu.
   - `Shell-Tool`: To execute PowerShell commands.
   - `Scrape-Tool`: To scrape the entire webpage for information.

2. 其他工具待补充.......

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=xskjya/Windows-MCP-Agent&type=Date)](https://www.star-history.com/#CursorTouch/Windows-MCP&Date)

## ⚠️Caution

*  Windows-MCP 会直接与您的 Windows 操作系统交互以执行操作。请谨慎使用，并避免在无法承受此类风险的环境中部署。

## 📝 Limitations

- Selecting specific sections of the text in a paragraph, as the MCP is relying on a11y tree. (⌛ Working on it.)
- `Type-Tool` is meant for typing text, not programming in IDE because of it types program as a whole in a file. (⌛ Working on it.)

## 🪪License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
