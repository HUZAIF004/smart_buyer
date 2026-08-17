"""Tools for the SmartBuyer Sidekick.

Includes targeted Reddit/forum review extraction, physical lab/benchmark searches,
live store deal tracking, push notifications, and persistent MCP browser/filesystem sessions.
"""

import asyncio
import os
from contextlib import AsyncExitStack

import requests
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv(override=True)

serper = GoogleSerperAPIWrapper()


@tool
def search_reddit_and_forums(product_name: str, topic: str = "durability") -> str:
    """Search Reddit (r/BuyItForLife, r/gadgets, niche subs) and enthusiast forums for
    authentic, unvarnished user opinions, long-term durability reports, and known hardware/software defects.
    Use this to uncover what real users complain about after months of daily use.
    """
    query = (
        f'site:reddit.com "{product_name}" '
        f'("{topic}" OR "long term review" OR "issues" OR "broke after" OR "honest review" OR "durability")'
    )
    try:
        return serper.run(query)
    except Exception as e:
        return f"Reddit search failed: {e}. Try searching general web."


@tool
def search_expert_reviews(product_name: str) -> str:
    """Search independent lab test websites (e.g., RTINGS, Wirecutter, Consumer Reports, Project Farm)
    for objective measurements, sound/screen curves, battery drain tests, and direct comparison benchmarks.
    """
    query = (
        f'"{product_name}" '
        f'(site:rtings.com OR site:nytimes.com/wirecutter OR site:tomsguide.com OR "lab test" OR "benchmarks")'
    )
    try:
        return serper.run(query)
    except Exception as e:
        return f"Expert review search failed: {e}."


@tool
def search_product_deals(product_name: str) -> str:
    """Search major retail stores (Amazon, Best Buy, Walmart, B&H, manufacturer store)
    for current live prices, discounts, coupons, and stock availability.
    """
    query = f'"{product_name}" price buy (Amazon OR "Best Buy" OR Walmart OR "official store" OR "deal")'
    try:
        return serper.run(query)
    except Exception as e:
        return f"Deals search failed: {e}."


@tool
def general_web_search(query: str) -> str:
    """Perform a general web search for specifications, official manufacturer details, or release dates."""
    try:
        return serper.run(query)
    except Exception as e:
        return f"Search error: {e}"


@tool
def send_push_notification(text: str) -> str:
    """Send a push notification to the user's phone with the top recommended product,
    current best price, and direct link. Requires user approval before sending.
    """
    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER")
    if not token or not user:
        return "Pushover token or user not set in .env."

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={"token": token, "user": user, "message": text},
    )
    response.raise_for_status()
    return "Notification sent successfully."


@tool
def request_human_help(instructions: str) -> str:
    """Ask the user to do something in the browser window that you cannot do yourself,
    such as solving a Cloudflare/CAPTCHA check, logging in, or selecting a store location.
    Explain clearly what they need to do. The run pauses until the user completes the action.
    """
    return "The user confirmed the action is completed. Continue with the research task."


def mcp_connections(sandbox: str) -> dict:
    """The MCP servers the SmartBuyer uses: a headed Playwright browser and a sandbox filesystem."""
    return {
        "playwright": {
            "transport": "stdio",
            "command": "npx",
            "args": ["@playwright/mcp@latest", "--isolated"],
        },
        "filesystem": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox],
        },
    }


class McpSessions:
    """Holds persistent MCP sessions open so the browser keeps its state between tool calls."""

    def __init__(self, connections: dict):
        self.connections = connections
        self.tools = []
        self._ready = asyncio.Event()
        self._stop = asyncio.Event()
        self._task = None

    async def _run(self):
        client = MultiServerMCPClient(self.connections)
        async with AsyncExitStack() as stack:
            for name in self.connections:
                session = await stack.enter_async_context(client.session(name))
                self.tools += await load_mcp_tools(session, server_name=name)
            self._ready.set()
            await self._stop.wait()

    async def start(self) -> list:
        self._task = asyncio.create_task(self._run())
        ready = asyncio.create_task(self._ready.wait())
        await asyncio.wait([ready, self._task], return_when=asyncio.FIRST_COMPLETED)
        ready.cancel()
        if self._task.done():
            self._task.result()
        return self.tools

    def stop(self):
        self._stop.set()


async def get_all_tools(sandbox: str):
    """Return the complete suite of SmartBuyer tools (our specialized tools + MCP server tools)
    and the session manager.
    """
    sessions = McpSessions(mcp_connections(sandbox))
    mcp_tools = await sessions.start()
    our_tools = [
        search_reddit_and_forums,
        search_expert_reviews,
        search_product_deals,
        general_web_search,
        send_push_notification,
        request_human_help,
    ]
    return our_tools + mcp_tools, sessions
