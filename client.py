import asyncio
import sys
import os
from typing import Dict, List, Optional, Literal
from contextlib import AsyncExitStack
from urllib.parse import urlparse

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

# Define available transport types
TransportType = Literal["stdio", "sse"]

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.servers: Dict[str, Dict] = {}  # Dictionary to store server connections
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def connect_to_server(self, server_name: str, server_script_path: str):
        """Connect to an MCP server and register it

        Args:
            server_name: A friendly name for the server
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))

        await session.initialize()

        # List available tools
        response = await session.list_tools()
        tools = response.tools
        
        self.servers[server_name] = {
            "session": session,
            "tools": tools,
            "path": server_script_path
        }
        
        print(f"\nConnected to server '{server_name}' with tools: {[tool.name for tool in tools]}")

    async def get_all_available_tools(self):
        """Get a list of all available tools across all servers"""
        all_tools = []
        for server_name, server_info in self.servers.items():
            for tool in server_info["tools"]:
                # Use underscore instead of colon to separate server and tool names
                tool_with_server = {
                    "name": f"{server_name}_{tool.name}",
                    "description": f"[From {server_name} server] {tool.description}",
                    "input_schema": tool.inputSchema
                }
                all_tools.append(tool_with_server)
        return all_tools

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        available_tools = await self.get_all_available_tools()

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        tool_results = []
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_with_server = content.name
                tool_args = content.input

                # Parse server name and tool name (now using underscore separator)
                try:
                    # Split on first underscore
                    parts = tool_with_server.split('_', 1)
                    if len(parts) != 2:
                        error_msg = f"Invalid tool format: {tool_with_server}. Expected format: 'server_tool'"
                        final_text.append(f"[Error: {error_msg}]")
                        continue
                        
                    server_name, tool_name = parts
                    if server_name not in self.servers:
                        error_msg = f"Server '{server_name}' not found. Available servers: {list(self.servers.keys())}"
                        final_text.append(f"[Error: {error_msg}]")
                        continue
                except ValueError:
                    error_msg = f"Invalid tool format: {tool_with_server}. Expected format: 'server_tool'"
                    final_text.append(f"[Error: {error_msg}]")
                    continue

                # Execute tool call on the appropriate server
                server_session = self.servers[server_name]["session"]
                try:
                    result = await server_session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[Calling tool {tool_name} on server {server_name} with args {tool_args}]")
                except Exception as e:
                    error_msg = f"Error calling tool {tool_name} on server {server_name}: {str(e)}"
                    final_text.append(f"[Error: {error_msg}]")
                    continue

                # Add the tool use to the message history
                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                
                # Add the tool result to the message history
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Multi-Server Client Started!")
        print(f"Connected servers: {list(self.servers.keys())}")
        print("Type your queries or 'quit' to exit.")
        print("Special commands:")
        print("  !servers - List all connected servers and their tools")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break
                    
                # Handle special commands
                if query.startswith('!servers'):
                    # List all connected servers and their tools
                    for server_name, server_info in self.servers.items():
                        tools = [tool.name for tool in server_info["tools"]]
                        print(f"\n{server_name} ({server_info['path']}):")
                        for tool in tools:
                            print(f"  - {tool}")
                    continue

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 3:
        print("Usage: python client.py server_name1:path_to_server1.py [server_name2:path_to_server2.py ...]")
        print("Example: python client.py weather:servers/weather_server.py calculator:servers/calculator_server.py")
        sys.exit(1)

    client = MCPClient()
    try:
        # Connect to all specified servers
        for server_arg in sys.argv[1:]:
            try:
                server_name, server_path = server_arg.split(':', 1)
                await client.connect_to_server(server_name, server_path)
            except ValueError:
                print(f"Invalid server specification: {server_arg}")
                print("Format should be 'server_name:path_to_server'")
                sys.exit(1)
                
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
