import asyncio
from concurrent.futures import TimeoutError
from fastmcp import Client
from google.adk.tools import FunctionTool
from google.adk.agents import LlmAgent


async def fetch_faq_from_mcp_async(query: str) -> str:
    try:
        async with Client("faq_mcp_server.py") as client:
            faqs = await client.get_resource("faq://all")

            for faq in faqs:
                if query.lower() in faq["question"].lower():
                    return f"{faq['answer']}\n(Source: NuGenomics FAQ)"

            return "Sorry, I can only answer questions from the official NuGenomics FAQ."

    except Exception as e:
        # Handle any connection or retrieval issues
        return f"Error connecting to FAQ MCP server: {e}"


def fetch_faq_from_mcp(query: str) -> str:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(fetch_faq_from_mcp_async(query))
    else:
        future = asyncio.run_coroutine_threadsafe(fetch_faq_from_mcp_async(query), loop)
        try:
            return future.result(timeout=10)  # Wait up to 10 seconds for completion
        except TimeoutError:
            return "FAQ retrieval timed out. Please try again."
        except Exception as e:
            return f"Error while fetching FAQ: {e}"


faq_tool = FunctionTool(fetch_faq_from_mcp)


nugen_agent = LlmAgent(
    name="nugen_agent",
    model="gemini-2.5-flash",
    description="Answers only NuGenomics-related questions using the external FAQ MCP server.",
    instruction=(
        "You are the official NuGenomics support assistant.\n"
        "Use only the FAQ data served via the MCP FAQ service.\n"
        "If the answer isn't found, say: "
        "'Sorry, I can only answer questions from the official NuGenomics FAQ.'"
    ),
    tools=[faq_tool],
)
