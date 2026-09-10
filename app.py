import os

from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt

from database import create_database, create_user, get_user

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "development-secret-key"
)

create_database()


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Basic input validation
        if len(username) < 3:
            return render_template(
                "register.html",
                message="Username must be at least 3 characters long."
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                message="Password must be at least 8 characters long."
            )

        if password != confirm_password:
         return render_template(
        "register.html",
        message="Passwords do not match."
    )

        # Hash password using bcrypt
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        # Store user in database
        success = create_user(
            username,
            password_hash.decode("utf-8")
        )

        if not success:
            return render_template(
                "register.html",
                message="Username already exists."
            )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        # Find user
        user = get_user(username)

        if user is None:
            return render_template(
                "login.html",
                message="Invalid username or password."
            )

        user_id, stored_username, stored_hash = user

        # Verify password using bcrypt
        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        ):
            session["user_id"] = user_id
            session["username"] = stored_username

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            message="Invalid username or password."
        )

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)