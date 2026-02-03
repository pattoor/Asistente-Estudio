# 🧠 Internal AI Assistant with Private Documents (RAG)

AI assistant designed to help teams quickly find information inside private documentation using Retrieval-Augmented Generation (RAG).

The system runs locally (offline-capable), preserves data privacy, and can be deployed as an internal service.

---

## 🚀 What problem does this solve?

Teams waste time:
- searching internal docs
- answering repetitive questions
- onboarding new members

This assistant:
- searches private documents semantically
- answers questions grounded only in internal data
- reduces time spent browsing documentation

---

## 🏗️ Architecture Overview

User → FastAPI API → RAG Pipeline  
- Document Loader  
- Text Splitter  
- Embeddings  
- Vector Database  
- Local LLM  

---

## 🧩 Tech Stack

- **Python**
- **FastAPI** – backend API
- **LangChain** – RAG orchestration
- **FAISS** – vector database
- **Ollama** – local LLM runtime
  - LLM: LLaMA / Mistral
  - Embeddings: nomic-embed-text
- **Docker** – containerized deployment

---

## 🔒 Privacy First

- No external APIs required
- Documents never leave the local environment
- Suitable for internal company data

---

## 📁 Project Structure

---

## ⚙️ How it works

1. Documents are loaded and split into chunks  
2. Chunks are converted into embeddings  
3. Embeddings are stored in a vector database  
4. User queries retrieve relevant chunks  
5. The LLM generates grounded answers  

---

## 📌 Use cases

- Internal documentation assistant
- Knowledge base search
- Onboarding support
- Technical Q&A for teams

---

## 🧪 Status

🚧 Work in progress  
Next steps:
- API endpoints
- Docker setup
- Agentic extension (LangGraph)

---

## 👤 Author. Patricio Romero

Built by an AI Engineer focused on:
- GenAI systems
- Agentic workflows
- Production-ready AI solutions
