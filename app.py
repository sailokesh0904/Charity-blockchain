from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
from blockchain import Blockchain
from zkp import ZKPTransaction

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Initialize Blockchain
blockchain = Blockchain()

# Load user data
USER_DATA_FILE = 'users.json'
try:
    with open(USER_DATA_FILE, 'r') as file:
        users = json.load(file)
except FileNotFoundError:
    users = {}

# Helper function to save users
def save_users():
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(users, file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        if user_id in users:
            flash('User ID already exists.')
            return redirect('/register')
        
        # Hash the password and store it
        users[user_id] = generate_password_hash(password)
        save_users()
        flash('Registration successful. Please log in.')
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        
        if user_id not in users or not check_password_hash(users[user_id], password):
            flash('Invalid user ID or password.')
            return redirect('/login')
        
        session['user_id'] = user_id
        flash('Login successful.')
        return redirect('/donate')
    
    return render_template('login.html')

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if 'user_id' not in session:
        flash('You must log in to donate.')
        return redirect('/login')

    if request.method == 'POST':
        charity = request.form['charity']
        donation_amount = int(request.form['donation_amount'])
        user_id = session['user_id']
        
        # Generate a ZKP for the user's password
        p = int(request.form['p'])
        g = int(request.form['g'])
        transaction = ZKPTransaction(user_id, donation_amount, charity, p, g)
        
        transaction.create_proof()
        transaction.receive_challenge()
        transaction.send_response()
        
        if transaction.verify_proof():
            blockchain.add_transaction(user_id, donation_amount, charity, p, g)  # Matches the method
            blockchain.mine_block(miner_address="network")
            flash('Donation successful.')
        else:
            flash('ZKP verification failed. Donation not recorded.')
        
        return redirect('/donate')
    
    return render_template('donate.html', charities=["Orphanage", "Red Cross", "WWF"])



@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash('You must log in to view your transactions.')
        return redirect('/login')

    user_id = session['user_id']
    user_transactions = blockchain.view_user(user_id)
    return render_template('transactions.html', transactions=user_transactions)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
