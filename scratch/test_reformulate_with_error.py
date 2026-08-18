import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))
from main import reformulate_question, ChatMessage

history = [
    ChatMessage(role="user", content="ada bidang apa aja di pln"),
    ChatMessage(role="assistant", content="Maaf, saya hanya bisa menjawab pertanyaan yang bersifat membaca data.")
]
question = "ada bidang apa aja di pln"

try:
    result = reformulate_question(question, history, provider="gemini")
    print("Reformulated:", result)
except Exception as e:
    print("Error:", e)
