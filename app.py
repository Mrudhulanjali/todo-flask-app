from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a random secret key
bcrypt = Bcrypt(app)

# MongoDB Atlas Configuration
app.config["MONGO_URI"] = "mongodb+srv://daarlabhanumurthy:bhanu1234@tododb.2gyhvmr.mongodb.net/todoDB?retryWrites=true&w=majority"
app.config['MONGO_SSL'] = True  # Required for Atlas
app.config['MONGO_SSL_CERT_REQS'] = None  # Helps with SSL issues

mongo = PyMongo(app)

# Test MongoDB Connection
try:
    mongo.db.command('ping')
    print("✓ Successfully connected to MongoDB Atlas")
except Exception as e:
    print(f"✗ Connection failed: {e}")

# Routes
@app.route('/')
def index():
    if 'username' in session:
        tasks = mongo.db.tasks.find({'user': session['username']})
        return render_template('index.html', tasks=tasks)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username': request.form['username']})
        
        if existing_user:
            return "Username already exists!"
        
        hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        users.insert_one({
            'username': request.form['username'],
            'password': hashed_password
        })
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username': request.form['username']})
        
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return "Invalid username or password"
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_task():
    if 'username' in session:
        task_content = request.form['content']
        mongo.db.tasks.insert_one({
            'content': task_content,
            'user': session['username'],
            'completed': False
        })
    return redirect(url_for('index'))

@app.route('/delete/<task_id>')
def delete_task(task_id):
    if 'username' in session:
        mongo.db.tasks.delete_one({'_id': ObjectId(task_id), 'user': session['username']})
    return redirect(url_for('index'))

@app.route('/complete/<task_id>')
def complete_task(task_id):
    if 'username' in session:
        mongo.db.tasks.update_one(
            {'_id': ObjectId(task_id), 'user': session['username']},
            {'$set': {'completed': True}}
        )
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)