


from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)


def create_table():
    connection = sqlite3.connect("careertrack.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            applied_date TEXT,
            notes TEXT
        )
    """)

    try:
        cursor.execute("ALTER TABLE applications ADD COLUMN applied_date TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE applications ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = sqlite3.connect("careertrack.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM applications")
    applications = cursor.fetchall()

    connection.close()

    return render_template("index.html", applications=applications)


@app.route("/add", methods=["POST"])
def add_application():
    company = request.form["company"]
    role = request.form["role"]
    status = request.form["status"]
    applied_date = date.today().strftime("%Y-%m-%d")
    notes = request.form.get("notes", "")

    connection = sqlite3.connect("careertrack.db")
    cursor = connection.cursor()

    cursor.execute(
        """INSERT INTO applications
           (company, role, status, applied_date, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (company, role, status, applied_date, notes)
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    connection = sqlite3.connect("careertrack.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id = ?",
        (application_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/")


@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):
    connection = sqlite3.connect("careertrack.db")
    cursor = connection.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        status = request.form["status"]
        notes = request.form.get("notes", "")

        cursor.execute(
            """UPDATE applications
               SET company = ?, role = ?, status = ?, notes = ?
               WHERE id = ?""",
            (company, role, status, notes, application_id)
        )

        connection.commit()
        connection.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM applications WHERE id = ?",
        (application_id,)
    )

    application = cursor.fetchone()
    connection.close()

    if application is None:
        return "Application not found", 404

    return render_template("edit.html", application=application)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
