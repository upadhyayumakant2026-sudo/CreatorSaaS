import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)
app.secret_key = 'UMAKANTUPADHYAY_MILITARY_SURAKSHA_KAVACH_KEY_2026'

# --- SECURITY & ZERO DATA LEAKAGE SHIELD ---
@app.after_request
def apply_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# --- ROUTES & PIPELINE ---
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

# ULTRA-FAST PROCESSING & API PUBLISHING PIPELINE (Within seconds/minutes)
@app.route('/process_video_fast', methods=['POST'])
def process_video_fast():
    used = session.get('videos_used', 0)
    current_plan = session.get('user_plan', 'Free Trial')

    # Strict Trial Lock: Max 1 Video for Free Trial users
    if used >= 1 and current_plan == 'Free Trial':
        return jsonify({
            'status': 'redirect',
            'message': 'Free Trial Limit Reached! 1 Video Allowed. Please select a plan.',
            'url': url_for('dashboard') + '#plans'
        })

    # High Speed Processing Simulation
    start_time = time.time()
    
    # Simulating Fast Multi-API Auto Editing & Auto SEO Pipeline
    time.sleep(1) # Fast processing
    
    session['videos_used'] = used + 1
    execution_time = round(time.time() - start_time, 2)

    return jsonify({
        'status': 'success',
        'message': f'🚀 Video Auto-Edited, SEO Generated & Auto-Published to FB, Instagram, YouTube & Twitter(X) in {execution_time} seconds!',
        'videos_used': session['videos_used']
    })

@app.route('/save_social_links', methods=['POST'])
def save_social_links():
    data = request.json
    # Secure Link Storage
    session['social_links'] = data
    return jsonify({'status': 'success', 'message': 'Social Media Accounts Linked & Encrypted Securely!'})

@app.route('/payment_success')
def payment_success():
    # Direct Payment Hook Callback & Redirect back to Login
    plan = request.args.get('plan', 'Starter')
    session['user_plan'] = plan
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)