import uuid

def generate_session_id() -> str:
    return str(uuid.uuid4())

def generate_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:8]}"
