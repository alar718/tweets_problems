from flask import Flask, session, request, redirect, render_template, flash
from mysqlconnection import connectToMySQL

app=Flask(__name__)
app.secret_key = 'keep it secret'

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


@app.route('/reg/post', methods=['POST'])
def post_method():
    is_valid = True
    if len(request.form['fname']) < 1:
        is_valid = False
        flash("Please enter a FIRST NAME")
    if len(request.form['lname']) < 1:
        is_valid = False
        flash("Please enter a LAST NAME")
    if len(request.form['emil']) < 1:
        is_valid = False
        flash("Please enter an EMAIL")
    if not EMAIL_REGEX.match(request.form['emil']):
        is_valid = False
        flash("Invalid email address format")
    if len(request.form['pwd']) < 5:
        is_valid = False
        flash("Password must be 5 or more characters")
    if (request.form['pwd'] != request.form['pwd2']):
        is_valid = False
        flash("Passwords do not match!")

    if is_valid:
        mysql = connectToMySQL('basic_registration')
        pw_hash = bcrypt.generate_password_hash(request.form['pwd'])
        query = 'INSERT INTO users (first_name, last_name, email, password) VALUES(%(fnm)s, %(lnm)s, %(eml)s, %(psw)s)'
        data = {
            "fnm": request.form['fname'],
            "lnm": request.form['lname'],
            "eml": request.form['emil'],
            "psw": pw_hash
        }
        mysql.query_db(query, data)
        flash("You've Successfully Added a Friend!")

    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    mysql = connectToMySQL('basic_registration')
    query = 'SELECT * FROM users WHERE email = %(eml)s;'
    data = {
        "eml": request.form['emil2']
    }
    user = mysql.query_db(query, data)

    if user:
        session['userid'] = user[0]['id']
        session['usereml'] = user[0]['email']
        session['user_first'] = user[0]['first_name']
        session['user_last'] = user[0]['last_name']
        hashed_pw = user[0]['password']
        if bcrypt.check_password_hash(hashed_pw, request.form['pwd3']):
            session['logged_in'] = True
            flash("Thanks for logging in")
            return redirect('/welcome')
        else:
            session['logged_in'] = False
            flash("Login failed. Please try again or regisweter.")
            return redirect('/')
    else:
        flash("Your email could not be found. Please retry or register.")
        return redirect('/')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash("You are now logged out. Come back soon!")
    session.clear()
    return redirect('/')

@app.route('/welcome')
def welcome():
    if not session['logged_in']:
        flash("You're not logged in. Please login or register")
        return redirect('/')
    else:
        mysql = connectToMySQL('basic_registration')
        tweets = mysql.query_db('SELECT * FROM tweets ORDER BY created_at DESC;')
        return render_template('welcome.html', tweetz = tweets)

@app.route('/welcome/tweet', methods=['POST'])
def welcome_tweet():
    mysql = connectToMySQL('basic_registration')
    query = 'INSERT INTO tweets (first_name, last_name, tweet_content) VALUES (%(fnm)s, %(lnm)s, %(_twt)s);'
    data = {
        "fnm": session['user_first'],
        "lnm": session['user_last'],
        "_twt": request.form['twtbox']
    }
    mysql.query_db(query, data)
    return redirect('/welcome')



# @app.route('/login')
# def log_in():
#     mysql = connectToMySQL('basic_registration')
#     query = 'SELECT * FROM users;'
#     mysql.query_db(query)
#     if request.info['emil2'] == users.email:

#     return redirect('/')

if __name__ == ('__main__'):
    app.run(debug=True)