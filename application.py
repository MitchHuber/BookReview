import os
import requests
import json

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    return render_template("register.html")

@app.route("/save-reg", methods=["POST"])
def savereg():
    user = request.form.get("username")
    password = request.form.get("password")
    password1 = request.form.get("password1")
    email = request.form.get("email")
    if password != password1:
        return render_template("register.html", message = "Passwords do not match")
    if user == "" or password == "" or email == "":
        return render_template("register.html", message="You must file out all of the boxes before registering")
    if db.execute("SELECT * FROM users WHERE username = :user", {"user": user}).rowcount >= 1:
        return render_template("register.html", message="That username is taken")
    db.execute("INSERT INTO users (username,password,email) VALUES (:user, :password, :email)",
        {"user": user, "password": password, "email":email})
    db.commit()
    return render_template("index.html", message="Registration Successful")

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("username")
    password = request.form.get("password")
    #Checks to make sure user doesn't leave username/password field empty
    if user == "" or password == "":
        return render_template("index.html", message="You must fill out the username and passoword field to log in")
    #Checks to see if the user is registered
    if db.execute("SELECT * FROM users where username = :user", {"user": user}).rowcount == 0:
        return render_template("index.html", message="There is no user registered with that username")
    #Checks to make sure username/password is correct
    if db.execute("SELECT * FROM users WHERE username = :user AND password = :password",
        {"user": user, "password": password}).rowcount == 0:
        return render_template("index.html", message="The username/password combination is incorrect")
    session['username'] = user
    return render_template("mainpage.html")

@app.route("/searchResults", methods=["POST"])
def searchResults():
    first_search = request.form.get("search")
    search = f"%{first_search}%"
    #Chcek to make sure user fills out the search box
    if search == "%%":
        return render_template("mainpage.html", message="You have to fill out the search box!")
    #Checks isbn, title, and author for no results
    if db.execute("SELECT * FROM books WHERE isbn LIKE :isbn",
        {"isbn": search}).rowcount == 0:
        if db.execute("SELECT * FROM books WHERE title LIKE :title",
          {"title": search}).rowcount == 0:
          if db.execute("SELECT * FROM books WHERE author LIKE :author",
          {"author": search}).rowcount == 0:
            return render_template("mainpage.html", message="No results found")
    #Checks the database for matches with isbn, title, & author
    results = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author",
        {"isbn": search, "title": search, "author": search})
    return render_template("books.html", results=results, first_search=first_search)

@app.route("/bookinfo/<int:book_id>")
def bookinfo(book_id):
    if db.execute("SELECT isbn FROM books WHERE id = :id",
        {"id": book_id}).rowcount == 0:
            return render_template("error.html", message = "Book not found")

    isbns = db.execute("SELECT isbn FROM books WHERE id = :id",
        {"id": book_id}).fetchone()[0]
    book = db.execute("SELECT * FROM books where isbn = :isbn",
        {"isbn": isbns})
    review = db.execute("SELECT * FROM reviews WHERE book = :id",
        {"id": book_id})

    userid = db.execute("SELECT username FROM reviews WHERE book = :bookid",
        {"bookid": book_id}).fetchall()

    username = []
    for users in userid:
        user = db.execute("SELECT username from users WHERE id = :userid",
        {"userid": users[0]}).fetchone()[0]
        username.append(user)

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": "C3kxNYZgP5DXgSbQwX7yQ", "isbns": isbns})

    data = res.json()
    parsed_data = json.dumps(data)
    reviews = data.get("books")

    totalrating = (reviews[0].get("reviews_count"))
    avgrating = (reviews[0].get("average_rating"))

    return render_template("bookinfo.html", book=book, totalrating=totalrating, avgrating=avgrating, review=review, username=username )

@app.route("/save-rev/<string:book_isbn>", methods=["POST"])
def saverev(book_isbn):
    desc = request.form.get("description")
    rating = int(request.form['rating'])
    bookid = db.execute("SELECT id FROM books WHERE isbn = :isbn",
        {"isbn": book_isbn}).fetchone()[0]
    userid = db.execute("SELECT id FROM users WHERE username = :username",
        {"username": session['username']}).fetchone()[0]

    if desc == "":
        return render_template("mainpage.html", message="Review failed no decsription include")

    if db.execute("SELECT username FROM reviews WHERE username = :userid AND book = :bookid",
        {"userid": userid, "bookid": bookid}).rowcount > 0:
        return render_template("mainpage.html", message="You already submitted a review for that title")

    db.execute("INSERT INTO reviews (username, book, description, rating) VALUES (:username, :book, :description, :rating)",
       {"username": userid, "book": bookid, "description": desc, "rating": rating})
    db.commit()
    return render_template("mainpage.html", message="Review submitted")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('username', None)
    return render_template("index.html")

@app.route("/api/<string:isbn>")
def api(isbn):
    if db.execute("SELECT isbn FROM books WHERE isbn = :id",
        {"id": isbn}).rowcount == 0:
        return jsonify({"error": "Invalid ISBN"}), 404

    isbns = db.execute("SELECT isbn FROM books WHERE isbn = :id",
        {"id": isbn}).fetchone()[0]

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": "C3kxNYZgP5DXgSbQwX7yQ", "isbns": isbns})

    title = db.execute("SELECT title FROM books WHERE isbn = :isbn",
        {"isbn": isbns}).fetchone()[0]
    author = db.execute("SELECT author FROM books WHERE isbn = :isbn",
        {"isbn": isbns}).fetchone()[0]
    year = db.execute("SELECT year FROM books WHERE isbn = :isbn",
        {"isbn": isbns}).fetchone()[0]

    data = res.json()
    parsed_data = json.dumps(data)
    reviews = data.get("books")

    totalrating = (reviews[0].get("reviews_count"))
    avgrating = (reviews[0].get("average_rating"))

    return jsonify({
        "title": title,
        "author": author,
        "isbn": isbn,
        "year": year,
        "review_count": totalrating,
        "average_score": avgrating
    })
