# doc-backend
# doc-backend
#  Official Letters Assistant – Backend

This project is the **backend service** of *Official Letters Assistant*, developed for **Labayh** platform.  
It is divided into **two independent servers** that must run separately:

---

##  Project Structure

- **`main.py`** → Runs the AI Agent server using **FastAPI** and **Agno**.  
- **`DOC_DB/`** → Contains the **database service** built with **Prisma + PostgreSQL**.  
- **`.env`** → Environment variables (database URL, API keys, etc.).

---

##  How to Run the Project

You must start **two servers**:  
one for the **Database (port 8000)** and another for the **AI Agent backend (port 8001)**.

---

### 1️ Run the Database Service
```bash
cd DOC_DB
pip install -r requirements.txt
prisma generate --schema ./prisma_data/schema.prisma
prisma db push
uvicorn main:app --reload --port 8000
