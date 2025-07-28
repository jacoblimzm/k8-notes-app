# backend/app/main.py
import os  # 🚨 used for command execution
from flask import Flask, request, jsonify
import psycopg
from dotenv import load_dotenv
import logging
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)


# Initialize the database connection
def get_db_connection():
    return psycopg.connect(
        f'host={os.environ.get("DB_HOST")} port={os.environ.get("DB_PORT")} dbname={os.environ.get("DB_NAME")} user={os.environ.get("DB_USER")} password={os.environ.get("DB_PASSWORD")}'
    )


def create_notes_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            content VARCHAR(255) NOT NULL
        );
    """
    logging.info("Creating notes table.")
    try:
        cursor.execute(create_table_query)
        conn.commit()
        logging.info("Table created successfully in PostgreSQL")
        cursor.close()
    except Exception as e:
        print(e)
        conn.rollback()
        cursor.close()
        logging.info("Table already exists.")


create_notes_table()


@app.route("/")
def index():
    return "Flask app is running. Add your first note!"


@app.route("/notes", methods=["GET"])
def get_notes():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM notes;")
    notes = cur.fetchall()
    cur.close()
    conn.close()
    # jsonify not necessary with flask
    return [{"id": n[0], "content": n[1]} for n in notes]


@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    content = data.get("content")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (content) VALUES (%s) RETURNING id;", (content,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "content": content}), 201


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json()
    content = data.get("content")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET content = %s WHERE id = %s;", (content, note_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": note_id, "content": content})


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
