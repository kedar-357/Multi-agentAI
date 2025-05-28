import json

def handle_json(content):
    try:
        data = json.loads(content)
        missing_fields = []
        required_fields = ["invoice_id", "amount", "date"]

        for field in required_fields:
            if field not in data:
                missing_fields.append(field)

        return {
            "status": "success",
            "extracted": data,
            "missing_fields": missing_fields
        }
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON"}
