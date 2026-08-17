# 🛒 SmartBuyer — AI Deal Hunter & Review Authenticator

An autonomous product research agent that cuts through fake reviews, finds real user complaints from Reddit/forums, compares live store prices, and delivers an objective Buyer's Guide — all in under 2 minutes.

![Stack: LangChain + LangGraph](https://img.shields.io/badge/Stack-LangChain%20%2B%20LangGraph-209DD7?style=flat-square)

---

## ✨ Features

- **Reddit & Forum Mining** — Searches `r/BuyItForLife`, `r/gadgets`, and niche subs for honest 6-month durability reports and known defects
- **Expert Lab Data** — Cross-references RTINGS, Wirecutter, and Tom's Guide for objective benchmarks
- **Live Price Comparison** — Compares prices across Amazon, Best Buy, Walmart, and manufacturer stores
- **Browser Integration** — Uses a headed Playwright browser (via MCP) to inspect live product pages
- **Buyer's Guide Output** — Writes a structured `buyer_guide.md` with pros, cons, price table, and verdict to the sandbox
- **Push Notification** — Sends top recommendation + best price to your phone via Pushover
- **Evaluator Loop** — An LLM evaluator checks the guide's quality and sends feedback for up to 3 retry attempts
- **Live Research Plan** — Real-time todo list in the UI shows exactly what the agent is working on
- **Human-in-the-Loop** — Pauses for approval before sending push notifications or when it needs help (CAPTCHAs, logins)

---

## 🏗️ Architecture

```
User Query → LangGraph Worker (DeepSeek V4 Flash via OpenRouter)
                │
                ├── search_reddit_and_forums (Serper)
                ├── search_expert_reviews (Serper)
                ├── search_product_deals (Serper)
                ├── general_web_search (Serper)
                ├── Playwright Browser (MCP)
                ├── Filesystem (MCP → sandbox/)
                ├── send_push_notification (Pushover)
                └── request_human_help
                │
                ▼
          Evaluator (Structured Output)
                │
          [Pass] → Deliver Guide + Alert
          [Fail] → Feedback → Retry (up to 3x)
```

**Middleware Stack:**
| Middleware | Purpose |
|---|---|
| `TolerateToolErrors` | Catches browser/search failures gracefully |
| `TodoListMiddleware` | Powers the live research plan in the UI |
| `PIIMiddleware` | Redacts emails and credit card numbers |
| `ModelCallLimitMiddleware(30)` | Hard cap to keep costs under $0.01 |
| `HumanInTheLoopMiddleware` | Pauses on push notifications and human help requests |

---

## 📁 Project Structure

```
smart_buyer/
├── app.py                 # Gradio web interface
├── smart_buyer.py         # Core agent (Worker + Evaluator + advance/resume loop)
├── smart_buyer_tools.py   # Tools: search, browser, filesystem, push notifications
├── styles.py              # E-commerce dark theme (glassmorphism, animations)
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── sandbox/
    └── buyer_guide.md     # Generated output (Buyer's Guide)
```

---

## 🔑 Prerequisites

### API Keys (in `.env`)

```env
OPENROUTER_API_KEY=your_key       # Powers DeepSeek worker & evaluator
SERPER_API_KEY=your_key           # Google search for Reddit, reviews, prices
PUSHOVER_TOKEN=your_token         # Push notification delivery
PUSHOVER_USER=your_user_key       # Push notification recipient
```

### System Requirements

- **Python 3.11+**
- **Node.js 18+** and `npx` (for MCP servers — Playwright browser & filesystem)

---

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   npx playwright install
   ```

2. **Set up your `.env` file** with the API keys listed above.

3. **Run the app:**
   ```bash
   python app.py
   ```

4. **Open your browser** at `http://127.0.0.1:7860` and ask something like:
   > *"Best wireless noise-canceling headphones under $150"*

---

## 💰 Cost

| Component | Cost |
|---|---|
| DeepSeek V4 Flash (worker + evaluator) | ~$0.003–0.005 |
| Serper API (3–5 searches) | ~$0.001 |
| **Total per research run** | **~$0.005** |

---

## 📄 Sample Output

The agent produces a comprehensive `sandbox/buyer_guide.md` with:

- 🏆 **#1 Recommendation** with specs table
- 💰 **Budget Alternative** for cost-conscious buyers
- 🔴 **"What They Don't Tell You"** — real defects and durability issues from Reddit
- 📊 **Multi-store price comparison table** with direct links
- 💡 **Final verdict & buying advice**

---

## 🎨 UI Theme

Premium dark e-commerce storefront with:
- Animated gradient mesh background with floating glow orbs
- Glassmorphism cards with backdrop blur
- Animated CTA button with gradient shimmer
- Live-pulse research status indicators
- Custom scrollbar and micro-interactions

---

*Built with [LangChain](https://langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) + [Gradio](https://gradio.app/)*
