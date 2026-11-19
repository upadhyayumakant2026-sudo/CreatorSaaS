import os
import shutil
from flask import (
    Flask, render_template_string, request, jsonify,
    redirect, url_for, session, send_from_directory
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'statics')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'process_output')

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR if os.path.isdir(STATIC_DIR) else 'static'
)
app.secret_key = "goat_creatorsaas_secret_2026"

for folder in (TEMPLATE_DIR, STATIC_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER):
    os.makedirs(folder, exist_ok=True)


def load_html(filename, **context):
    for path in (os.path.join(TEMPLATE_DIR, filename), os.path.join(BASE_DIR, filename)):
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                return render_template_string(f.read(), **context)
    return render_template_string(
        "<h3>File not found: {{ fname }}</h3><a href='/'>Home</a> | <a href='/login'>Login</a> | <a href='/dashboard'>Dashboard</a>",
        fname=filename
    )


@app.route('/')
def home():
    return load_html('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip()
        session['logged_in'] = True
        session['user_name'] = name or (email.split('@')[0].title() if email else 'Creator')
        session['user_email'] = email or 'creator@goatstudio.in'
        return redirect(url_for('dashboard'))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login — GOAT- Automated video editing and publishing platemorms</title>
        <style>
            * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body {
                margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
                padding: 20px; background: #070d1d; color: #f8fafc;
            }
            .card {
                width: 100%; max-width: 430px; background: #0f172a; border: 1px solid #334155;
                border-radius: 14px; padding: 28px;
            }
            .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
            .stat { background: #1e293b; border: 1px solid #38bdf8; border-radius: 10px; padding: 12px; text-align: center; }
            .stat b { display: block; font-size: 20px; color: #38bdf8; }
            .stat span { font-size: 12px; color: #cbd5e1; }
            h1 { margin: 0 0 18px; font-size: 22px; text-align: center; }
            label { display: block; font-size: 13px; margin-bottom: 6px; color: #e2e8f0; }
            input {
                width: 100%; padding: 11px 12px; border-radius: 8px; border: 1px solid #334155;
                background: #070d1d; color: #fff; margin-bottom: 14px; font-size: 14px;
            }
            button {
                width: 100%; padding: 12px; border: none; border-radius: 8px;
                background: #10b981; color: #fff; font-size: 15px; font-weight: 700; cursor: pointer;
            }
            .nav { display: flex; justify-content: space-between; margin-top: 16px; font-size: 13px; }
            .nav a { color: #38bdf8; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="stats">
                <div class="stat"><b>12,000+</b><span>Downloads</span></div>
                <div class="stat"><b>4★</b><span>Rating</span></div>
            </div>
            <h1>Creator Login</h1>
            <form method="POST" action="/login">
                <label>Name</label>
                <input type="text" name="name" placeholder="Your Name" required>
                <label>Email</label>
                <input type="email" name="email" placeholder="you@example.com" required>
                <button type="submit">Login to Dashboard</button>
            </form>
            <div class="nav">
                <a href="/">Landing (landing.html)</a>
                <a href="/dashboard">Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.route('/dashboard')
def dashboard():
    return load_html(
        'dashboard.html',
        user_name=session.get('user_name', 'Creator'),
        total_referrals=session.get('total_referrals', 0),
        referral_earnings=session.get('referral_earnings', 0)
    )


@app.route('/success')
def success():
    return load_html('success.html')


@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        video_file = request.files.get('video_file')
        selected = request.form.getlist('brahmastras')
        out_name = "GOAT_Mastered_Video.mp4"
        video_url = ""

        if video_file and video_file.filename:
            clean = os.path.basename(video_file.filename)
            out_name = f"mastered_{clean}"
            raw_path = os.path.join(UPLOAD_FOLDER, clean)
            out_path = os.path.join(OUTPUT_FOLDER, out_name)
            video_file.save(raw_path)
            shutil.copyfile(raw_path, out_path)
            video_url = f"/process_output/{out_name}"

        active = ", ".join(selected) if selected else "All 5 Brahmastras"
        return jsonify({
            'status': 'success',
            'message': f'Processed with {active}.',
            'video_url': video_url,
            'seo_title': 'Viral Video 2026 | GOAT- Automated video editing and publishing platemorms',
            'seo_description': 'Edited and prepared for YouTube, Facebook, Instagram, and X. #GOAT #VideoEditing #CreatorSaaS'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/simulate_referral_share', methods=['POST'])
def simulate_referral_share():
    session['total_referrals'] = session.get('total_referrals', 0) + 1
    session['referral_earnings'] = session.get('referral_earnings', 0) + 125
    return jsonify({
        'message': 'Referral link copied (+₹125).',
        'total_referrals': session['total_referrals'],
        'referral_earnings': session['referral_earnings']
    })


@app.route('/process_output/<path:filename>')
def get_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)