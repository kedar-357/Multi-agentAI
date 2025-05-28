import re

def handle_email(content):
    content_str = content.decode("utf-8").lower()

    # Extract sender using regex
    sender_match = re.search(r'from:\s*([\w\.-]+@[\w\.-]+)', content_str)
    sender = sender_match.group(1) if sender_match else "unknown@domain.com"

    # Intent detection
    if "rfq" in content_str or "quotation" in content_str or "quote" in content_str:
        intent = "RFQ"
    elif "complaint" in content_str or "not satisfied" in content_str or "issue" in content_str:
        intent = "Complaint"
    elif "invoice" in content_str or "billing" in content_str:
        intent = "Invoice"
    elif "regulation" in content_str or "compliance" in content_str:
        intent = "Regulation"
    else:
        intent = "General Inquiry"

    # Urgency detection
    if any(word in content_str for word in ["urgent", "asap", "immediately"]):
        urgency = "high"
    else:
        urgency = "normal"

    # Return structured response
    return {
        "sender": sender,
        "intent_detected": intent,
        "urgency": urgency,
        "summary": content_str[:300] + "..." if len(content_str) > 300 else content_str
    }
