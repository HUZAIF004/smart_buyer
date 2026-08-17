"""The SmartBuyer Sidekick: An autonomous deal hunter & review authenticator.

Researches authentic product feedback across Reddit and specialist forums,
cross-references lab benchmark data, compares live retail store pricing,
writes a structured buyer's guide to the sandbox, and sends a push alert.
"""

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    PIIMiddleware,
    TodoListMiddleware,
)
from langchain_core.messages import ToolMessage
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import BaseModel, Field

from smart_buyer_tools import get_all_tools

load_dotenv(override=True)

HERE = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(HERE, "sandbox")
MAX_ATTEMPTS = 3


class EvaluatorOutput(BaseModel):
    feedback: str = Field(description="Feedback on the assistant's buyer guide and research quality")
    success_criteria_met: bool = Field(description="Whether the success criteria have been fully met")
    user_input_needed: bool = Field(
        description="True if the assistant has a clarifying question or is stuck and needs human input"
    )


SMART_BUYER_PROMPT = """You are SmartBuyer, an objective product research assistant and deal hunter.
Your mission is to help the user make the smartest purchasing decision by cutting through fake reviews,
finding hidden product flaws from real owners on Reddit/forums, comparing live store prices, and saving
a comprehensive Buyer's Guide to buyer_guide.md in the sandbox.

Key Guidelines:
1. Research Authenticity: Use `search_reddit_and_forums` to uncover unvarnished opinions, 6-month durability
   reports, and common defect patterns on Reddit (r/BuyItForLife, r/gadgets, niche subs).
2. Expert Data: Use `search_expert_reviews` to check independent lab tests (RTINGS, Wirecutter, Project Farm)
   for physical measurements and benchmark ratings.
3. Live Deals & Prices: Use `search_product_deals` and the browser to compare prices across stores (Amazon,
   Best Buy, Walmart, manufacturer site) and look for active discounts/coupons.
4. Browser Usage: When you use the browser, navigate directly to product pages, dismiss banners yourself,
   and take a snapshot to inspect pricing. If blocked by a CAPTCHA or 2FA, use `request_human_help`.
5. Deliverable: Always write a complete Markdown report to `buyer_guide.md` in the sandbox with:
   - Top #1 Recommendation & Best Budget Alternative
   - "What They Don't Tell You" (real known issues & durability flaws from Reddit)
   - Multi-store price comparison table with links
   - Clear final buying verdict
6. Notification: Send a push notification with your top recommended pick and its best live price.
7. Keep working until the success criteria are met, then clearly summarize what you found."""


class TolerateToolErrors(AgentMiddleware):
    """Hand tool failures back to the model as a message so it can recover, rather than
    crashing the run. Tools that touch the outside world, like a browser or web search, fail now and then."""

    async def awrap_tool_call(self, request, handler):
        try:
            return await handler(request)
        except Exception as error:
            return ToolMessage(
                content=f"That tool call failed: {error}. Try another approach.",
                tool_call_id=request.tool_call["id"],
            )


class SmartBuyer:
    def __init__(self):
        self.sidekick_id = str(uuid.uuid4())
        self.memory = InMemorySaver()
        self.tools = None
        self.sessions = None
        self.worker = None
        self.evaluator = None
        self.task = ""
        self.success_criteria = ""
        self.attempts = 0
        self.paused = False
        self.pending_actions = 0
        self.todos = []

    async def setup(self):
        os.makedirs(SANDBOX, exist_ok=True)
        self.tools, self.sessions = await get_all_tools(SANDBOX)
        self.worker = create_agent(
            model="openrouter:deepseek/deepseek-v4-flash",
            tools=self.tools,
            system_prompt=f"{SMART_BUYER_PROMPT}\nToday is {datetime.now():%A %d %B %Y}.",
            middleware=[
                TolerateToolErrors(),
                TodoListMiddleware(),
                PIIMiddleware("email"),
                PIIMiddleware("credit_card", apply_to_tool_results=True),
                ModelCallLimitMiddleware(run_limit=30),
                HumanInTheLoopMiddleware(
                    interrupt_on={"send_push_notification": True, "request_human_help": True}
                ),
            ],
            checkpointer=self.memory,
        )
        self.evaluator = ChatOpenRouter(model="deepseek/deepseek-v4-flash").with_structured_output(EvaluatorOutput)

    async def evaluate(
        self, message: str, success_criteria: str, last_reply: str, tools_used: list[str]
    ) -> EvaluatorOutput:
        prompt = f"""You decide whether the SmartBuyer assistant has met the success criteria for a product research task.

User request:
{message}

Success criteria:
{success_criteria}

Tools called during execution:
{", ".join(tools_used) or "none"}

Assistant's reply:
{last_reply}

Decide whether the criteria are met, using the tool calls and evidence of what was saved to the sandbox.
Ensure that:
1. Real user feedback (Reddit/forums/expert reviews) was consulted.
2. Honest product drawbacks or durability caveats are included.
3. Live price comparison is present.
Give brief, concrete feedback."""
        return await self.evaluator.ainvoke(prompt)

    async def run_turn(self, message: str, success_criteria: str, history: list) -> list:
        """One turn of conversation: the worker attempts the research task and the evaluator checks it,
        retrying with feedback up to MAX_ATTEMPTS. If the worker pauses for approval, this
        returns straight away with paused set, and resume() continues the same turn."""
        self.task = message
        self.success_criteria = success_criteria or (
            "buyer_guide.md is written in the sandbox with honest pros/cons, Reddit findings, "
            "a price comparison table, and a push notification was sent with the top recommendation."
        )
        self.attempts = 0
        self.todos = []
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": f"{message}\n\nThe success criteria for this task are: {self.success_criteria}",
                }
            ]
        }
        return await self._advance(payload, history + [{"role": "user", "content": message}])

    async def resume(self, history: list) -> list:
        """Approve the actions the worker paused on (e.g. sending the push notification), and continue."""
        payload = Command(resume={"decisions": [{"type": "approve"}] * self.pending_actions})
        return await self._advance(payload, history)

    async def _advance(self, payload, history: list) -> list:
        config = {"configurable": {"thread_id": self.sidekick_id}}
        while True:
            result = None
            async for result in self.worker.astream(payload, config=config, stream_mode="values"):
                self.todos = result.get("todos", self.todos)

            if "__interrupt__" in result:
                actions = result["__interrupt__"][0].value["action_requests"]
                self.paused = True
                self.pending_actions = len(actions)
                described = "\n".join(action["description"] for action in actions)
                return history + [{"role": "assistant", "content": f"Waiting for your approval:\n{described}"}]

            self.paused = False
            reply = result["messages"][-1].content
            tools_used = [
                call["name"] for m in result["messages"] for call in (getattr(m, "tool_calls", None) or [])
            ]
            self.attempts += 1
            verdict = await self.evaluate(self.task, self.success_criteria, reply, tools_used)
            if verdict.success_criteria_met or verdict.user_input_needed or self.attempts >= MAX_ATTEMPTS:
                return history + [
                    {"role": "assistant", "content": reply},
                    {"role": "assistant", "content": f"Evaluator: {verdict.feedback}"},
                ]
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Your last response did not meet the success criteria. "
                        f"Here is the feedback: {verdict.feedback}. Please keep working and address it.",
                    }
                ]
            }

    def cleanup(self):
        """Shut down the persistent MCP servers; the browser closes cleanly."""
        if self.sessions:
            self.sessions.stop()
