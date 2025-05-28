# 🧠 Multi-Agent AI System

This project is a simple multi-agent AI orchestration system built with FastAPI and vanilla JS. It classifies and routes files (PDF, JSON, Email TXT) to specialized agents and stores results in shared memory.

## 🚀 Features

- Upload support for **PDF, JSON, and Email (TXT)**
- **Classifier Agent**:
  - Detects file format
  - Identifies intent (Invoice, RFQ, Complaint, etc.)
  - Routes to correct agent
- **Email Agent**:
  - Extracts sender, urgency, intent
- **JSON Agent**:
  - Validates schema, flags missing fields
- In-memory shared context for traceability
- Frontend file upload with results and memory display

## 🖼️ Demo

[Insert Loom/YouTube link here]

## 🧪 Sample Inputs

Sample files are available in `/sample_inputs`:
- `sample_invoice.pdf`
- `sample_rfq.json`
- `sample_email.txt`

## 📦 How to Run

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
