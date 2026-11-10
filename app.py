import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'creatorsaas_master_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        session['user'] = username if username else 'upadhyayumakant2026@gmail.com'
        if 'videos_used' not in session:
            session['videos_used'] = 0
        if 'user_plan' not in session:
            session['user_plan'] = 'Free Trial'
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html')

@app.route('/process_video', methods=['POST'])
def process_video():
    used = session.get('videos_used', 0)
    if used >= 1 and session.get('user_plan') == 'Free Trial':
        return jsonify({'status': 'redirect', 'url': url_for('dashboard') + '#plans'})
    session['videos_used'] = used + 1
    return jsonify({'status': 'success', 'message': 'Video Processed Successfully!'})

@app.route('/payment_success')
def payment_success():
    # Direct redirect back to login upon payment completion
    plan_type = request.args.get('plan', 'Starter')
    session['user_plan'] = plan_type
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)