from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)
from typing import List
from dotenv import load_dotenv

load_dotenv()


class LanguageCortex_Online:
    def __init__(self):
        self.client = MultiServerMCPClient(
            {
                "rigel tools": {
                    "url": "http://localhost:8001/sse",
                    "transport": "sse",
                }
            },
        )
        self.model = ChatGroq(model="llama3-70b-8192")
        self.tools = None
        self.agent = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the tools and agent asynchronously"""
        if not self._initialized:
            self.tools = await self.client.get_tools()
            self.agent = create_react_agent(self.model, self.tools)
            self._initialized = True

    async def online_call(self, input_text: str, RAG: bool = False) -> str:
        # Ensure the agent is initialized before making a call
        if not self._initialized:
            await self.initialize()
        
        response = await self.agent.ainvoke({"messages": [HumanMessage(content=input_text)]})
        return response["messages"][-1].content