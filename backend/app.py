# backend/app/main.py
import os  # 🚨 used for command execution
from flask import Flask, request, jsonify
import psycopg
from dotenv import load_dotenv
import logging
from pythonjsonlogger import jsonlogger
from flask_cors import CORS

load_dotenv()


# Configure JSON logging using python-json-logger
def configure_json_logging():
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        # fmt='%(timestamp)s %(levelname)s %(name)s %(message)s',
        fmt="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] "
        "[dd.service=%(dd.service)s dd.env=%(dd.env)s dd.version=%(dd.version)s dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] "
        "- %(message)s",
        timestamp=True,
        rename_fields={"levelname": "level"},
    )

    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Add JSON handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


# Initialize JSON logging
configure_json_logging()

# Create logger for this module
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)


# Initialize the database connection
def get_db_connection():
    try:
        connection = psycopg.connect(
            f'host={os.environ.get("DB_HOST")} port={os.environ.get("DB_PORT")} dbname={os.environ.get("DB_NAME")} user={os.environ.get("DB_USER")} password={os.environ.get("DB_PASSWORD")}'
        )
        logger.info("Database connection established successfully")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise


def create_notes_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            content VARCHAR(255) NOT NULL
        );
    """
    logger.info("Creating notes table.")
    try:
        cursor.execute(create_table_query)
        conn.commit()
        logger.info("Table created successfully in PostgreSQL")
        cursor.close()
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        conn.rollback()
        cursor.close()
        logger.info("Table already exists.")


create_notes_table()


@app.before_request
def log_request():
    """Log incoming request details"""
    logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")


@app.after_request
def log_response(response):
    """Log response details"""
    logger.info(f"Response: {response.status_code} - {request.method} {request.path}")
    return response


@app.route("/")
def index():
    logger.info("Index endpoint accessed")
    return "Flask app is running. Add your first note!"


@app.route("/notes", methods=["GET"])
def get_notes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, content FROM notes;")
        notes = cur.fetchall()
        cur.close()
        conn.close()

        result = [{"id": n[0], "content": n[1]} for n in notes]
        logger.info(f"GET /notes - Successfully retrieved {len(result)} notes")
        return result
    except Exception as e:
        logger.error(f"GET /notes - Error retrieving notes: {str(e)}")
        return jsonify({"error": "Failed to retrieve notes"}), 500


@app.route("/notes", methods=["POST"])
def create_note():
    try:
        data = request.get_json()

        content = data.get("content")
        logger.info(f"POST /notes - Creating note with content: {content[:50]}...")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (content) VALUES (%s) RETURNING id;", (content,))
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        response_data = {"id": new_id, "content": content}
        logger.info(f"POST /notes - Successfully created note with ID: {new_id}")
        return jsonify(response_data), 201
    except Exception as e:
        logger.error(f"POST /notes - Error creating note: {str(e)}")
        return jsonify({"error": "Failed to create note"}), 500


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    try:
        data = request.get_json()
        if not data or "content" not in data:
            logger.warning(f"PUT /notes/{note_id} - Missing content in request")
            return jsonify({"error": "Content is required"}), 400

        content = data.get("content")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE notes SET content = %s WHERE id = %s;", (content, note_id))

        conn.commit()
        cur.close()
        conn.close()

        response_data = {"id": note_id, "content": content}
        logger.info(f"PUT /notes/{note_id} - Successfully updated note")
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"PUT /notes/{note_id} - Error updating note: {str(e)}")
        return jsonify({"error": "Failed to update note"}), 500


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM notes WHERE id = %s;", (note_id,))

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f"DELETE /notes/{note_id} - Successfully deleted note")
        return "", 204
    except Exception as e:
        logger.error(f"DELETE /notes/{note_id} - Error deleting note: {str(e)}")
        return jsonify({"error": "Failed to delete note"}), 500


if __name__ == "__main__":
    # logger.info("Starting Flask application")
    app.run(host="0.0.0.0", port=8000)
