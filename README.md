# Local AI Assistant

A lightweight, single-file Python chatbot FRONTEND TEMPLATE using Gradio for frontend.

### Features
- GPT-style chat interface (local, no Flask needed)
- Upload and extract PDF context (this is enabled using an extra python script that uses pdfplumber for text extraction, no biggie)
- Auto-save/load/delete chats
- You can pretty much build any of your own apps and whatnot on top of this.
- Pure Python + Gradio = quick setup

### Getting Started

1) Setup ur project structure like this:

chatbot-template-gradio/
├── main.py                  # Single-file chatbot with UI + logic
├── pdf_reader.py            # PDF text extraction utility
├── API_Credentials.env      
├── requirements.txt
├── saved_chats/             # Auto-created for saved conversations
└── README.md                

2) Install requirements:
pip install -r requirements.txt

3) Setup ur API keys and stuff

4) Run it
   python main.py

python main.py
