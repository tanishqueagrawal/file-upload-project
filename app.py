from flask import Flask, render_template, request, redirect
import cloudinary
import cloudinary.uploader
import os
import psycopg2

app = Flask(__name__)

# Cloudinary configuration (reads from CLOUDINARY_URL env variable)
cloudinary.config(secure=True)

# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


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
        result = cloudinary.uploader.upload(file)
        file_url = result["secure_url"]

        # Save URL to PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO files (file_url) VALUES (%s);", (file_url,))
        conn.commit()
        cur.close()
        conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    return "Invalid file type"


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
