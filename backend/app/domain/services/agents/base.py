import json
import time
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from app.domain.external.llm import LLM
from app.domain.models.memory import Memory
from app.domain.services.tools.base import BaseTool
from app.domain.models.tool_result import ToolResult
from app.domain.models.event import (
    AgentEvent,
    ToolCallingEvent,
    ToolCalledEvent,
    ErrorEvent,
    MessageEvent,
)


class BaseAgent(ABC):
    """
    Base agent class, defining the basic behavior of the agent
    """

    system_prompt: str = ""
    format: Optional[str] = None
    max_iterations: int = 30
    max_retries: int = 3
    retry_interval: float = 1.0

    def __init__(self, memory: Memory, llm: LLM, tools: List[BaseTool] = []):
        self.memory = memory
        self.llm = llm
        self.memory.add_message({
            "role": "system", "content": self.system_prompt,
        })
        self.tools = tools
    
    def get_available_tools(self) -> Optional[List[Dict[str, Any]]]:
        """Get all available tools list"""
        available_tools = []
        for tool in self.tools:
            available_tools.extend(tool.get_tools())
        return available_tools
    
    def get_tool(self, function_name: str) -> BaseTool:
        """Get specified tool"""
        for tool in self.tools:
            if tool.has_function(function_name):
                return tool
        raise ValueError(f"Unknown tool: {function_name}")

    async def execute_tool(self, tool: BaseTool, function_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute specified tool, with retry mechanism"""

        retries = 0
        while retries <= self.max_retries:
            try:
                return await tool.invoke_function(function_name, **arguments)
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries <= self.max_retries:
                    await asyncio.sleep(self.retry_interval)
                else:
                    break
        
        raise ValueError(f"Tool execution failed, retried {self.max_retries} times: {last_error}")
    
    async def execute(self, request: str) -> AsyncGenerator[AgentEvent, None]:
        message = await self.ask(request, self.format)
        for _ in range(self.max_iterations):
            if not message.tool_calls:
                break
            tool_responses = []
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id
                
                tool = self.get_tool(function_name)

                # Generate event before tool call
                yield ToolCallingEvent(
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args
                )

                result = await self.execute_tool(tool, function_name, function_args)
                
                # Generate event after tool call
                yield ToolCalledEvent(
                    tool_name=tool.name,
                    function_name=function_name,
                    function_args=function_args,
                    function_result=result
                )

                tool_response = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result.model_dump_json()
                }
                tool_responses.append(tool_response)

            message = await self.ask_with_messages(tool_responses)
        else:
            yield ErrorEvent(error="Maximum iteration count reached, failed to complete the task")
        
        yield MessageEvent(message=message.content)
    
    async def ask_with_messages(self, messages: List[Dict[str, Any]], format: Optional[str] = None) -> Dict[str, Any]:
        self.memory.add_messages(messages)

        response_format = None
        if format:
            response_format = {"type": format}

        message = await self.llm.ask(self.memory.get_messages(), 
                                     tools=self.get_available_tools(), 
                                     response_format=response_format)
        if message.tool_calls:
            message.tool_calls = message.tool_calls[:1]
        self.memory.add_message(message)
        return message

    async def ask(self, request: str, format: Optional[str] = None) -> Dict[str, Any]:
        return await self.ask_with_messages([
            {
                "role": "user", "content": request
            }
        ], format)
    
    def roll_back(self):
        self.memory.roll_back()
