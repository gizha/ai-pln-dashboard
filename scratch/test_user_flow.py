import sys
import os
import mysql.connector
import sqlite3

# Add backend directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'separated_app', 'backend'))

import main

# Ensure database functions connect correctly
main.load_dotenv(dotenv_path="separated_app/backend/.env", override=True)

# Question 1: "berapa persen karyawan ga masuk keseluruhan"
history = []
q1 = "berapa persen karyawan ga masuk keseluruhan"
print("=================== QUESTION 1 ===================")
print("Question:", q1)

# Generate SQL
sql1 = main.generate_sql(q1, provider="ollama_local")
print("Generated SQL for Q1:", sql1)

# Run Query on MySQL
try:
    conn = main.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql1)
    rows1 = cursor.fetchall()
    print("MySQL Rows Q1:", rows1)
    cursor.close()
    conn.close()
except Exception as e:
    print("MySQL Error Q1:", e)

# Answer Q1
ans1 = main.summarize_result(q1, rows1, provider="ollama_local", translate=True)
print("Answer Q1:", ans1)

# Append to history
history.append(main.ChatMessage(role="user", content=q1))
history.append(main.ChatMessage(role="assistant", content=ans1))

# Question 2: "berapa orang 20% itu berarti?"
q2 = "berapa orang 20% itu berarti?"
print("\n=================== QUESTION 2 ===================")
print("Question:", q2)

# Reformulate Question
q2_ref = main.reformulate_question(q2, history, provider="ollama_local")
print("Reformulated Question:", q2_ref)

# Generate SQL for Q2
sql2 = main.generate_sql(q2_ref, provider="ollama_local")
print("Generated SQL for Q2:", sql2)

# Run Query on MySQL
try:
    conn = main.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql2)
    rows2 = cursor.fetchall()
    print("MySQL Rows Q2:", rows2)
    cursor.close()
    conn.close()
except Exception as e:
    print("MySQL Error Q2:", e)

# Answer Q2
ans2 = main.summarize_result(q2_ref, rows2, provider="ollama_local", translate=True)
print("Answer Q2:", ans2)
