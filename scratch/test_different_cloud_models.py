import sys
import os
import requests

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))

import main

# Ensure env is loaded
main.load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

test_models = [
    "gpt-oss:20b",
    "gpt-oss:120b",
    "qwen3.5:397b",
    "deepseek-v4-pro",
    "gemma4:31b"
]

question = "berapa persen karyawan yang masuk"
print("Testing question:", question)

for model in test_models:
    print(f"\n--- Testing Model: {model.upper()} ---")
    # Temporarily override the cloud model in main module
    main.OLLAMA_CLOUD_MODEL = model
    try:
        sql = main.generate_sql(question, provider="ollama_cloud")
        print("Generated SQL:", sql)
        
        # Test executing
        conn = main.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        print("Execution Result:", rows)
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", e)
