from agents.json_agent import handle_json
from agents.email_agent import handle_email
from memory.memory_store import memory
import json

def classify_and_route(filename, content):
    # Determine file type
    if filename.endswith(".json"):
        file_type = "JSON"
        intent = "Invoice" if b"invoice" in content.lower() else "Unknown"
        result = handle_json(content)
    elif filename.endswith(".txt"):
        file_type = "Email"
        intent = "Complaint" if b"complaint" in content.lower() else "RFQ"
        result = handle_email(content)
    elif filename.endswith(".pdf"):
        file_type = "PDF"
        intent = "Regulation"  # placeholder
        result = {"message": "PDF support not implemented yet"}
    else:
        return {"error": "Unsupported file type"}

    log = {
        "filename": filename,
        "type": file_type,
        "intent": intent,
        "result": result,
    }
    memory.append(log)
    return result
