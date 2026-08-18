import sys
import os
import requests

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))

import main

# Ensure env is loaded
main.load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

question = "berapa persen karyawan yang masuk"
print("Question:", question)

providers = ["gemini", "ollama_local", "ollama_cloud"]

for provider in providers:
    print(f"\n--- Provider: {provider.upper()} ---")
    try:
        sql = main.generate_sql(question, provider=provider)
        print("Generated SQL:", sql)
        
        # Run against MySQL to see the result
        conn = main.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql)
        rows = cursor.fetchall()
        print("Result:", rows)
        cursor.close()
        conn.close()
    except Exception as e:
        print("Error:", e)
