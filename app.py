"""Gradio Web Interface for SmartBuyer Sidekick.
Run with: python app.py
"""

import html
import sys
import os

import gradio as gr

# Ensure local imports work — local styles.py takes priority over parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import styles
from smart_buyer import SmartBuyer

LAUNCH_STYLE = {"theme": styles.THEME, "css": styles.CSS, "head": styles.JS}

HEADER = """
<div id="header">
    <div class="badge"><span class="dot"></span> AI-POWERED DEAL INTELLIGENCE</div>
    <h1><span class="smart">Smart</span><span class="buyer">Buyer</span></h1>
    <div class="brand-bar"></div>
    <div class="tagline"><strong>Cut through fake reviews.</strong> Find real deals. Get the truth before you buy.</div>
</div>
"""


def render_todos(todos):
    if not todos:
        items = '<div class="placeholder">SmartBuyer will write its research plan here as it works</div>'
    else:
        items = "<ul>" + "".join(
            f'<li class="{todo["status"]}"><span class="mark"></span>{html.escape(todo["content"])}</li>'
            for todo in todos
        ) + "</ul>"
    return f"<h3>Research Plan</h3>{items}"


async def setup():
    smart_buyer = SmartBuyer()
    await smart_buyer.setup()
    return smart_buyer, gr.update(interactive=True)


async def process_message(smart_buyer, message, history):
    if smart_buyer is None:
        return history, gr.update(visible=False), smart_buyer
    # Use the default success criteria built into SmartBuyer
    results = await smart_buyer.run_turn(message, "", history)
    return results, gr.update(visible=smart_buyer.paused), smart_buyer


async def approve(smart_buyer, history):
    results = await smart_buyer.resume(history)
    return results, gr.update(visible=smart_buyer.paused), smart_buyer


def watch_todos(smart_buyer):
    return render_todos(smart_buyer.todos) if smart_buyer else render_todos([])


async def reset(smart_buyer):
    if smart_buyer:
        smart_buyer.cleanup()
    new_buyer = SmartBuyer()
    await new_buyer.setup()
    return "", None, gr.update(visible=False), new_buyer


def free_resources(smart_buyer):
    if smart_buyer:
        smart_buyer.cleanup()


with gr.Blocks(title="SmartBuyer") as ui:
    gr.HTML(HEADER)
    buyer_state = gr.State(delete_callback=free_resources)

    with gr.Row():
        chatbot = gr.Chatbot(label="SmartBuyer", height=340, scale=3, elem_id="chat")
        with gr.Column(scale=1):
            todos_panel = gr.HTML(render_todos([]), elem_id="plan-panel")

    with gr.Group(elem_id="ask-panel"):
        with gr.Row():
            message = gr.Textbox(
                show_label=False,
                placeholder="What product do you want to research? (e.g. Best wireless earbuds under $100)",
            )

    with gr.Row():
        reset_button = gr.Button("Reset", elem_id="reset-button")
        approve_button = gr.Button("Approve Push Notification", visible=False, elem_id="approve-button")
        go_button = gr.Button("🔍 Find Best Deals & Reviews!", elem_id="go-button", interactive=False)

    timer = gr.Timer(1)

    ui.load(setup, [], [buyer_state, go_button])
    timer.tick(watch_todos, [buyer_state], [todos_panel], show_progress="hidden")
    message.submit(
        process_message,
        [buyer_state, message, chatbot],
        [chatbot, approve_button, buyer_state],
    )
    go_button.click(
        process_message,
        [buyer_state, message, chatbot],
        [chatbot, approve_button, buyer_state],
    )
    approve_button.click(approve, [buyer_state, chatbot], [chatbot, approve_button, buyer_state])
    reset_button.click(reset, [buyer_state], [message, chatbot, approve_button, buyer_state])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    ui.launch(
        server_name="0.0.0.0",
        server_port=port,
        **LAUNCH_STYLE,
    )
