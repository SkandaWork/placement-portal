from flask import Flask, render_template, request, redirect, session
from database import create_tables, get_db

app = Flask(__name__)
app.secret_key = "secret"

create_tables()


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    role = request.form["role"]
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    if role == "admin":

        cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password))
        admin = cur.fetchone()

        if admin:
            return redirect("/admin_dashboard")

    if role == "student":

        cur.execute("SELECT * FROM students WHERE email=? AND password=?", (username, password))
        student = cur.fetchone()

        if student:
            session["student_id"] = student["id"]
            return redirect("/student_dashboard")

    if role == "company":
        cur.execute(
            "SELECT * FROM companies WHERE name=? AND password=? AND status='Approved'",
            (username, password)
        )
        company = cur.fetchone()
        if company:
            session["company_id"] = company["id"]
            return redirect("/company_dashboard")
        return "Company not approved yet"

    return "Invalid Login"
@app.route("/register_student", methods=["GET","POST"])
def register_student():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO students (name,email,password) VALUES (?,?,?)",
        (name,email,password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register_student.html")
@app.route("/register_company", methods=["GET","POST"])
def register_company():

    if request.method == "POST":

        name = request.form["name"]
        hr_contact = request.form["hr_contact"]
        website = request.form["website"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
        "INSERT INTO companies (name,hr_contact,website,password,status) VALUES (?,?,?,?,?)",
        (name,hr_contact,website,password,"Pending")
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register_company.html")
@app.route("/admin_dashboard")
def admin_dashboard():

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM companies")
    companies = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM students")
    students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM companies")
    company_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM drives")
    drive_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications")
    application_count = cur.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        companies=companies,
        students=students,
        company_count=company_count,
        drive_count=drive_count,
        application_count=application_count
    )
@app.route("/approve_company/<int:company_id>")
def approve_company(company_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE companies SET status='Approved' WHERE id=?",
        (company_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin_dashboard")

@app.route("/company_dashboard")
def company_dashboard():

    company_id = session.get("company_id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM drives WHERE company_id=?",
        (company_id,)
    )

    drives = cur.fetchall()

    conn.close()

    return render_template(
        "company_dashboard.html",
        drives=drives
    )

@app.route("/create_drive", methods=["GET","POST"])
def create_drive():

    company_id = session.get("company_id")

    if request.method == "POST":

        job_title = request.form["job_title"]
        description = request.form["description"]
        eligibility = request.form["eligibility"]
        deadline = request.form["deadline"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
        """
        INSERT INTO drives
        (company_id,job_title,description,eligibility,deadline,status)
        VALUES (?,?,?,?,?,?)
        """,
        (company_id,job_title,description,eligibility,deadline,"Approved")
        )

        conn.commit()
        conn.close()

        return redirect("/company_dashboard")

    return render_template("create_drive.html")

@app.route("/student_dashboard")
def student_dashboard():

    student_id = session.get("student_id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM drives")
    drives = cur.fetchall()

    cur.execute(
        "SELECT * FROM applications WHERE student_id=?",
        (student_id,)
    )

    applications = cur.fetchall()

    conn.close()

    return render_template(
        "student_dashboard.html",
        drives=drives,
        applications=applications
    )
@app.route("/apply/<int:drive_id>")
def apply(drive_id):

    student_id = session.get("student_id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
    "SELECT * FROM applications WHERE student_id=? AND drive_id=?",
    (student_id,drive_id)
    )

    existing = cur.fetchone()

    if existing:
        return "Already applied"

    cur.execute(
    "INSERT INTO applications (student_id,drive_id,status) VALUES (?,?,?)",
    (student_id,drive_id,"Applied")
    )

    conn.commit()
    conn.close()

    return redirect("/student_dashboard")

@app.route("/view_applicants/<int:drive_id>")
def view_applicants(drive_id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM applications WHERE drive_id=?",
        (drive_id,)
    )

    applications = cur.fetchall()

    conn.close()

    return render_template(
        "view_applicants.html",
        applications=applications
    )

@app.route("/update_status/<int:app_id>/<status>")
def update_status(app_id,status):

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE applications SET status=? WHERE id=?",
        (status,app_id)
    )

    conn.commit()
    conn.close()

    return redirect(request.referrer)
if __name__ == "__main__":
    app.run(debug=True)

