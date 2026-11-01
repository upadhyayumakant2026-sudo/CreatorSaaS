import json
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'creatorsaas_secret_key_123'  # Session active rakhne ke liye zaroori hai

# 1. Main Home / Landing Page
@app.route('/')
def home():
    return render_template('index.html')

# 2. Login Handle Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vault file check
        vault_path = 'secure_users_vault.json'
        if os.path.exists(vault_path):
            with open(vault_path, 'r') as f:
                vault = json.load(f)
                if username in vault and vault[username] == password:
                    session['user'] = username
                    return redirect(url_for('dashboard'))
        
        # Bypass check for testing: agar vault na mile ya validation fail ho tab bhi demo ke liye dashboard jane do
        session['user'] = username if username else 'creator_user'
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('home'))

# 3. Main Dashboard Route (Direct Access Allowed)
@app.route('/dashboard')
def dashboard():
    # Dashboard hamesha khulne do taaki aapka kaam na ruke
    username = session.get('user', 'Creator Admin')
    return render_template('dashboard.html', username=username)

if __name__ == '__main__':
    app.run(debug=True, port=5001)