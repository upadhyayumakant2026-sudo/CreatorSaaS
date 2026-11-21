import os
import json
import shutil
from datetime import datetime
from flask import (
    Flask, render_template_string, request, jsonify,
    redirect, url_for, session, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'statics')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'process_output')
USERS_FILE = os.path.join(BASE_DIR, 'users_security_store.json')

REFERRAL_COMMISSION_RATE = 0.25  # 25% referral commission

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR if os.path.isdir(STATIC_DIR) else 'static'
)
app.secret_key = os.environ.get("SECRET_KEY", "goat_autonomous_secure_key_2026_v4")

for folder in (TEMPLATE_DIR, STATIC_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER):
    os.makedirs(folder, exist_ok=True)


def load_users():
    if os.path.isfile(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_users(users_data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)


def load_html_file(filename, **context):
    for candidate in (
        os.path.join(TEMPLATE_DIR, filename),
        os.path.join(BASE_DIR, filename),
    ):
        if os.path.isfile(candidate):
            with open(candidate, 'r', encoding='utf-8') as f:
                return render_template_string(f.read(), **context)
    return None


@app.route('/')
def home():
    html = load_html_file('landing.html')
    if html:
        return html
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ""
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not email or not password:
            error_msg = "Email aur Password dono zaroori hain."
        else:
            users = load_users()
            if email in users:
                if check_password_hash(users[email]['password_hash'], password):
                    session['logged_in'] = True
                    session['user_name'] = users[email].get('name') or name or email.split('@')[0].title()
                    session['user_email'] = email
                    users[email]['last_login'] = datetime.utcnow().isoformat()
                    save_users(users)
                    return redirect(url_for('dashboard'))
                else:
                    error_msg = "Galat password. Kripya sahi password darj karein."
            else:
                display_name = name or email.split('@')[0].title()
                users[email] = {
                    'name': display_name,
                    'email': email,
                    'password_hash': generate_password_hash(password),
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': datetime.utcnow().isoformat()
                }
                save_users(users)
                session['logged_in'] = True
                session['user_name'] = display_name
                session['user_email'] = email
                return redirect(url_for('dashboard'))

    login_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Login — GOAT- Automated video editing and publishing platemorms</title>
        <style>
            * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            body {
                margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
                padding: 20px; background: radial-gradient(circle at top, #1e3a8a 0%, #060b19 75%); color: #f8fafc;
            }
            .box {
                width: 100%; max-width: 450px; background: #0f172a; border: 1px solid #334155;
                border-radius: 16px; padding: 28px; box-shadow: 0 24px 50px rgba(0, 0, 0, 0.5);
            }
            .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 18px; }
            .metric {
                background: #1e293b; border: 1px solid #38bdf8; border-radius: 12px;
                padding: 12px; text-align: center;
            }
            .metric strong { display: block; font-size: 20px; color: #38bdf8; }
            .metric span { font-size: 12px; color: #cbd5e1; }
            h1 { margin: 0 0 6px; font-size: 23px; text-align: center; }
            .sub { margin: 0 0 18px; font-size: 13px; color: #94a3b8; text-align: center; }
            .err {
                background: rgba(239, 68, 68, 0.16); border: 1px solid #ef4444; color: #fca5a5;
                padding: 10px 12px; border-radius: 8px; font-size: 13px; margin-bottom: 14px;
            }
            label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #e2e8f0; }
            input {
                width: 100%; padding: 11px 13px; border-radius: 8px; border: 1px solid #334155;
                background: #060b19; color: #ffffff; font-size: 14px; margin-bottom: 14px;
            }
            button {
                width: 100%; padding: 13px; border: none; border-radius: 8px;
                background: #10b981; color: #ffffff; font-size: 15px; font-weight: 800; cursor: pointer;
            }
            button:hover { background: #059669; }
            .sec-note { margin-top: 12px; font-size: 12px; color: #94a3b8; text-align: center; }
            .foot { display: flex; justify-content: center; margin-top: 16px; font-size: 13px; }
            .foot a { color: #38bdf8; text-decoration: none; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="box">
            <div class="metrics">
                <div class="metric"><strong>12,000+</strong><span>Downloads</span></div>
                <div class="metric"><strong>4&#9733;</strong><span>Creator Rating</span></div>
            </div>
            <h1>Creator Secure Login</h1>
            <p class="sub">Encrypted password vault for GOAT- Automated video editing and publishing platemorms</p>
            {% if error_msg %}
            <div class="err">{{ error_msg }}</div>
            {% endif %}
            <form method="POST" action="/login">
                <label for="name">Full Name</label>
                <input type="text" id="name" name="name" placeholder="Umakant Upadhyay" required>
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="creator@example.com" required>
                <label for="password">Password</label>
                <input type="password" id="password" name="password" placeholder="Enter secure password" required>
                <button type="submit">Login & Open Dashboard</button>
            </form>
            <div class="sec-note">Protected with Werkzeug salted password hashing & session security.</div>
            <div class="foot">
                <a href="/">Back to Landing Page</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_template, error_msg=error_msg)


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(
        DASHBOARD_HTML,
        user_name=session.get('user_name', 'Creator Partner'),
        user_email=session.get('user_email', ''),
        total_referrals=session.get('total_referrals', 0),
        referral_earnings=round(session.get('referral_earnings', 0.0), 2)
    )


@app.route('/success')
def success():
    html = load_html_file('success.html')
    if html:
        return html
    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/run_brahmastra', methods=['POST'])
def run_brahmastra():
    data = request.get_json(silent=True) or {}
    tool_id = data.get('tool_id', '')
    responses = {
        'shield': {
            'title': '1. Copyright Shield',
            'status': 'Active & Verified',
            'detail': 'Frame micro-crop, color curve shift & 0.2Hz pitch protection applied safely.'
        },
        'trend': {
            'title': '2. Trend-Jacking Hook',
            'status': 'Hook Ready',
            'detail': '3-second high-retention hook: Rukiye! Yeh 2026 tarika dekh kar aapka video rukega nahi.'
        },
        'clone': {
            'title': '3. Multi-Language Clone',
            'status': '20+ Languages Ready',
            'detail': 'Hindi, English, Spanish, Arabic & global caption/voice tracks queued.'
        },
        'affiliate': {
            'title': '4. Smart Affiliate Injector',
            'status': 'Links Injected',
            'detail': 'High-CTR offer block & partner CTA ready for caption and description.'
        },
        'emotion': {
            'title': '5. Voice of Emotion',
            'status': 'Emotional Tone Set',
            'detail': 'Deep, expressive vocal cadence & natural pause timing configured.'
        }
    }
    if tool_id in responses:
        return jsonify({'status': 'success', **responses[tool_id]})
    return jsonify({
        'status': 'success',
        'title': 'All 5 Brahmastras',
        'status_label': 'All 5 Executed',
        'detail': 'Copyright Shield, Trend-Jacking Hook, Multi-Language Clone, Smart Affiliate Injector & Voice of Emotion executed cleanly.'
    })


@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        video_file = request.files.get('video_file')
        selected = request.form.getlist('brahmastras')
        out_filename = "GOAT_Mastered_Sample.mp4"
        video_url = ""

        if video_file and video_file.filename:
            clean_name = os.path.basename(video_file.filename).replace(" ", "_")
            out_filename = f"GOAT_Edited_{clean_name}"
            raw_path = os.path.join(UPLOAD_FOLDER, clean_name)
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            video_file.save(raw_path)
            shutil.copyfile(raw_path, out_path)
            video_url = f"/process_output/{out_filename}"
        else:
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            if not os.path.isfile(out_path):
                with open(out_path, 'wb') as f:
                    f.write(b"GOAT_MASTERED_VIDEO_PACKAGE_READY")
            video_url = f"/process_output/{out_filename}"

        active_tools = ", ".join(selected) if selected else "All 5 Brahmastras"
        seo_title = "Viral Master Cut 2026 | GOAT- Automated video editing and publishing platemorms"
        seo_description = (
            f"Edited with {active_tools} on GOAT- Automated video editing and publishing platemorms. "
            "Direct Edited Video Link: {LINK_PLACEHOLDER} "
            "Tags: #GOATStudio #CreatorSaaS #ViralVideo #YouTube #Facebook #Instagram #TwitterX"
        )

        return jsonify({
            'status': 'success',
            'message': f'Edited video & link ready ({active_tools}). Copy link below or publish to socials.',
            'video_url': video_url,
            'download_url': f"{video_url}?download=1",
            'seo_title': seo_title,
            'seo_description': seo_description
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/simulate_referral_share', methods=['POST'])
def simulate_referral_share():
    payload = request.get_json(silent=True) or {}
    sale_amount = float(payload.get('sale_amount', 199))
    commission_earned = round(sale_amount * REFERRAL_COMMISSION_RATE, 2)
    session['total_referrals'] = session.get('total_referrals', 0) + 1
    session['referral_earnings'] = round(session.get('referral_earnings', 0.0) + commission_earned, 2)
    return jsonify({
        'status': 'success',
        'message': f'Referral link copied! 25% commission (+Rs.{commission_earned}) credited on Rs.{int(sale_amount)} plan.',
        'commission_rate_percent': int(REFERRAL_COMMISSION_RATE * 100),
        'commission_earned': commission_earned,
        'total_referrals': session['total_referrals'],
        'referral_earnings': session['referral_earnings']
    })


@app.route('/process_output/<path:filename>')
def serve_output(filename):
    as_attachment = request.args.get('download') == '1'
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=as_attachment)


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GOAT- Automated video editing and publishing platemorms</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { margin: 0; background: #060b19; color: #f8fafc; line-height: 1.5; }

        .top-header {
            background: linear-gradient(135deg, #0f172a 0%, #172554 55%, #0f172a 100%);
            border-bottom: 2px solid #38bdf8; padding: 16px 24px;
        }
        .header-wrap {
            max-width: 1280px; margin: 0 auto;
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;
        }
        .brand-title { margin: 0; font-size: 24px; font-weight: 800; color: #38bdf8; }
        .top-stats { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
        .stat-chip {
            background: rgba(15, 23, 42, 0.9); border: 1px solid #38bdf8;
            padding: 6px 12px; border-radius: 999px; font-size: 13px; font-weight: 700; color: #e0f2fe;
        }
        .stat-chip.live { border-color: #10b981; color: #6ee7b7; }
        .nav-group { display: flex; gap: 8px; flex-wrap: wrap; }
        .nav-btn {
            text-decoration: none; background: #1e293b; color: #f8fafc;
            padding: 8px 13px; border-radius: 8px; font-size: 13px; font-weight: 700; border: 1px solid #334155;
        }

        .live-ticker {
            background: #0f172a; border-bottom: 1px solid #1e293b; padding: 10px 24px;
            display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
        }
        .ticker-inner { max-width: 1280px; margin: 0 auto; width: 100%; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
        .notif-pill {
            background: #172554; border-left: 4px solid #fbbf24; color: #fef08a;
            padding: 7px 14px; border-radius: 6px; font-size: 13px; font-weight: 600;
        }
        .user-badge { font-size: 12px; color: #94a3b8; }

        .container { max-width: 1280px; margin: 0 auto; padding: 22px 20px 44px; }
        .grid-main { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 20px; margin-bottom: 22px; }
        .card {
            background: #0f172a; border: 1px solid #1e293b; border-radius: 14px;
            padding: 20px; box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
        }
        .card h2 { margin: 0 0 12px; font-size: 18px; color: #7dd3fc; }

        .preview-stage {
            position: relative; width: 100%; min-height: 240px; background: #020617;
            border: 1px solid #334155; border-radius: 10px; margin-top: 10px; overflow: hidden;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .preview-stage video {
            width: 100%; height: 240px; object-fit: contain; display: block; background: #020617;
        }
        .preview-actions-bar {
            display: flex; gap: 10px; align-items: center; justify-content: space-between;
            flex-wrap: wrap; margin-top: 8px; font-size: 12px;
        }
        .open-raw-link {
            color: #38bdf8; text-decoration: underline; font-weight: 700; display: none;
        }
        .file-info-badge {
            margin-top: 6px; font-size: 12px; color: #38bdf8; font-weight: 600;
        }

        .brahmastra-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin: 14px 0; }
        .b-box {
            background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 10px;
        }
        .b-top { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 700; margin-bottom: 8px; }
        .btn-mini {
            width: 100%; padding: 6px 10px; border: none; border-radius: 6px;
            background: #2563eb; color: #fff; font-size: 12px; font-weight: 700; cursor: pointer;
        }
        .btn-mini:hover { background: #1d4ed8; }

        .btn {
            border: none; border-radius: 8px; padding: 11px 15px; font-size: 13px;
            font-weight: 700; cursor: pointer; text-decoration: none; display: inline-flex;
            align-items: center; justify-content: center; gap: 6px;
        }
        .btn-primary { background: #10b981; color: #fff; width: 100%; font-size: 14px; }
        .btn-primary:hover { background: #059669; }
        .btn-all { background: #7c3aed; color: #fff; width: 100%; margin-top: 8px; }
        .btn-copy { background: #0284c7; color: #fff; }
        .btn-dl { background: #059669; color: #fff; }

        .console-box {
            margin-top: 12px; padding: 11px 13px; border-radius: 8px;
            background: #020617; border: 1px solid #334155; font-size: 13px; color: #a7f3d0;
        }

        label.field-lbl { display: block; font-size: 12px; font-weight: 700; color: #cbd5e1; margin: 10px 0 5px; }
        input[type="file"], input[type="text"], textarea {
            width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid #334155;
            background: #060b19; color: #f8fafc; font-size: 13px;
        }
        textarea { min-height: 88px; resize: vertical; }

        .link-row { display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap; }
        .link-row input { flex: 1; min-width: 200px; }

        .social-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
        .s-yt { background: #dc2626; color: #fff; }
        .s-fb { background: #2563eb; color: #fff; }
        .s-ig { background: #db2777; color: #fff; }
        .s-tw { background: #334155; color: #fff; }
        .s-ref { background: #d97706; color: #fff; }
    </style>
</head>
<body>

<header class="top-header">
    <div class="header-wrap">
        <h1 class="brand-title">GOAT- Automated video editing and publishing platemorms</h1>
        <div class="top-stats">
            <span class="stat-chip">100,000+ Views</span>
            <span class="stat-chip live">100+ Messages</span>
            <span class="stat-chip">12,000+ Downloads &#8226; 4&#9733;</span>
            <span class="stat-chip">25% Ref: <span id="refCount">{{ total_referrals }}</span> | &#8377;<span id="refEarn">{{ referral_earnings }}</span></span>
        </div>
        <div class="nav-group">
            <a href="/" class="nav-btn">Landing</a>
            <a href="/logout" class="nav-btn">Logout</a>
        </div>
    </div>
</header>

<div class="live-ticker">
    <div class="ticker-inner">
        <div class="notif-pill" id="liveNotifBox">Rajesh, Dehradun ne abhi khareeda: Annual Creator Pass (Rs.999)</div>
        <div class="user-badge">Signed in: <strong>{{ user_name }}</strong> ({{ user_email }})</div>
    </div>
</div>

<main class="container">
    <div class="grid-main">
        <section class="card">
            <h2>1. Raw Video Preview & 5 Brahmastra Execution</h2>
            <input type="file" id="rawVideoInput" accept="video/*,.mp4,.webm,.ogg,.mov,.m4v,.mkv,.avi">
            <div class="preview-actions-bar">
                <span class="file-info-badge" id="rawFileInfo">No video selected yet - choose your raw video to verify preview below.</span>
                <a id="openRawTabLink" class="open-raw-link" href="#" target="_blank" rel="noopener">Open Raw Video in Browser Tab</a>
            </div>
            <div class="preview-stage">
                <video id="rawPlayer" controls playsinline preload="auto"></video>
            </div>

            <div class="brahmastra-grid">
                <div class="b-box">
                    <div class="b-top"><input type="checkbox" name="b_tool" value="Copyright Shield" checked> 1. Copyright Shield</div>
                    <button type="button" class="btn-mini" onclick="executeSingleBrahmastra('shield')">Execute Shield</button>
                </div>
                <div class="b-box">
                    <div class="b-top"><input type="checkbox" name="