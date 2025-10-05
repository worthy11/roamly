import time

session_memory = {}

def cleanup_sessions():
    while True:
        now = time.time()
        expired = [
            sid for sid, data in session_memory.items()
            if now - data["last_used"] > 3600
        ]
        for sid in expired:
            del session_memory[sid]
        time.sleep(600)

def update_session(session_id, role, content):
    now = time.time()
    if not session_memory.get(session_id):
        session_memory[session_id] = {
            "last_used": now,
            "history": [{
                "role": role,
                "content": content
            }]
        }
    else:
        session_memory[session_id]["last_used"] = now
        session_memory[session_id]["history"].append({
            "role": role,
            "content": content
        })

def get_history(session_id):
    if not session_memory.get(session_id):
        return []
    return session_memory[session_id]["history"]