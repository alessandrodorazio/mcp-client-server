# MCP Client

This is a Model Context Protocol (MCP) client that allows you to interact with MCP servers, enabling Claude to use tools provided by these servers.

## Prerequisites

- Python 3.11 or higher
- An Anthropic API key (set in `.env` file)

## Setup

1. Clone this repository
2. Ensure you have the required dependencies installed:
   ```
   pip install anthropic mcp python-dotenv
   ```
   Or use uv:
   ```
   uv pip install anthropic mcp python-dotenv
   ```

3. Set up your Anthropic API key in a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the client by providing the path to an MCP server script:

```
python client.py path/to/server_script.py
```

The client supports both Python and JavaScript MCP servers:

```
python client.py path/to/server_script.js
```

## How It Works

1. The client connects to the specified MCP server
2. It retrieves available tools from the server
3. When you enter a query, it's sent to Claude along with tool descriptions
4. Claude decides which tools to use
5. The client executes tool calls through the server
6. Results are sent back to Claude for a final response

## Features

- Interactive command-line interface
- Support for both Python and Node.js MCP servers
- Proper resource management and error handling
- Seamless integration with Claude's tool-use capabilities

## Troubleshooting

- If you encounter connection issues, verify the server path and ensure the server is running
- The first response might take up to 30 seconds due to initialization
- For more detailed logs, check the server output

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Anthropic API Documentation](https://docs.anthropic.com)
