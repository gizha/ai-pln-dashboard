import sys
import os
import requests

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))

import main

# Ensure env is loaded
main.load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

main.OLLAMA_CLOUD_MODEL = "gemma4:31b"

history = [
    main.ChatMessage(role="user", content="berapa persen karyawan ga masuk keseluruhan"),
    main.ChatMessage(role="assistant", content="Berdasarkan data di database lokal, hasil pencarian absent_percentage adalah: 20%")
]
q2 = "berapa orang 20% itu berarti?"

print("Model: gemma4:31b")
print("Q1 (History): berapa persen karyawan ga masuk keseluruhan")
print("A1 (History): 20%")
print("Q2:", q2)

try:
    # 1. Reformulate
    q2_ref = main.reformulate_question(q2, history, provider="ollama_cloud")
    print("Reformulated Q2:", q2_ref)
    
    # 2. Generate SQL
    sql = main.generate_sql(q2_ref, provider="ollama_cloud")
    print("Generated SQL:", sql)
    
    # 3. Execute
    conn = main.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    rows = cursor.fetchall()
    print("Execution Result:", rows)
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
