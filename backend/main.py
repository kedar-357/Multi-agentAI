from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import configure, GenerativeModel, ChatSession
from PyPDF2 import PdfReader
import io
import json
import re

GEMINI_API_KEY = "AIzaSyDL5m6vqOBYdND5q0wzdUraAwu4ek293JM"
configure(api_key=GEMINI_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


TARGET_KEYS = {"format", "intent", "sender", "urgency", "summary"}

# 🧠 In-memory categorized store
memory_store = {
    "pdf": [],
    "json": [],
    "text": []
}

def clean_gemini_response(text: str) -> str:
    return re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)

def classify_with_gemini(filename: str, content: str) -> str:
    model = GenerativeModel("gemini-1.5-flash")
    chat = ChatSession(model=model)

    system_message = (
        "You are a classification assistant that outputs a JSON object containing: "
        "format, intent, sender, urgency, and summary of the document."
    )
    chat.send_message(system_message)

    prompt = f"""
Filename: {filename}
Content:
\"\"\"
{content}
\"\"\"

Please provide ONLY a JSON object with these keys: format, intent, sender, urgency, summary.
"""
    response = chat.send_message(prompt)
    return response.text

def validate_json_schema(data: dict) -> dict:
    missing = list(TARGET_KEYS - data.keys())
    extra = list(data.keys() - TARGET_KEYS)
    result = {
        "valid": not missing,
        "missing_fields": missing,
        "extra_fields": extra,
        "structured": {k: data.get(k, "") for k in TARGET_KEYS}
    }
    return result

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content_bytes = await file.read()
    content_str = ""
    filename = file.filename

    if filename.endswith(".pdf"):
        try:
            pdf_reader = PdfReader(io.BytesIO(content_bytes))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    content_str += page_text + "\n"
        except Exception as e:
            return {"error": f"Failed to extract text from PDF: {str(e)}"}

        gemini_response = classify_with_gemini(filename, content_str)
        cleaned = clean_gemini_response(gemini_response)
        try:
            parsed = json.loads(cleaned)
            validated = validate_json_schema(parsed)
            memory_store["pdf"].append(validated["structured"])
            return {"result": validated}
        except Exception:
            return {"error": "Failed to parse Gemini response", "raw": gemini_response}

    elif filename.endswith(".json"):
        try:
            json_data = json.loads(content_bytes.decode("utf-8"))

            # Unwrap only if clearly structured result
            if (
                isinstance(json_data, dict)
                and "result" in json_data
                and isinstance(json_data["result"], dict)
                and set(json_data["result"].keys()) >= {"structured", "valid", "missing_fields", "extra_fields"}
            ):
                json_data = json_data["result"]["structured"]

            validated = validate_json_schema(json_data)
            memory_store["json"].append(validated["structured"])
            return {"result": validated}
        except Exception as e:
            return {"error": f"Failed to parse JSON: {str(e)}"}

    else:
        try:
            content_str = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            content_str = ""

        gemini_response = classify_with_gemini(filename, content_str)
        cleaned = clean_gemini_response(gemini_response)
        try:
            parsed = json.loads(cleaned)
            validated = validate_json_schema(parsed)
            memory_store["text"].append(validated["structured"])
            return {"result": validated}
        except Exception:
            return {"error": "Failed to parse Gemini response", "raw": gemini_response}

@app.get("/memory/")
def get_memory():
    return memory_store

