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

model = ChatGroq(model="llama3-70b-8192")


async def show_weather_response(agent, message: str):
    weather_response = await agent.ainvoke({"messages": [HumanMessage(content=message)]})
    for msg in weather_response["messages"]:
        if isinstance(msg, HumanMessage):
            print(f"HumanMessage: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"AIMessage: {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"ToolMessage: {msg.content}")


async def show_calculator_response(agent, message: str):
    calculator_response = await agent.ainvoke({"messages": [HumanMessage(content=message)]})
    for msg in calculator_response["messages"]:
        if isinstance(msg, HumanMessage):
            print(f"HumanMessage: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"AIMessage: {msg.content}")
        elif isinstance(msg, ToolMessage):
            print(f"ToolMessage: {msg.content}")


async def main():
    client = MultiServerMCPClient(
        {
            "calculator": {
                "url": "http://localhost:8001/sse",
                "transport": "sse",
            },
            "weather": {
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
        },
    )
    tools = await client.get_tools()
    agent = create_react_agent(model, tools)
    await show_weather_response(agent, "What is the meaning of life")
    await show_calculator_response(
        agent,
        "I need to calculate (2 + 2) / 4. First add 2 and 2, then divide that result by 4.",
    )


if __name__ == "__main__":
    asyncio.run(main())