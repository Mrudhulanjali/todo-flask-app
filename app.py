from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)
import os

app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb+srv://todouser:todoPass123@cluster0.omakqvn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

mongo = PyMongo(app)

# Routes

@app.route('/')
def index():
    if 'username' in session:
        tasks = mongo.db.tasks.find({'user': session['username']})
        return render_template('index.html', tasks=tasks)
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        if existing_user:
            return "User already exists!"
        hashpass = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        users.insert_one({'username': request.form['username'], 'password': hashpass})
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username': request.form['username']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            session['username'] = request.form['username']
            return redirect('/')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/add', methods=['POST'])
def add_task():
    if 'username' in session:
        task_content = request.form['content']
        mongo.db.tasks.insert_one({'content': task_content, 'user': session['username']})
    return redirect('/')

@app.route('/delete/<task_id>')
def delete_task(task_id):
    mongo.db.tasks.delete_one({'_id': ObjectId(task_id)})
    return redirect('/')
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
