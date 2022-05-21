import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# import tkinter
# from tkinter import messagebox

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///decaploy.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():

    # TODO: Get all assigned task from database, name the row rows
    rows = db.execute("SELECT employees.first_name AS firstname, employees.last_name AS lastname, tasks.task AS task, assigned_tasks.id AS id, assigned_tasks.due_date AS due_date FROM employees JOIN assigned_tasks ON employees.id = assigned_tasks.assigned_id JOIN tasks ON assigned_tasks.assigned_task_id = tasks.id")

    # TODO: render the index template
    return render_template("index.html", rows = rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            error_message = "Please enter username"
            return render_template("login.html", error = error_message)

        # Ensure password was submitted
        elif not password:
            error_message = "Please enter password"
            return render_template("login.html", error = error_message)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            error_message = "Wrong password or username"
            return render_template("login.html", error = error_message)

        # Remember which user has logged in
        session["user_role"] = rows[0]["user_role"]
        session["user_id"] = rows[0]["user_id"]
        session["user_name"] = username

        # Get the number of complaint counts from the database
        rows = db.execute("SELECT COUNT(*) AS count FROM complaints")
        row = rows[0]
        session["complaint_count"] = row["count"]

        # Get the total number of employees
        employees = db.execute("SELECT COUNT(*) AS count FROM employees")
        employee = employees[0]
        session["employees"] = employee["count"]

        # Get the total number of assigned tasks
        tasks = db.execute("SELECT COUNT(*) AS count FROM assigned_tasks")
        task = tasks[0]
        session["tasks"] = task["count"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/add_employee", methods=["GET", "POST"])
@login_required
def add_employee():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return redirect("/", error = error_message)
        # messagebox.showinfo("Access Denied", "")

    # validate user
    if request.method == "POST":

        # Store session id in an id variable
        id = session["user_id"]

        # Store all the user inputs in variables
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        password = request.form.get("password")
        comfirm_password = request.form.get("comfirmation")
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        gender = request.form.get("gender")
        country = request.form.get("country")
        state = request.form.get("state")
        designation = request.form.get("designation")
        address = request.form.get("address")
        age = request.form.get("age")
        qualification = request.form.get("qualification")
        role = request.form.get("role")
        grade = request.form.get("grade")

        #TODO: create a list of inputs and do back end form validation

        # Ensure that the email does not exist
        rows = db.execute("SELECT * FROM employees WHERE email = ?", email)
        if len(rows) != 0:
            error_message = "Email already taken"
            return render_template("add_employees.html", error = error_message)

        # Database validation
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            error_message = "Username already exits"
            return render_template("add_employees.html", error = error_message)

        # Ensure password and comfirm password matches
        if password != comfirm_password:
            error_message = "Passwords must match"
            return render_template("add_employees.html", error = error_message)

        # Hash password
        hashed_password = generate_password_hash(password)

        #TODO: Create the user
        user_id = db.execute("INSERT INTO employees (first_name, middle_name, last_name, email, phone, gender, country, origin_state, designation, aaddress, qualification, grade, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", first_name, middle_name, last_name, email, phone_number, gender, country, state, designation, address, qualification, grade, age)

        #TODO: Insert user logincredentials into users table
        db.execute("INSERT INTO users (user_id, username, password, user_role) VALUES(?, ?, ?, ?)", user_id, username, hashed_password, role)

        #TODO: Redirect the user to his/her dashboard
        success_message = "Employee has been added successfully"
        return render_template("add_employees.html", success = success_message)

    else:
        return render_template("add_employees.html")

@app.route("/task", methods=["GET", "POST"])
@login_required
def task():

     # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Ensure post request was made
    if request.method == "POST":

        # Get the user input
        task = request.form.get("task")

        # Update the tasks table
        db.execute("INSERT INTO tasks (task) VALUES(?)", task)

        # Render task teplate
        success_message = "Task added successfully"
        return render_template("tasks.html", success = success_message)

    else:
        return render_template("tasks.html")

@app.route("/item", methods=["GET", "POST"])
@login_required
def item():

     # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Ensure post request was made
    if request.method == "POST":

        # Get the user input
        item = request.form.get("item")

        # Update the items table
        db.execute("INSERT INTO items (item) VALUES(?)", item)

        # Render item teplate
        success_message = "Item added successfully"
        return render_template("items.html", success = success_message)

    else:
        return render_template("items.html")

@app.route("/assign", methods=["GET", "POST"])
@login_required
def assign():

    # Get the logged in user's id
    id = session["user_id"]

     # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Ensure post request was made
    if request.method == "POST":

        # Get the user input
        task_id = request.form.get("assigned_task")
        employee_id = request.form.get("employee")
        due_date = request.form.get("due_date")

        # Update the tasks table
        db.execute("INSERT INTO assigned_tasks (assignee_id, assigned_id, assigned_task_id, due_date) VALUES(?, ?, ?, ?)", id, employee_id, task_id, due_date)

        # Render task teplate
        success_message = "Task added successfully"
        return render_template("items.html", success = success_message)

    else:

        # TODO: Get tasks from database, name the row tasks
        tasks = db.execute("SELECT * FROM tasks")

        # TODO: Get employees from the database, name the row employees
        employees = db.execute("SELECT * FROM employees JOIN users ON employees.id = users.user_id WHERE users.user_role = ?", 0)

        # success message
        success_message = "Task assigned successfully"

        return render_template("assign_tasks.html", employees = employees, tasks = tasks, success = success_message)



@app.route("/report_task", methods=["GET", "POST"])
@login_required
def report_task():

    # Get the logged in user id
    id = session["user_id"]

    if session["user_role"] == 1:

        # TODO: Get all assigned task from database, name the row rows
        rows = db.execute("SELECT employees.first_name AS firstname, employees.last_name AS lastname, tasks.task AS task, assigned_tasks.id AS id, assigned_tasks.due_date AS due_date FROM employees JOIN assigned_tasks ON employees.id = assigned_tasks.assigned_id JOIN tasks ON assigned_tasks.assigned_task_id = tasks.id")

        # TODO: render the report_task template
        return render_template("report_tasks.html", rows = rows)

    if session["user_role"] != 1:

        # TODO: Get all assigned task from database, name the row rows
        rows = db.execute("SELECT employees.first_name AS firstname, employees.last_name AS lastname, tasks.task AS task, assigned_tasks.id AS id, assigned_tasks.due_date AS due_date FROM employees JOIN assigned_tasks ON employees.id = assigned_tasks.assigned_id JOIN tasks ON assigned_tasks.assigned_task_id = tasks.id WHERE employees.id = ?", id)

        # TODO: render the report_task template
        return render_template("employee_task.html", rows = rows)


@app.route("/delete_task", methods=["GET", "POST"])
@login_required
def delete_task():

    # Get the logged in user id
    id = session["user_id"]

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    if request.method == "POST":

        # Get user input
        task_id = request.form.get("task")

        # Ensure an item is selected
        if not task_id:
            error_message = "Select a task"
            return render_template("delete_task.html", error = error_message)

        # Delete the task from the assigned task table
        db.execute("DELETE FROM assigned_tasks WHERE assigned_task_id = ?", task_id)

        # TODO: Delete task from the tasks table
        db.execute("DELETE FROM tasks WHERE id = ?", task_id)

        # Render the delete_task template with success message
        success_message = "Task deleted successfully"
        return render_template("delete_task.html", success = success_message)


    else:
        # TODO: Get all tasks from tasks table and name the row tasks
        tasks = db.execute("SELECT * FROM tasks")

        # TODO: Render the template
        return render_template("delete_task.html", tasks = tasks)



@app.route("/delete_item", methods=["GET", "POST"])
@login_required
def delete_item():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    if request.method == "POST":

        # Get user input
        item_id = request.form.get("item")

        # Ensure an item is selected
        if not item_id:
            error_message = "Select an item"
            return render_template("delete_item.html", error = error_message)

        # Delete from requisition table
        db.execute("DELETE FROM requisition WHERE item_id = ?", item_id)

        # Delete item from items table
        db.execute("DELETE FROM items WHERE id = ?", item_id)

        # Render the delete_item template
        success_message = "Item deleted successfully"
        return render_template("delete_item.html", success = success_message)

    else:

        # Get all the items from the database
        items = db.execute("SELECT * FROM items")

        # render the template
        return render_template("delete_item.html", items = items)


@app.route("/report_employee", methods=["GET", "POST"])
@login_required
def report_employee():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # TODO: Get all employees from database, name the row rows
    rows = db.execute("SELECT * FROM employees")

    # TODO: render the report_task template
    count = 0
    return render_template("report_employees.html", rows = rows, count = count)

@app.route("/employee_detail", methods=["GET", "POST"])
@login_required
def employee_detail():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")

    # TODO: Get all employees from database, name the row rows
    rows = db.execute("SELECT *, users.user_role FROM employees JOIN users ON employees.id = users.user_id WHERE employees.id = ?", id)
    row = rows[0]

    # TODO: render the report_task template
    return render_template("employee_details.html", row = row)

@app.route("/employee_update", methods=["GET", "POST"])
@login_required
def employee_update():

    # Check if post request was made
    if request.method == "POST":

        # Store all the user inputs in variables
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        gender = request.form.get("gender")
        country = request.form.get("country")
        state = request.form.get("state")
        designation = request.form.get("designation")
        address = request.form.get("address")
        age = request.form.get("age")
        qualification = request.form.get("qualification")
        grade = request.form.get("grade")
        id = request.form.get("id")

        #TODO: create a list of inputs and do back end form validation


        #TODO: Update the user
        if session["user_role"] == 1:
            db.execute("UPDATE employees SET first_name = ?, middle_name = ?, last_name = ?, email = ?, phone = ?, gender = ?, country = ?, origin_state = ?, designation = ?, aaddress = ?, qualification = ?, grade = ?, age = ? WHERE id = ?", first_name, middle_name, last_name, email, phone_number, gender, country, state, designation, address, qualification, grade, age, id)

        if session["user_role"] != 1:
            db.execute("UPDATE employees SET email = ?, phone = ?, gender = ?, country = ?, origin_state = ?, aaddress = ?, qualification = ?, age = ? WHERE id = ?", email, phone_number, gender, country, state, address, qualification, age, id)

         #TODO: Redirect the user to his/her dashboard
        success_message = "Employee info has been updated successfully"
        return render_template("index.html", success = success_message)

    else:

        if session["user_role"] == 1:

            # Get the user input
            id = request.args.get("id")

            # TODO: Get all employees from database, name the row rows
            rows = db.execute("SELECT *, users.user_role FROM employees JOIN users ON employees.id = users.user_id WHERE employees.id = ?", id)
            row = rows[0]

            # TODO: render the report_task template
            return render_template("employee_update.html", row = row)

        if session["user_role"] != 1:

            # Get the user input
            id = session["user_id"]

            # TODO: Get all employees from database, name the row rows
            rows = db.execute("SELECT *, users.user_role FROM employees JOIN users ON employees.id = users.user_id WHERE employees.id = ?", id)
            row = rows[0]

            # TODO: render the report_task template
            return render_template("update_profile.html", row = row)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():

    # Get the user input
    id = session["user_id"]

    # TODO: Get all employees from database, name the row rows
    rows = db.execute("SELECT *, users.user_role FROM employees JOIN users ON employees.id = users.user_id WHERE employees.id = ?", id)
    row = rows[0]

    # TODO: render the report_task template
    return render_template("edit_profile.html", row = row)

@app.route("/delete_employee", methods=["GET", "POST"])
@login_required
def delete_employee():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")

    # Delete the employee from users table
    db.execute("DELETE FROM users WHERE user_id = ?", id)

    # Delete the employee from the database
    db.execute("DELETE FROM employees WHERE id = ?", id)

    # redirect the user
    return redirect("/report_employee")


@app.route("/report_item", methods=["GET", "POST"])
@login_required
def report_item():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # TODO: Get all items from database, name the row rows
    rows = db.execute("SELECT * FROM items")

    # TODO: render the report_task template
    return render_template("report_items.html", rows = rows)

@app.route("/delete_items", methods=["GET", "POST"])
@login_required
def delete_items():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")

    # Delete the employee from the database
    db.execute("DELETE FROM items WHERE id = ?", id)

    # redirect the user
    return redirect("/report_item")


@app.route("/delete_tasks", methods=["GET", "POST"])
@login_required
def delete_tasks():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")

    # Delete the task from assigned tasks table
    db.execute("DELETE FROM assigned_tasks WHERE assigned_task_id = ?", id)

    # Delete the employee from the database
    db.execute("DELETE FROM tasks WHERE id = ?", id)

    # redirect the user
    return redirect("/report_task")

@app.route("/report_complaints", methods=["GET", "POST"])
@login_required
def report_complaints():

    # Get the logged in user's id
    id = session["user_id"]

    if session["user_role"] == 1:

        # TODO: Get all complaints from database, name the row rows
        rows = db.execute("SELECT complaints.id AS id, complaints.status AS status, complaints.complaint AS complaint, employees.first_name AS firstname, employees.last_name AS lastname FROM complaints JOIN employees ON complaints.employee_id = employees.id")

        # TODO: render the report_compalints template
        return render_template("report_complaints.html", rows = rows)

    if session["user_role"] != 1:

        # TODO: Get all complaints from database, name the row rows
        rows = db.execute("SELECT complaints.id AS id, complaints.status AS status, complaints.complaint AS complaint, employees.first_name AS firstname, employees.last_name AS lastname FROM complaints JOIN employees ON complaints.employee_id = employees.id WHERE employees.id = ?", id)

        # TODO: render the report_compalints template
        return render_template("employee_complaint.html", rows = rows)


@app.route("/review_complaints", methods=["GET", "POST"])
@login_required
def review_complaints():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")

    # TODO: Update the status of the complaints table
    db.execute("UPDATE complaints SET status = ? WHERE id = ?", "Resolved", id)

    # TODO: render the report_compalints template
    # TODO: Get all complaints from database, name the row rows
    rows = db.execute("SELECT complaints.id AS id, complaints.status AS status, complaints.complaint AS complaint, employees.first_name AS firstname, employees.last_name AS lastname FROM complaints JOIN employees ON complaints.employee_id = employees.id")

    success_message = "Complaints have been reviewed and resolved"
    return render_template("report_complaints.html", rows = rows, success = success_message)

@app.route("/report_leave", methods=["GET", "POST"])
@login_required
def report_leave():

    # Get the logged in user's id
    id = session["user_id"]

    if session["user_role"] == 1:

        # TODO: Get all leave requests from database, name the row rows
        rows = db.execute("SELECT leave.id, reason, start_date, end_date, status, employees.first_name AS firstname, employees.last_name AS lastname FROM leave JOIN employees ON leave.employees_id = employees.id ORDER BY status ASC")

        # TODO: render the report_leave template
        return render_template("report_leave.html", rows = rows)

    if session["user_role"] != 1:

        # TODO: Get all leave requests from database, name the row rows
        rows = db.execute("SELECT leave.id, reason, start_date, end_date, status, employees.first_name AS firstname, employees.last_name AS lastname FROM leave JOIN employees ON leave.employees_id = employees.id WHERE employees.id = ? ORDER BY status ASC", id)

        # TODO: render the report_leave template
        return render_template("employee_leave_report.html", rows = rows)


@app.route("/approve_leave", methods=["GET", "POST"])
@login_required
def approve_or_reject_leave():

    # Check if admin user is logged in
    if session["user_role"] != 1:
        error_message = "Access Denied"
        return render_template("index.html", error = error_message)

    # Get the user input
    id = request.args.get("id")
    status = request.args.get("status")

    # TODO: Update the status of the leave table
    if status == "approve":
        db.execute("UPDATE leave SET status = ? WHERE id = ?", "Approved", id)

    if status == "reject":
        db.execute("UPDATE leave SET status = ? WHERE id = ?", "Rejected", id)

    # TODO: Get all complaints from database, name the row rows
    rows = db.execute("SELECT leave.id, reason, start_date, end_date, status, employees.first_name AS firstname, employees.last_name AS lastname FROM leave JOIN employees ON leave.employees_id = employees.id")

    # Render the template with success message
    error_message = "Rejected"
    success_message = "Leave approved suuceesfully"

    if status == "approve":
        return render_template("report_leave.html", rows = rows, success = success_message)

    if status == "reject":
        return render_template("report_leave.html", rows = rows, error = error_message)


@app.route("/report_requisition", methods=["GET", "POST"])
@login_required
def report_requisition():

    # Get logged user id
    id = session["user_id"]

    if session["user_role"] == 1:

        # TODO: Get all requisition requests from database, name the row rows
        rows = db.execute("SELECT requisition.id, items.item AS request, requisition.status AS status, employees.first_name AS firstname, employees.last_name AS lastname FROM requisition JOIN employees ON requisition.employee_id = employees.id JOIN items ON requisition.item_id = items.id")

        # TODO: render the report_compalints template
        return render_template("report_requisition.html", rows = rows)

    if session["user_role"] != 1:

        # TODO: Get all requisition requests from database, name the row rows
        rows = db.execute("SELECT requisition.id, items.item AS request, requisition.status AS status, employees.first_name AS firstname, employees.last_name AS lastname FROM requisition JOIN employees ON requisition.employee_id = employees.id JOIN items ON requisition.item_id = items.id WHERE employees.id = ?", id)

        # TODO: render the report_compalints template
        return render_template("requested_item.html", rows = rows)



# EMPLOYEE FUNCTIONS

@app.route("/leave_request", methods=["GET", "POST"])
@login_required
def leave_request():

    # Ensure request method is post
    if request.method == "POST":

        # Get user inputs
        reason = request.form.get("reason")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        employee_id = session["user_id"]

        # Ensure no input field is empty
        if not start_date or not end_date:
            error_message = "Please choose a start or end date"
            return render_template("leave_request.html", error = error_message)

        # Insert the request in the daabase
        db.execute("INSERT INTO leave (employees_id, reason, start_date, end_date) VALUES(?, ?, ?, ?)", employee_id, reason, start_date, end_date)

        # Render the leave template with a success essage
        success_message = "Request logged successfully"
        return render_template("leave_request.html", success = success_message)

    else:

        # render the leave template
        return render_template("leave_request.html")

@app.route("/item_request", methods=["GET", "POST"])
@login_required
def item_request():


    # Ensure post request was made
    if request.method == "POST":

        employee_id = session["user_id"]

        # Get the user input
        item = request.form.get("item")
        qty = request.form.get("qty")

        # Update the requisition table
        db.execute("INSERT INTO requisition (employee_id, item_id, qty) VALUES(?, ?, ?)", employee_id, item, qty)

        # Render task teplate
        success_message = "Item requested successfully"
        return render_template("item_request.html", success = success_message)

    else:

        # TODO: Get items from database, name the row tasks
        items = db.execute("SELECT * FROM items")

        # Render the template
        return render_template("item_request.html", items = items)

@app.route("/complaint", methods=["GET", "POST"])
@login_required
def complain():

# To ensure request method is post
    if request.method == "POST":

        # Get employee id
        employee_id = session["user_id"]

        # Get user's input
        complaint = request.form.get("complain")

        # capture employee complaint into the database
        db.execute("INSERT INTO complaints (employee_id, complaint) VALUES(?, ?)", employee_id, complaint)

        # Render successful if complaint is captured
        success_message = "complaint received successfully"

        # Render the complaint template with success message
        return render_template("complaint.html", success = success_message)

    else:
        #render the complaint template
        return render_template("complaint.html")

@app.route("/security", methods=["GET", "POST"])
@login_required
def security():

    # Get logged in user id
    id = session["user_id"]

    if request.method == "POST":

        # Get user's inputs
        old_password = request.form.get("old_password")
        password = request.form.get("password")
        comfirm_password = request.form.get("comfirmation")

        # Ensure old password matches user's current password
        rows = db.execute("SELECT * FROM users WHERE user_id = ?", id)
        row = rows[0]

        if not check_password_hash(row["password"], old_password):

            # render the password template with error message
            error_message = "Wrong old password"
            return render_template("security.html", error = error_message)

        # Ensure that the new passwords match
        if password != comfirm_password:

            # render the password template with error message
            error_message = "New passwords must match"
            return render_template("security.html", error = error_message)

        # Hash the new password
        hashed_password = generate_password_hash(password)

        # Change the password
        db.execute("UPDATE users SET password = ? WHERE user_id = ?", hashed_password, id)

        # render the password template with success message
        success_message = "Password changed successfully"
        return render_template("security.html", success = success_message)

    else:

        # render the password template
        return render_template("security.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")