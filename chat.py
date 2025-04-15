# %%
import mysql.connector
import requests

# --- KONFIGURASI ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test'
}

OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3:8b'
MODE_BERBAHAYA = True  # False = mode aman (tidak boleh DELETE/UPDATE/DROP)

# --- CEK KEAMANAN QUERY ---
def aman_dieksekusi(query):
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ['delete', 'update', 'drop']):
        if not MODE_BERBAHAYA:
            print("❌ Mode aman aktif. Query penghapusan/pembaruan diblokir.")
            return False
        konfirmasi = input(f"⚠️ Query sensitif terdeteksi:\n{query}\nLanjutkan? (yes/no): ")
        return konfirmasi.strip().lower() == "yes"
    return True

# --- FUNGSI EKSEKUSI SQL ---
def run_query(sql):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(sql)
    if cursor.description:  # kalau SELECT atau query lain yang punya hasil
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
    else:  # misal DELETE/UPDATE
        conn.commit()
        rows = [(f"{cursor.rowcount} baris terpengaruh",)]
        columns = ["Status"]
    cursor.close()
    conn.close()
    return {"columns": columns, "rows": rows}

# --- KIRIM PROMPT KE OLLAMA ---
def ask_ollama(prompt):
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

# --- AGENT LOOP ---
def run_agent_loop(user_question):
    history = f"""Kamu adalah asisten AI yang bisa mengakses database MySQL.
Kamu akan diberikan pertanyaan, dan kamu boleh menjalankan SQL untuk mencari jawaban.

Jangan jawab dulu sebelum yakin punya data yang cukup.

Jika kamu ingin mengeksekusi query, tulis dengan format

SQL: [query di sini]

Jika kamu sudah bisa menjawab, cukup jawab langsung, tanpa SQL.
"""

    while True:
        prompt = history + f"\n\nPertanyaan: {user_question}\n\nJawaban:"
        print("\n⏳ Mengirim prompt ke Ollama...\n")
        response = ask_ollama(prompt)
        print("🧠 Model:", response)

        if "SQL:" in response:
            query = response.split("SQL:")[1].split("```")[0].strip()

            if aman_dieksekusi(query):
                try:
                    result = run_query(query)
                    rows_preview = "\n".join(str(row) for row in result["rows"][:5])
                    history += f"\n\nSQL: {query}\n\nHasil:\n{rows_preview}\n"
                except Exception as e:
                    print("⚠️ Gagal eksekusi SQL:", e)
                    history += f"\n\n(SQL gagal dijalankan: {e})\n"
            else:
                history += f"\n\n(SQL dibatalkan oleh user)\n"
        else:
            print("\n✅ Jawaban akhir:\n", response.strip())
            break

# --- MAIN ---
if __name__ == "__main__":
    pertanyaan = input("❓ Masukkan pertanyaan: ")
    run_agent_loop(pertanyaan)



