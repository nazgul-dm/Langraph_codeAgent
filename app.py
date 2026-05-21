import gradio as gr
from codeAgent import CodeAgent


async def setup():
    codeAgent = CodeAgent()
    await codeAgent.setup()
    return codeAgent


async def process_message(codeAgent, message, history):
    results = await codeAgent.run_superstep(message, history)
    return results, codeAgent


async def reset():
    new_codeAgent = CodeAgent()
    await new_codeAgent.setup()
    return "", "", None, new_codeAgent


def free_resources(codeAgent):
    print("Cleaning up")
    try:
        if codeAgent:
            codeAgent.cleanup()
    except Exception as e:
        print(f"Exception during cleanup: {e}")


with gr.Blocks(title="CodeAgent", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Personal Code Agent")
    codeAgent = gr.State(delete_callback=free_resources)

    with gr.Row():
        chatbot = gr.Chatbot(label="Code Agent", height=300, type="messages")
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the code agent")
        
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")

    ui.load(setup, [], [codeAgent])
    message.submit(
        process_message, [codeAgent, message, chatbot], [chatbot, codeAgent]
    )
    go_button.click(
        process_message, [codeAgent, message, chatbot], [chatbot, codeAgent]
    )
    reset_button.click(reset, [], [message, chatbot, codeAgent])


ui.launch(inbrowser=True)
