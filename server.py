from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt

app=Flask(__name__)
mysql = MySQLConnector(app,'walldb')
app.secret_key="SecretGarden"
bcrypt = Bcrypt(app)

import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
Name_REGEX = re.compile(r'^[a-zA-Z]+$')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def log():
    
    validation = True

    if len(request.form['passwordlog']) < 1:
        flash("You must enter your password")
        validation = False
    if len(request.form['usernamelog']) < 1:
        flash("You must enter your username")
        validation = False
    
    if validation:
        query = "SELECT * FROM users WHERE username = :username "
        data = {
            "username": request.form['usernamelog']
        }

        entry = mysql.query_db(query, data)
        
        if not entry:
            flash("Incorrect username Entered")
            return redirect('/')

        if bcrypt.check_password_hash(entry[0]['password'],request.form['passwordlog']) == False :
            flash("Incorrect Password Entered")
            return redirect('/')
        else:
            
            session['user_id'] = entry[0]['id']
            print session['user_id']
            return redirect("/the_wall")
        
    return redirect("/")
 
@app.route('/register', methods=['POST'])
def register():
    
    validation = True
    if len(request.form['first']) < 1:
        flash("First Name cannot be empty!")
        validation = False
    if not request.form['first'].isalpha():
        flash("First Fame can only include letters")
        validation = False
    if len(request.form['last']) < 1:
        flash("Last Name cannot be empty!")
        validation = False
    if not request.form['last'].isalpha():
        flash("Last Name can only include letters")
        validation = False
    if len(request.form['email']) < 1:
        flash("Email cannot be empty")
        validation = False
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Not a valid Email address")
        validation = False
    if len(request.form['password']) < 1:
        flash("Password is required.")
        validation = False
    if len(request.form['password']) < 8:
        flash("Password must be longer than 8 characters")
        validation = False
    if len(request.form['confirm']) < 1:
        flash("Password  Confirmation is required.")
        validation = False
    if not request.form['password'] == request.form['confirm']:
        flash("Password Confirmation does not enter Password")
        validation = False 
    
    if validation:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print pw_hash

        query = "INSERT INTO users(first_name,last_name,username,email,password,created_at,updated_at) VALUES(:first, :last, :username, :email, :pw_hash, NOW(), NOW())"
        print query

        data = {
            'first': request.form['first'],
            'last': request.form['last'],
            'username': request.form['username'],
            'email': request.form['email'],
            'pw_hash': pw_hash
        }

        session['user_id'] = mysql.query_db(query,data)

        return redirect("/the_wall")
    else:
        return redirect("/")

    
@app.route("/the_wall")
def the_wall():
    
    m_query = "SELECT message, messages.id, messages.created_at, users.id as user_id, first_name, last_name FROM messages LEFT JOIN users ON messages.user_id = users.id ORDER BY messages.created_at DESC"
    messages = mysql.query_db(m_query)
    print messages 

    c_query = "SELECT comment, comments.created_at, comments.id as comment_id, comments.message_id, users.id as user_id, first_name, last_name FROM messages JOIN comments ON messages.id = comments.message_id JOIN users ON comments.user_id = users.id ORDER BY comments.created_at ASC"

    comments = mysql.query_db(c_query)
    print comments
   
    query3 = "SELECT users.first_name FROM users WHERE id = :user_id"
    data = {
        "user_id": session['user_id']
    }
    hello = mysql.query_db(query3,data)
    greeting = hello[0]['first_name']


    return render_template("wall.html", greeting=greeting, messages=messages, comments=comments)

@app.route("/add_message", methods=['POST'])
def add_message():
    query = "INSERT INTO messages (message, user_id, created_at, updated_at) VALUES (:message, :user_id, NOW(), NOW())"
    data = {
        "message": request.form['message'], 
        "user_id": session['user_id']
    }

    mysql.query_db(query, data)

    return redirect("/the_wall")

@app.route("/add_comment/<message_id>", methods=['POST'])
def add_comment(message_id):
    print "test"
    query = "INSERT into comments (comment, created_at, updated_at, message_id, user_id) VALUE (:comment, NOW(), NOW(), :message_id, :user_id)"
    print "test"
    data = {
        'comment': request.form['commentarea'],
        'message_id': message_id,
        'user_id': session['user_id']
    }

    mysql.query_db(query,data)
    print "test"
    return redirect("/the_wall")


@app.route('/delete/<message_id>')
def delete(message_id):
	delete_query = "DELETE FROM messages WHERE id = :message_id"
	delete_query2 = "DELETE FROM comments WHERE message_id = :message_id"
	data = {'message_id': message_id}
	mysql.query_db(delete_query2, data)
	mysql.query_db(delete_query, data)
	return redirect('/the_wall')

@app.route('/delete/add_comment/<comment_id>')
def delete_comment(comment_id):
	delete_query = "DELETE FROM comments WHERE id = :comment_id"
	data = {'comment_id': comment_id}
	mysql.query_db(delete_query, data)
	return redirect('/the_wall')


        
@app.route('/logout')
def logout():
    session.clear()
    print "Bye!"
    return redirect ('/')

app.run(debug=True)