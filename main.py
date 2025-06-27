#install libraries

import os, json, shutil
import gradio as gr
from dotenv import load_dotenv
from openai import AzureOpenAI                  #Subjective, my LLM of choice is this, yours could be different
from pdf_reader import extract_text_from_pdf    #This ones the pdf_reading script I've provided in the repo

# Load env files and get ur keys
load_dotenv("C:/Users/hp/Desktop/API_details.env")

#______________API Key configuration varies as per provider, kindly check your own documentation before proceeding_________________________________________________
# Azure config
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT_NAME")
#__________________________________________________________________________________________________________________________________________________________________

# === File structure ===
SAVE_DIR = "saved_chats"
os.makedirs(SAVE_DIR, exist_ok=True)

# === Chat engine with PDF context ===
def chat(user_input, history, pdf_memory):
    history = history or []

    # Add context from PDF if available
    if pdf_memory:
        combined_input = f"The user uploaded a document. Use this context:\n\n{pdf_memory[:3000]}\n\nNow answer:\n{user_input}"
    else:
        combined_input = user_input

    history.append({"role": "user", "content": combined_input})
    #___________________________________________________________ Again, this is subjective ______________________________________________________________________
    response = client.chat.completions.create(
        model=AZURE_DEPLOYMENT,
        messages=[{"role": "system", "content": "You are a helpful assistant."}, *history]
    )
    #____________________________________________________________________________________________________________________________________________________________
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})

    gr_history = [(h["content"], history[i+1]["content"]) for i, h in enumerate(history) if h["role"] == "user"]
    return gr_history, history

# === File management ===
def get_chat_folder(title):
    return os.path.join(SAVE_DIR, title)

def get_json_path(title):
    return os.path.join(get_chat_folder(title), f"{title}.json")

def list_saved_chats():
    return sorted([
        folder for folder in os.listdir(SAVE_DIR)
        if os.path.isdir(os.path.join(SAVE_DIR, folder)) and os.path.isfile(get_json_path(folder))
    ])

def save_chat(title, history):
    folder = get_chat_folder(title)
    os.makedirs(folder, exist_ok=True)
    with open(get_json_path(title), "w") as f:
        json.dump({"title": title, "history": history}, f)

def load_chat(title):
    with open(get_json_path(title), "r") as f:
        return json.load(f)["history"]

def delete_chat(title):
    folder = get_chat_folder(title)
    if os.path.exists(folder):
        shutil.rmtree(folder)

# === PDF upload handler ===
def handle_pdf_upload(file, title):
    if not title:
        return "⚠️ Please name your chat first.", ""

    folder = get_chat_folder(title)
    upload_dir = os.path.join(folder, "user_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    saved_path = os.path.join(upload_dir, file.name)
    shutil.copy(file.name, saved_path)

    try:
        extracted_text = extract_text_from_pdf(saved_path)
        return f"✅ Uploaded and extracted {file.name}", extracted_text
    except Exception as e:
        return f"❌ Error reading PDF: {str(e)}", ""

# === UI ===
with gr.Blocks() as demo:
    gr.Markdown("## Local - PDF-Aware Saveable Chat")

    state = gr.State([])          # Chat history
    current_chat = gr.State("")   # Chat name
    pdf_memory = gr.State("")     # Stored PDF content

    with gr.Row():
        with gr.Column(scale=1):
            chat_list = gr.Radio(choices=list_saved_chats(), label=" Saved Chats ", interactive=True)
            new_chat_name = gr.Textbox(placeholder="Name this chat", label=" New Chat")
            save_btn = gr.Button(" Save Chat")
            delete_btn = gr.Button(" Delete Chat")
        with gr.Column(scale=4):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Type your message")
            file_input = gr.File(label=" Upload PDF", file_types=[".pdf"])
            upload_btn = gr.Button(" Process PDF")
            upload_status = gr.Markdown()
            clear = gr.Button(" New Chat")

    # Submit message
    msg.submit(chat, [msg, state, pdf_memory], [chatbot, state])

    # Save button
    def save_and_refresh(name, history):
        if name:
            save_chat(name, history)
        return gr.update(choices=list_saved_chats(), value=name)

    save_btn.click(save_and_refresh, inputs=[new_chat_name, state], outputs=[chat_list])

    # Load chat
    def load_and_set(chatname):
        if chatname:
            hist = load_chat(chatname)
            ui_hist = [(h["content"], hist[i+1]["content"]) for i, h in enumerate(hist) if h["role"] == "user"]
            return ui_hist, hist, chatname, ""
        return [], [], "", ""

    chat_list.change(load_and_set, inputs=chat_list, outputs=[chatbot, state, current_chat, pdf_memory])

    # Delete
    delete_btn.click(lambda t: delete_chat(t) or ([], [], "", "", gr.update(choices=list_saved_chats(), value=None)),
                     inputs=[chat_list],
                     outputs=[chatbot, state, current_chat, pdf_memory, chat_list])

    # Clear
    clear.click(lambda: ([], [], "", ""), None, outputs=[chatbot, state, current_chat, pdf_memory])

    # PDF Upload
    upload_btn.click(fn=handle_pdf_upload,
                     inputs=[file_input, current_chat],
                     outputs=[upload_status, pdf_memory])

demo.launch()
