import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))
from main import generate_sql

question = "ada bidang apa aja di pln"
for provider in ["gemini", "ollama_local"]:
    try:
        print(f"\n--- Testing with provider: {provider} ---")
        sql = generate_sql(question, provider=provider)
        print("Generated SQL:", sql)
    except Exception as e:
        print("Error:", e)
