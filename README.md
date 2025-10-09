# Everly - Floating AI Assistant

A minimalist, floating desktop application that uses GPT-4o Vision to analyze screenshots and answer questions about what's on your screen.

## Features

- **Floating Window**: Small, frameless, always-on-top input bar
- **Screenshot Analysis**: Takes full screenshots and analyzes them with GPT-4o Vision
- **LangChain Integration**: Uses LangChain's agent framework with custom tools
- **Non-intrusive**: Results displayed in separate dialog window
- **Draggable**: Both input and result windows can be moved anywhere
- **Transparent Design**: Semi-transparent dark theme with rounded corners

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4o access
- macOS, Windows, or Linux

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/DoanAnhThi/Everly.git
   cd Everly
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   
   Create a `.env` file in the project directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   Replace `your_openai_api_key_here` with your actual OpenAI API key.

## Usage

1. **Run the application**:
   ```bash
   python main.py
   ```

2. **The floating input bar will appear** on your screen

3. **Type your question** in the input field and press Enter

4. **The app will**:
   - Take a screenshot of your current screen
   - Send the screenshot and your question to GPT-4o Vision
   - Show the AI response in a separate dialog window

5. **Move the windows** by clicking and dragging them anywhere on screen

6. **Close the app** by pressing the Escape key

## Example Questions

- "What's on my screen right now?"
- "Can you read the text in this document?"
- "What application is currently open?"
- "Describe the layout of this webpage"
- "What buttons or controls are visible?"

## Project Structure

```
├── main.py          # Application entry point
├── ui.py            # PySide6 UI components and floating windows
├── mcp_agent.py     # MCP client wrapper used by the UI/agent layer
├── mcp_server.py    # MCP server exposing screenshot, schedule, messaging tools
├── agent.py         # (Legacy) LangChain agent implementation
├── requirements.txt # Python dependencies
├── test_setup.py    # Setup verification script
├── env_template.txt # Environment variables template
└── README.md        # This file
```

## Technical Details

### Architecture

- **Modular Design**: Separated into UI, agent client, MCP server, and main modules
- **Threading**: Screenshot analysis runs in background thread to prevent UI freezing
- **MCP Integration**: The UI communicates with a local MCP server that exposes Everly tools
- **Vision API**: Leverages GPT-4o's vision capabilities for image analysis

### Key Components

- **FloatingWindow**: PySide6-based frameless, always-on-top input bar
- **ResultDialog**: Separate dialog for displaying AI analysis results
- **MCP Server (`mcp_server.py`)**: FastMCP server exposing screenshot analysis, scheduling, and messaging tools
- **MCP Client (`mcp_agent.py`)**: Lightweight wrapper connecting the UI to the MCP server
- **AnalysisThread**: QThread subclass for non-blocking AI analysis

### MCP Workflow Overview

1. `ui.py` receives user input and delegates processing to `floating_app_agent`.
2. `mcp_agent.py` connects to the stdio-based `mcp_server.py` using the MCP Python client.
3. The MCP server exposes three tools (`screenshot_analysis`, `schedule_workout`, `send_message_to_client`).
4. Tool results are returned as MCP `TextContent` blocks, converted to plain text for rendering in the UI.

### Dependencies

- **PySide6**: GUI framework for the floating windows
- **MCP (mcp)**: Model Context Protocol server/client toolkit powering the tools
- **OpenAI & openai-responses**: Communication with GPT-4o models via the Responses API
- **pyautogui**: Screenshot capture functionality
- **Pillow**: Image processing for screenshot handling
- **python-dotenv**: Environment variable management
- **LangChain** *(legacy)*: Kept for the previous agent implementation (`agent.py`)

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set"**:
   - Create a `.env` file with your OpenAI API key
   - Ensure the file is in the same directory as `main.py`

2. **"No module named 'PySide6'"**:
   - Install dependencies: `pip install -r requirements.txt`

3. **Screenshot permission errors** (macOS):
   - Go to System Preferences > Security & Privacy > Privacy > Screen Recording
   - Add your terminal application or Python to the allowed list

4. **API rate limits**:
   - The app uses GPT-4o Vision which may have rate limits
   - Consider upgrading your OpenAI plan if needed

### Testing Setup

Run the test script to verify everything is configured correctly:
```bash
python test_setup.py
```

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application. 