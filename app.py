from flask import Flask, render_template, request, redirect
import cloudinary
import cloudinary.uploader
import os
import psycopg2

app = Flask(__name__)

# Configure Cloudinary (uses CLOUDINARY_URL from Render)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Automatically create table if not exists
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id SERIAL PRIMARY KEY,
            file_url TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

create_table()


@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT file_url FROM files ORDER BY id DESC;")
    files = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("upload.html", files=files)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file selected"

    file = request.files["file"]

    if file.filename == "":
        return "No file selected"

    if file:
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
    file,
    upload_preset="my_unsigned_upload"
)
        file_url = result["secure_url"]

        # Save URL in PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO files (file_url) VALUES (%s);", (file_url,))
        conn.commit()
        cur.close()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    


