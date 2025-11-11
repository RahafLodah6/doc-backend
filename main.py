# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from doc_agent import agent



app = FastAPI()

# السماح للواجهة تتصل بالباك إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Backend is running!"}


# ======================================================
# 🔹 1. مسار إنشاء / تعديل المستند (قديم)
# ======================================================
class GenerateRequest(BaseModel):
    prompt: str
    rules: str

@app.post("/generate")
async def generate_doc(data: dict):
    prompt = f"""
    القواعد: {data.get('rules', '')}

    النص الحالي:
    {data.get('document_content', '')}

    التعليمات الجديدة:
    {data.get('prompt', '')}
    """
    response = agent.run(prompt)
    return {"response": response}


# ======================================================
# 🔹 2. مسار المحادثة الذكية الجديدة
# ======================================================

class ChatRequest(BaseModel):
    messages: list
    rules: str
    document: str
    document_title: str


# 🔹 دالة تحديد النية (chat / edit / unknown)
def detect_intent(message: str) -> str:
    message = message.strip().lower()
    chat_keywords = ["مرحبا", "اهلا", "السلام", "كيف", "شكرا", "تمام"]
    edit_keywords = ["عدل", "غير", "حدث", "اكتب", "انشئ", "اضف", "احذف", "فقرة", "خاتمة", "مقدمة"]

    if any(word in message for word in chat_keywords):
        return "chat"
    elif any(word in message for word in edit_keywords):
        return "edit"
    return "unknown"


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    هذا المسار للمحادثة التفاعلية.
    الإيجنت يفهم إذا المستخدم يريد التحدث أو تعديل المستند.
    """
    last_message = req.messages[-1]["content"]
    intent = detect_intent(last_message)

    # 🔹 إذا ما فهمنا النية، نطلب من الموديل يقرر
    if intent == "unknown":
        classification_prompt = f"""
        Analyze this user message and classify it as one of the following intents:
        - "chat": if it's casual conversation or greeting.
        - "edit": if it's asking to modify or generate document content.
        
        Message: "{last_message}"
        Return only one word: chat or edit.
        """
        intent_response = agent.run(classification_prompt)
        intent = str(intent_response.content).strip().lower()

    # 🔹 الرد حسب الحالة
    if intent == "chat":
    # 🔹 نحاول نحدد اللغة من آخر رسالة
     import re
     msg = last_message.strip()
     lang = "Arabic" if re.search(r"[\u0600-\u06FF]", msg) else "English"

     chat_prompt = f"""
    You are a friendly and intelligent assistant specialized in helping users with documents.
    The document title is "{req.document_title or 'current document'}".
    The user’s last message is written in {lang}.
    
    You MUST reply in the exact same language as the user's message.
    Never switch languages unless the user switches first.
    
    Keep your tone natural, warm, and human-like — as if you are having a real chat.
    Avoid repeating the document title unless necessary.
    
    User message:
    "{last_message}"
    """
     chat_response = agent.run(chat_prompt)
     return {"reply": chat_response.content, "document_update": None}



    elif intent == "edit":
     edit_prompt = f"""
   You are a skilled and creative document editor.
    Your task is to modify the provided text according to the user's request
    while strictly following the current rules and policies.

    --- القواعد والسياسات ---
    {req.rules or "لم يتم تحديد قواعد خاصة."}
    -----------------------------

    --- النص الحالي ---
    {req.document}

    --- طلب المستخدم ---
    {last_message}

     INSTRUCTIONS:
    - Modify **only** the parts that are requested.
    - Keep all unrelated sections unchanged.
    - Apply the above rules and policies in every sentence you write.
    - Maintain the same tone, style, or dialect specified in the rules.
    - Do not repeat instructions or add explanations.
    - Return only the **final edited document content**, nothing else.
    """

    response = agent.run(edit_prompt)
    reply = "تم تعديل المستند وفق القواعد المحددة."
    return {"reply": reply, "document_update": response.content}

