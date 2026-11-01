from flask import render_template, request, redirect, url_for, session

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Yahan aapka vault check ya validation hoga...
    # Agar login successful ho jaye, toh session set karke seedha dashboard bhejiye:
    
    session['user'] = username
    return redirect(url_for('dashboard'))  # <-- Yeh line honi zaroori hai!

@app.route('/dashboard')
def dashboard():
    # Check kariye ki user logged-in hai ya nahi
    if 'user' not in session:
        return redirect(url_for('home')) # Agar login nahi hai toh home bhej do
    
    return render_template('dashboard.html') # Agar login hai toh dashboard dikhao