# BookReview

This application was made for project 1 of HarvardX: CS50W
CS50's Web Programming with Python and JavaScript.

To get the app to work, you must export environment variables, FLASK_APP=application.py
& DATABASE_URL=postgres://ciavsuokdemeps:5d851a73c4d439092f560d1f5a8ae980d3d5cd354411d40649519c36bbbdb3e0@ec2-34-206-31-217.compute-1.amazonaws.com:5432/d89d5opnllrl2b before running flask.

Once started, the first page provides the ability for the user to register or login
to the application. Before logging in, you have to create an account by clicking the register
button which will take the user to a registration page. From there, the user can fill out
the various fields and create an account which insert the users information into a database
called users. Once a user has created an account, they can enter their credentials on the
initial page and login.

Once a user is logged in, they will see a search page where they can enter an author,
title, or isbn. Once a user clicks the search button, the search result will go through
the books database and display all of the matches in a list. The search will work with
partial entries but the search is case-sensitive.

The user then has the ability to click on one of the list options which will bring the
user to a new page that lists the information of the book, review information from the
goodreads API, and any reviews that have been made using the application. The user has
the ability to fill out a review for the book and rate it out of five. 
