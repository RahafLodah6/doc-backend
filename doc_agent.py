# doc_agent.py
import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.cohere import Cohere


load_dotenv()


agent = Agent(
    model=Cohere(id="command-a-03-2025", api_key=os.getenv("COHERE_API_KEY")),
    instructions=(
         "You are a professional document assistant. "
        "Follow the provided rules and policies carefully "
        "to generate well-structured and clear documents in Arabic. "
        "If an existing document is provided, edit only the requested part and keep the rest unchanged. "
        "Do not include any conversational sentences or questions like 'Would you like me to...'. "
        "Only return the document content itself."
    ),
)
