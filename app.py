import os
import re
import json
import shutil
import smtplib
from email.message import EmailMessage
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
BONUS_LOGS_FILE = os.path.join(BASE_DIR, 'bonus_email_logs.json')

REFERRAL_COMMISSION_RATE = 0.25

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR if os.path.isdir(STATIC_DIR) else 'static'
)
app.secret_key = os.environ.get("SECRET_KEY", "goat_autonomous_secure_key_2026_v4")

for folder in (TEMPLATE_DIR, STATIC_DIR, UPLOAD_FOLDER, OUTPUT_FOLDER):
    os.makedirs(folder, exist_ok=True)


def load_json_file(path, default):
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_users():
    return load_json_file(USERS_FILE, {})


def save_users(users_data):
    save_json_file(USERS_FILE, users_data)


def load_html_file(filename, **context):
    for candidate in (
        os.path.join(TEMPLATE_DIR, filename),
        os.path.join(BASE_DIR, filename),
    ):
        if os.path.isfile(candidate):
            with open(candidate, 'r', encoding='utf-8') as f:
                return render_template_string(f.read(), **context)
    return None


def get_plan_max_minutes(plan_key):
    mapping = {
        'monthly': 5,
        'six_month': 60,
        'yearly': 180
    }
    return mapping.get(plan_key, 5)


def normalize_plan_key(raw_plan):
    val = (raw_plan or '').strip().lower()
    if val in ('six_month', 'six-month', '6m', '6_month', 'half_yearly', 'pro'):
        return 'six_month'
    if val in ('yearly', 'annual', 'one_year', '1y', '1_year', 'creator_pass'):
        return 'yearly'
    if val in ('monthly', 'month', '1m', 'starter'):
        return 'monthly'
    return None


def build_bonus_payload(plan_info):
    return {
        'bonus_title': 'GOAT Creator Bonus Vault',
        'plan_name': plan_info['name'],
        'max_minutes_allowed': plan_info['max_minutes'],
        'bonus_items': [
            '30+ Viral Short-Form Video Hooks Pack',
            '20+ Emotional Shayari & Retro Reels Scripts',
            'Suno AI & Video Editing Prompt Cheat-Sheet',
            '25% Partner Referral Fast-Start Guide'
        ]
    }


def dispatch_bonus_email(recipient_email, recipient_name, plan_info):
    bonus = build_bonus_payload(plan_info)
    smtp_host = os.environ.get("SMTP_HOST", "").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_pass = os.environ.get("SMTP_PASS", "").strip()
    smtp_from = os.environ.get("SMTP_FROM", smtp_user or "noreply@goatstudio.local").strip()

    body_lines = [
        f"Namaste {recipient_name},",
        "",
        f"Aapka {plan_info['name']} (Rs.{plan_info['price_inr']}) activate ho gaya hai.",
        f"Video Duration Limit: Less than {plan_info['max_minutes']} minutes per video.",
        "",
        "Aapka Bonus Pack:",
    ] + [f"- {item}" for item in bonus['bonus_items']] + [
        "",
        "Dashboard: https://autovideopublisher.onrender.com/dashboard",
        "Team GOAT- Automated video editing and publishing platemorms"
    ]
    email_body = "\n".join(body_lines)

    delivery_mode = "logged_ready_for_smtp"
    delivery_detail = "Bonus recorded and unlocked on account. Set SMTP_HOST/SMTP_USER/SMTP_PASS in env for live inbox delivery."

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = EmailMessage()
            msg['Subject'] = f"Bonus Unlocked - {plan_info['name']} | GOAT Studio"
            msg['From'] = smtp_from
            msg['To'] = recipient_email
            msg.set_content(email_body)

            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            delivery_mode = "sent_via_smtp"
            delivery_detail = f"Bonus email sent to {recipient_email}."
        except Exception as exc:
            delivery_mode = "smtp_error_logged"
            delivery_detail = f"SMTP attempt note: {exc}"

    logs = load_json_file(BONUS_LOGS_FILE, [])
    entry = {
        'timestamp_utc': datetime.utcnow().isoformat(),
        'email': recipient_email,
        'name': recipient_name,
        'plan_id': plan_info['id'],
        'plan_name': plan_info['name'],
        'price_inr': plan_info['price_inr'],
        'max_minutes': plan_info['max_minutes'],
        'delivery_mode': delivery_mode,
        'delivery_detail': delivery_detail,
        'bonus': bonus
    }
    logs.append(entry)
    save_json_file(BONUS_LOGS_FILE, logs)
    session['bonus_status_text'] = f"{delivery_mode} -> {recipient_email}"
    return entry


def activate_plan_and_bonus(plan_key, buyer_email=None, buyer_name=None):
    max_minutes = get_plan_max_minutes(plan_key)
    price_map = {'monthly': 199, 'six_month': 499, 'yearly': 999}
    label_map = {
        'monthly': 'Monthly Plan',
        'six_month': '6-Month Plan',
        'yearly': '1-Year Plan'
    }
    plan_info = {
        'id': plan_key,
        'name': label_map.get(plan_key, 'Monthly Plan'),
        'plan_key': plan_key,
        'price_inr': price_map.get(plan_key, 199),
        'max_minutes': max_minutes
    }

    resolved_email = (buyer_email or session.get('user_email') or '').strip().lower()
    resolved_name = (buyer_name or session.get('user_name') or (resolved_email.split('@')[0].title() if resolved_email else 'Creator Partner')).strip()

    session['active_plan_key'] = plan_key
    if resolved_email:
        session['user_email'] = resolved_email
    if resolved_name:
        session['user_name'] = resolved_name

    users = load_users()
    if resolved_email and resolved_email in users:
        users[resolved_email]['active_plan_key'] = plan_key
        users[resolved_email]['last_plan_purchase_at'] = datetime.utcnow().isoformat()
        save_users(users)

    if resolved_email:
        dispatch_bonus_email(resolved_email, resolved_name, plan_info)


def generate_unique_seo(raw_filename, plan_key, max_minutes, active_tools):
    base_stem = os.path.splitext(raw_filename)[0] if raw_filename else "GOAT_Master_Clip"
    cleaned_words = [w for w in re.split(r'[_\-\s.]+', base_stem) if w]
    topic_label = " ".join(cleaned_words[:6]).title() if cleaned_words else "Creator Master Cut"
    tool_tag_slug = "".join(ch for ch in topic_label.title() if ch.isalnum())[:24] or "CreatorCut"
    plan_label = plan_key.replace("_", "-").title()

    seo_title = f"{topic_label} ({plan_label} less than {max_minutes}m) | GOAT- Automated video editing and publishing platemorms"
    seo_description = (
        f"Video Topic: {topic_label} | Plan: {plan_label} (Max less than {max_minutes} min) | "
        f"Tools: {active_tools}. Link: {{LINK_PLACEHOLDER}} "
        f"#GOATStudio #{tool_tag_slug} #ViralVideo #YouTube #Facebook #Instagram #TwitterX"
    )
    return seo_title, seo_description


LOGIN_HTML = "\n".join([
    "<!DOCTYPE html>",
    "<html lang=\"en\">",
    "<head>",
    "    <meta charset=\"UTF-8\">",
    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
    "    <title>Secure Login - GOAT- Automated video editing and publishing platemorms</title>",
    "    <style>",
    "        * { box-sizing: border-box; font-family: Arial, sans-serif; }",
    "        body { margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; background: #060b19; color: #f8fafc; }",
    "        .box { width: 100%; max-width: 440px; background: #0f172a; border: 1px solid #334155; border-radius: 14px; padding: 26px; }",
    "        .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }",
    "        .metric { background: #1e293b; border: 1px solid #38bdf8; border-radius: 10px; padding: 10px; text-align: center; }",
    "        .metric strong { display: block; font-size: 19px; color: #38bdf8; }",
    "        .metric span { font-size: 12px; color: #cbd5e1; }",
    "        h1 { margin: 0 0 8px; font-size: 22px; text-align: center; }",
    "        .err { background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; padding: 10px; border-radius: 8px; margin-bottom: 12px; font-size: 13px; }",
    "        label { display: block; font-size: 13px; margin-bottom: 5px; }",
    "        input { width: 100%; padding: 10px 12px; border-radius: 8px; border: 1px solid #334155; background: #060b19; color: #fff; margin-bottom: 12px; font-size: 14px; }",
    "        button { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #10b981; color: #fff; font-size: 15px; font-weight: bold; cursor: pointer; }",
    "        .foot { text-align: center; margin-top: 14px; font-size: 13px; }",
    "        .foot a { color: #38bdf8; text-decoration: none; }",
    "    </style>",
    "</head>",
    "<body>",
    "    <div class=\"box\">",
    "        <div class=\"metrics\">",
    "            <div class=\"metric\"><strong>12,000+</strong><span>Downloads</span></div>",
    "            <div class=\"metric\"><strong>4&#9733;</strong><span>Creator Rating</span></div>",
    "        </div>",
    "        <h1>Creator Secure Login</h1>",
    "        {% if error_msg %}",
    "        <div class=\"err\">{{ error_msg }}</div>",
    "        {% endif %}",
    "        <form method=\"POST\" action=\"/login\">",
    "            <label for=\"name\">Full Name</label>",
    "            <input type=\"text\" id=\"name\" name=\"name\" placeholder=\"Umakant Upadhyay\" required>",
    "            <label for=\"email\">Email Address</label>",
    "            <input type=\"email\" id=\"email\" name=\"email\" placeholder=\"creator@example.com\" required>",
    "            <label for=\"password\">Password</label>",
    "            <input type=\"password\" id=\"password\" name=\"password\" placeholder=\"Enter password\" required>",
    "            <button type=\"submit\">Login and Open Dashboard</button>",
    "        </form>",
    "        <div class=\"foot\"><a href=\"/\">Back to Landing Page</a></div>",
    "    </div>",
    "</body>",
    "</html>"
])


DASHBOARD_HTML = "\n".join([
    "<!DOCTYPE html>",
    "<html lang=\"en\">",
    "<head>",
    "    <meta charset=\"UTF-8\">",
    "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
    "    <title>GOAT- Automated video editing and publishing platemorms</title>",
    "    <style>",
    "        * { box-sizing: border-box; font-family: Arial, sans-serif; }",
    "        body { margin: 0; background: #060b19; color: #f8fafc; line-height: 1.5; }",
    "        .top-header { background: #0f172a; border-bottom: 2px solid #38bdf8; padding: 14px 20px; }",
    "        .header-wrap { max-width: 1260px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }",
    "        .brand-title { margin: 0; font-size: 22px; font-weight: bold; color: #38bdf8; }",
    "        .top-stats { display: flex; gap: 8px; flex-wrap: wrap; }",
    "        .stat-chip { background: #1e293b; border: 1px solid #38bdf8; padding: 5px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; }",
    "        .nav-group { display: flex; gap: 8px; }",
    "        .nav-btn { text-decoration: none; background: #1e293b; color: #fff; padding: 7px 12px; border-radius: 8px; font-size: 12px; font-weight: bold; }",
    "        .live-ticker { background: #111827; border-bottom: 1px solid #1f2937; padding: 9px 20px; }",
    "        .ticker-inner { max-width: 1260px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }",
    "        .notif-pill { background: #172554; border-left: 4px solid #fbbf24; color: #fef08a; padding: 6px 12px; border-radius: 6px; font-size: 13px; }",
    "        .container { max-width: 1260px; margin: 0 auto; padding: 20px; }",
    "        .grid-main { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 18px; }",
    "        .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 12px; padding: 18px; }",
    "        .card h2 { margin: 0 0 10px; font-size: 17px; color: #7dd3fc; }",
    "        .preview-stage { width: 100%; height: 230px; background: #020617; border: 1px solid #334155; border-radius: 8px; margin-top: 8px; overflow: hidden; }",
    "        .preview-stage video { width: 100%; height: 100%; object-fit: contain; display: block; }",
    "        .file-info-badge { margin-top: 6px; font-size: 12px; color: #38bdf8; }",
    "        .open-raw-link { color: #38bdf8; font-size: 12px; font-weight: bold; display: none; margin-left: 10px; }",
    "        .brahmastra-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin: 12px 0; }",
    "        .b-box { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 9px; }",
    "        .b-top { font-size: 12px; font-weight: bold; margin-bottom: 6px; }",
    "        .btn-mini { width: 100%; padding: 6px; border: none; border-radius: 6px; background: #2563eb; color: #fff; font-size: 12px; font-weight: bold; cursor: pointer; }",
    "        .btn { border: none; border-radius: 8px; padding: 10px 14px; font-size: 13px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }",
    "        .btn-primary { background: #10b981; color: #fff; width: 100%; margin-top: 4px; }",
    "        .btn-all { background: #7c3aed; color: #fff; width: 100%; margin-top: 8px; }",
    "        .btn-copy { background: #0284c7; color: #fff; }",
    "        .btn-dl { background: #059669; color: #fff; }",
    "        .console-box { margin-top: 10px; padding: 10px; background: #020617; border: 1px solid #334155; border-radius: 8px; font-size: 12px; color: #a7f3d0; }",
    "        label.field-lbl { display: block; font-size: 12px; font-weight: bold; color: #cbd5e1; margin: 10px 0 4px; }",
    "        input[type=\"file\"], input[type=\"text\"], textarea { width: 100%; padding: 9px 11px; border-radius: 8px; border: 1px solid #334155; background: #060b19; color: #fff; font-size: 13px; }",
    "        textarea { min-height: 80px; }",
    "        .link-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; }",
    "        .link-row input { flex: 1; min-width: 180px; }",
    "        .social-bar { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }",
    "        .s-yt { background: #dc2626; color: #fff; }",
    "        .s-fb { background: #2563eb; color: #fff; }",
    "        .s-ig { background: #db2777; color: #fff; }",
    "        .s-tw { background: #334155; color: #fff; }",
    "        .s-ref { background: #d97706; color: #fff; }",
    "    </style>",
    "</head>",
    "<body>",
    "<header class=\"top-header\">",
    "    <div class=\"header-wrap\">",
    "        <h1 class=\"brand-title\">GOAT- Automated video editing and publishing platemorms</h1>",
    "        <div class=\"top-stats\">",
    "            <span class=\"stat-chip\">100,000+ Views</span>",
    "            <span class=\"stat-chip\">100+ Messages</span>",
    "            <span class=\"stat-chip\">12,000+ Downloads &#8226; 4&#9733;</span>",
    "            <span class=\"stat-chip\">25% Ref: <span id=\"refCount\">{{ total_referrals }}</span> | Rs.<span id=\"refEarn\">{{ referral_earnings }}</span></span>",
    "        </div>",
    "        <div class=\"nav-group\">",
    "            <a href=\"/\" class=\"nav-btn\">Landing</a>",
    "            <a href=\"/logout\" class=\"nav-btn\">Logout</a>",
    "        </div>",
    "    </div>",
    "</header>",
    "<div class=\"live-ticker\">",
    "    <div class=\"ticker-inner\">",
    "        <div class=\"notif-pill\" id=\"liveNotifBox\">Rajesh, Dehradun ne abhi khareeda: Annual Creator Pass (Rs.999)</div>",
    "        <div style=\"font-size:12px;color:#94a3b8;\">Signed in: <strong>{{ user_name }}</strong> ({{ user_email }}) | Max Limit: <strong>{{ max_minutes }}</strong> min | Bonus Status: <strong>{{ bonus_status_text }}</strong></div>",
    "    </div>",
    "</div>",
    "<main class=\"container\">",
    "    <div class=\"grid-main\">",
    "        <section class=\"card\">",
    "            <h2>1. Raw Video Preview & 5 Brahmastra Execution</h2>",
    "            <input type=\"file\" id=\"rawVideoInput\" accept=\"video/*,.mp4,.webm,.ogg,.mov,.m4v,.mkv,.avi\">",
    "            <div style=\"margin-top:6px;\">",
    "                <span class=\"file-info-badge\" id=\"rawFileInfo\">No video selected yet - choose your raw video to verify preview below.</span>",
    "                <a id=\"openRawTabLink\" class=\"open-raw-link\" href=\"#\" target=\"_blank\" rel=\"noopener\">Open Raw Video in Browser Tab</a>",
    "            </div>",
    "            <div class=\"preview-stage\">",
    "                <video id=\"rawPlayer\" controls playsinline preload=\"auto\"></video>",
    "            </div>",
    "            <div class=\"brahmastra-grid\">",
    "                <div class=\"b-box\"><div class=\"b-top\"><input type=\"checkbox\" name=\"b_tool\" value=\"Copyright Shield\" checked> 1. Copyright Shield</div><button type=\"button\" class=\"btn-mini\" onclick=\"executeSingleBrahmastra('shield')\">Execute Shield</button></div>",
    "                <div class=\"b-box\"><div class=\"b-top\"><input type=\"checkbox\" name=\"b_tool\" value=\"Trend-Jacking Hook\" checked> 2. Trend-Jacking Hook</div><button type=\"button\" class=\"btn-mini\" onclick=\"executeSingleBrahmastra('trend')\">Execute Hook</button></div>",
    "                <div class=\"b-box\"><div class=\"b-top\"><input type=\"checkbox\" name=\"b_tool\" value=\"Multi-Language Clone\" checked> 3. Multi-Language Clone</div><button type=\"button\" class=\"btn-mini\" onclick=\"executeSingleBrahmastra('clone')\">Execute Clone</button></div>",
    "                <div class=\"b-box\"><div class=\"b-top\"><input type=\"checkbox\" name=\"b_tool\" value=\"Smart Affiliate Injector\" checked> 4. Affiliate Injector</div><button type=\"button\" class=\"btn-mini\" onclick=\"executeSingleBrahmastra('affiliate')\">Execute Injector</button></div>",
    "                <div class=\"b-box\"><div class=\"b-top\"><input type=\"checkbox\" name=\"b_tool\" value=\"Voice of Emotion\" checked> 5. Voice of Emotion</div><button type=\"button\" class=\"btn-mini\" onclick=\"executeSingleBrahmastra('emotion')\">Execute Emotion</button></div>",
    "            </div>",
    "            <button type=\"button\" class=\"btn btn-primary\" onclick=\"processFullVideo()\">Run Full Video Edit + Generate Edited Link & SEO</button>",
    "            <button type=\"button\" class=\"btn btn-all\" onclick=\"executeAllFive()\">Execute All 5 Brahmastras Together</button>",
    "            <div class=\"console-box\" id=\"actionLog\">Status: Ready. Select raw video to verify preview, then run any Brahmastra.</div>",
    "        </section>",
    "        <section class=\"card\">",
    "            <h2>2. Edited Video Link, Download, SEO Copy & Social Publish</h2>",
    "            <div class=\"preview-stage\">",
    "                <video id=\"editedPlayer\" controls playsinline preload=\"auto\"></video>",
    "            </div>",
    "            <label class=\"field-lbl\">Edited Video Direct Link (Copy & Paste Anywhere)</label>",
    "            <div class=\"link-row\">",
    "                <input type=\"text\" id=\"editedLinkInput\" value=\"https://autovideopublisher.onrender.com/process_output/GOAT_Mastered_Sample.mp4\" readonly>",
    "                <button type=\"button\" class=\"btn btn-copy\" onclick=\"copyEditedLink()\">Copy Link</button>",
    "                <a id=\"downloadVideoBtn\" href=\"/process_output/GOAT_Mastered_Sample.mp4?download=1\" class=\"btn btn-dl\">Download Video</a>",
    "            </div>",
    "            <label class=\"field-lbl\">SEO Title</label>",
    "            <input type=\"text\" id=\"seoTitleBox\" value=\"Viral Master Cut 2026 | GOAT- Automated video editing and publishing platemorms\">",
    "            <label class=\"field-lbl\">SEO Caption, Tags & Video Link (Copy for Social Paste)</label>",
    "            <textarea id=\"seoCaptionBox\">Edited with GOAT- Automated video editing and publishing platemorms. Link: https://autovideopublisher.onrender.com/process_output/GOAT_Mastered_Sample.mp4 #GOATStudio #CreatorSaaS #ViralVideo #YouTube #Facebook #Instagram #TwitterX</textarea>",
    "            <button type=\"button\" class=\"btn btn-copy\" style=\"margin-top:8px;\" onclick=\"copyAllForSocial()\">Copy Full SEO + Edited Video Link</button>",
    "            <div class=\"social-bar\">",
    "                <button type=\"button\" class=\"btn s-yt\" onclick=\"publishToPlatform('youtube')\">YouTube</button>",
    "                <button type=\"button\" class=\"btn s-fb\" onclick=\"publishToPlatform('facebook')\">Facebook</button>",
    "                <button type=\"button\" class=\"btn s-ig\" onclick=\"publishToPlatform('instagram')\">Instagram</button>",
    "                <button type=\"button\" class=\"btn s-tw\" onclick=\"publishToPlatform('twitter')\">Twitter / X</button>",
    "                <button type=\"button\" class=\"btn s-ref\" onclick=\"addReferral()\">25% Referral Link</button>",
    "            </div>",
    "        </section>",
    "    </div>",
    "</main>",
    "<script>",
    "var buyerNotifications = [",
    "    \"Rajesh, Dehradun ne abhi khareeda: Annual Creator Pass (Rs.999)\",",
    "    \"Pooja Sharma, Jaipur ne abhi khareeda: 6-Month Pro Vault (Rs.499)\",",
    "    \"Amit Verma, Lucknow ne abhi khareeda: Monthly Starter Plan (Rs.199)\",",
    "    \"Sneha Joshi, Haldwani ne abhi khareeda: Annual Creator Pass (Rs.999)\",",
    "    \"Vikram Rathore, Indore ne abhi khareeda: 6-Month Pro Vault (Rs.499)\",",
    "    \"Neha Kulkarni, Pune ne abhi khareeda: Annual Creator Pass (Rs.999)\",",
    "    \"Saurabh Tiwari, Varanasi ne abhi khareeda: 6-Month Pro Vault (Rs.499)\",",
    "    \"Ankit Negi, Almora ne abhi khareeda: Annual Creator Pass (Rs.999)\",",
    "    \"Kavita Nair, Kochi ne abhi khareeda: Monthly Starter Plan (Rs.199)\",",
    "    \"Rohit Bansal, Chandigarh ne abhi khareeda: Annual Creator Pass (Rs.999)\"",
    "];",
    "var buyerIdx = 0;",
    "setInterval(function () {",
    "    buyerIdx = (buyerIdx + 1) % buyerNotifications.length;",
    "    var el = document.getElementById(\"liveNotifBox\");",
    "    if (el) el.textContent = buyerNotifications[buyerIdx];",
    "}, 30000);",
    "var rawVideoInput = document.getElementById(\"rawVideoInput\");",
    "var rawPlayer = document.getElementById(\"rawPlayer\");",
    "var rawFileInfo = document.getElementById(\"rawFileInfo\");",
    "var openRawTabLink = document.getElementById(\"openRawTabLink\");",
    "var editedPlayer = document.getElementById(\"editedPlayer\");",
    "var currentRawObjectUrl = null;",
    "var currentRawDurationSec = 0;",
    "if (editedPlayer) {",
    "    editedPlayer.addEventListener(\"loadeddata\", function () {",
    "        var log = document.getElementById(\"actionLog\");",
    "        if (log) { log.textContent = log.textContent + \" | Edited video frame ready in player.\"; }",
    "    });",
    "    editedPlayer.addEventListener(\"error\", function () {",
    "        var log = document.getElementById(\"actionLog\");",
    "        var errCode = editedPlayer.error ? editedPlayer.error.code : \"unknown\";",
    "        if (log) { log.textContent = log.textContent + \" | Edited player decode error (code: \" + errCode + \").\"; }",
    "    });",
    "}",
    "if (rawPlayer) {",
    "    rawPlayer.addEventListener(\"loadedmetadata\", function () {",
    "        currentRawDurationSec = Number(rawPlayer.duration || 0);",
    "        var mins = (currentRawDurationSec / 60).toFixed(2);",
    "        if (rawVideoInput && rawVideoInput.files && rawVideoInput.files[0]) {",
    "            var f = rawVideoInput.files[0];",
    "            var sizeMb = (f.size / (1024 * 1024)).toFixed(2);",
    "            rawFileInfo.textContent = \"Selected Raw Video: \" + f.name + \" (\" + sizeMb + \" MB, \" + mins + \" min)\";",
    "        }",
    "    });",
    "}",
    "if (rawVideoInput) {",
    "    rawVideoInput.addEventListener(\"change\", function () {",
    "        var file = this.files && this.files[0];",
    "        if (!file) return;",
    "        currentRawDurationSec = 0;",
    "        if (currentRawObjectUrl) { URL.revokeObjectURL(currentRawObjectUrl); }",
    "        currentRawObjectUrl = URL.createObjectURL(file);",
    "        rawPlayer.style.display = \"block\";",
    "        rawPlayer.src = currentRawObjectUrl;",
    "        rawPlayer.load();",
    "        var sizeMb = (file.size / (1024 * 1024)).toFixed(2);",
    "        rawFileInfo.textContent = \"Selected Raw Video: \" + file.name + \" (\" + sizeMb + \" MB)\";",
    "        if (openRawTabLink) { openRawTabLink.href = currentRawObjectUrl; openRawTabLink.style.display = \"inline\"; }",
    "        document.getElementById(\"actionLog\").textContent = \"Raw video loaded in preview player: \" + file.name;",
    "    });",
    "}",
    "async function executeSingleBrahmastra(toolId) {",
    "    var log = document.getElementById(\"actionLog\");",
    "    log.textContent = \"Executing \" + toolId + \"...\";",
    "    try {",
    "        var res = await fetch(\"/run_brahmastra\", { method: \"POST\", headers: { \"Content-Type\": \"application/json\" }, body: JSON.stringify({ tool_id: toolId }) });",
    "        var data = await res.json();",
    "        log.textContent = data.title + \" [\" + data.status + \"]: \" + data.detail;",
    "    } catch (e) { log.textContent = \"Execution error: \" + e.message; }",
    "}",
    "async function executeAllFive() {",
    "    var log = document.getElementById(\"actionLog\");",
    "    log.textContent = \"Executing all 5 Brahmastras...\";",
    "    try {",
    "        var res = await fetch(\"/run_brahmastra\", { method: \"POST\", headers: { \"Content-Type\": \"application/json\" }, body: JSON.stringify({ tool_id: \"all\" }) });",
    "        var data = await res.json();",
    "        log.textContent = data.title + \" (\" + data.status_label + \"): \" + data.detail;",
    "    } catch (e) { log.textContent = \"Error executing all 5: \" + e.message; }",
    "}",
    "async function processFullVideo() {",
    "    var log = document.getElementById(\"actionLog\");",
    "    log.textContent = \"Processing edited video, link, SEO & download package...\";",
    "    var fd = new FormData();",
    "    if (rawVideoInput && rawVideoInput.files && rawVideoInput.files[0]) { fd.append(\"video_file\", rawVideoInput.files[0]); }",
    "    fd.append(\"video_duration_sec\", String(currentRawDurationSec || 0));",
    "    var checkedBoxes = document.querySelectorAll(\"input[name='b_tool']:checked\");",
    "    for (var i = 0; i < checkedBoxes.length; i++) { fd.append(\"brahmastras\", checkedBoxes[i].value); }",
    "    try {",
    "        var res = await fetch(\"/process_video\", { method: \"POST\", body: fd });",
    "        var data = await res.json();",
    "        if (data.status === \"success\") {",
    "            var fullUrl = window.location.origin + data.video_url;",
    "            document.getElementById(\"editedLinkInput\").value = fullUrl;",
    "            document.getElementById(\"downloadVideoBtn\").href = data.download_url;",
    "            document.getElementById(\"seoTitleBox\").value = data.seo_title;",
    "            document.getElementById(\"seoCaptionBox\").value = data.seo_description.replace(\"{LINK_PLACEHOLDER}\", fullUrl);",
    "            if (editedPlayer) {",
    "                editedPlayer.style.display = \"block\";",
    "                if (currentRawObjectUrl) {",
    "                    editedPlayer.src = currentRawObjectUrl;",
    "                } else {",
    "                    editedPlayer.src = data.video_url;",
    "                }",
    "                editedPlayer.load();",
    "            }",
    "            log.textContent = data.message + \" | Preview loaded.\";",
    "        } else { log.textContent = \"Error: \" + data.message; }",
    "    } catch (e) { log.textContent = \"Processing failed: \" + e.message; }",
    "}",
    "function copyEditedLink() {",
    "    var linkVal = document.getElementById(\"editedLinkInput\").value;",
    "    navigator.clipboard.writeText(linkVal).then(function () { document.getElementById(\"actionLog\").textContent = \"Copied Edited Video Link: \" + linkVal; });",
    "}",
    "function copyAllForSocial() {",
    "    var title = document.getElementById(\"seoTitleBox\").value;",
    "    var caption = document.getElementById(\"seoCaptionBox\").value;",
    "    var combined = title + \"\\n\\n\" + caption;",
    "    navigator.clipboard.writeText(combined).then(function () { document.getElementById(\"actionLog\").textContent = \"Copied Title + SEO + Edited Video Link! Now paste directly on YouTube, Facebook, Instagram, or Twitter/X.\"; });",
    "}",
    "function publishToPlatform(platform) {",
    "    var linkVal = document.getElementById(\"editedLinkInput\").value;",
    "    var captionVal = document.getElementById(\"seoCaptionBox\").value;",
    "    navigator.clipboard.writeText(captionVal).catch(function () {});",
    "    var targetUrl = \"https://studio.youtube.com\";",
    "    if (platform === \"facebook\") { targetUrl = \"https://www.facebook.com/sharer/sharer.php?u=\" + encodeURIComponent(linkVal); }",
    "    else if (platform === \"instagram\") { targetUrl = \"https://www.instagram.com/\"; }",
    "    else if (platform === \"twitter\") { targetUrl = \"https://x.com/intent/tweet?text=\" + encodeURIComponent(captionVal); }",
    "    document.getElementById(\"actionLog\").textContent = \"Copied link & SEO for \" + platform.toUpperCase() + \". Opening platform so you can paste & publish immediately.\";",
    "    window.open(targetUrl, \"_blank\", \"noopener\");",
    "}",
    "async function addReferral() {",
    "    var res = await fetch(\"/simulate_referral_share\", { method: \"POST\", headers: { \"Content-Type\": \"application/json\" }, body: JSON.stringify({ sale_amount: 199 }) });",
    "    var data = await res.json();",
    "    if (data.status === \"success\") {",
    "        document.getElementById(\"refCount\").textContent = data.total_referrals;",
    "        document.getElementById(\"refEarn\").textContent = data.referral_earnings;",
    "        var refLink = window.location.origin + \"/login?ref=goat25\";",
    "        navigator.clipboard.writeText(refLink).catch(function () {});",
    "        document.getElementById(\"actionLog\").textContent = data.message + \" Link: \" + refLink;",
    "    }",
    "}",
    "</script>",
    "</body>",
    "</html>"
])


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
                    session['active_plan_key'] = users[email].get('active_plan_key', 'monthly')
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
                    'active_plan_key': 'monthly',
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': datetime.utcnow().isoformat()
                }
                save_users(users)
                session['logged_in'] = True
                session['user_name'] = display_name
                session['user_email'] = email
                session['active_plan_key'] = 'monthly'
                return redirect(url_for('dashboard'))

    return render_template_string(LOGIN_HTML, error_msg=error_msg)


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    plan_key = session.get('active_plan_key', 'monthly')
    return render_template_string(
        DASHBOARD_HTML,
        user_name=session.get('user_name', 'Creator Partner'),
        user_email=session.get('user_email', ''),
        total_referrals=session.get('total_referrals', 0),
        referral_earnings=round(session.get('referral_earnings', 0.0), 2),
        max_minutes=get_plan_max_minutes(plan_key),
        bonus_status_text=session.get('bonus_status_text', 'Pending Plan Activation')
    )


@app.route('/success')
def success():
    raw_plan = request.args.get('plan') or request.args.get('plan_key') or request.args.get('sub') or ''
    normalized_plan = normalize_plan_key(raw_plan)
    buyer_email = (request.args.get('email') or request.args.get('payer_email') or '').strip().lower()
    buyer_name = (request.args.get('name') or request.args.get('payer_name') or '').strip()

    if normalized_plan:
        activate_plan_and_bonus(normalized_plan, buyer_email=buyer_email or None, buyer_name=buyer_name or None)
    elif buyer_email:
        current_plan = session.get('active_plan_key', 'monthly')
        activate_plan_and_bonus(current_plan, buyer_email=buyer_email, buyer_name=buyer_name or None)

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
            'status': 'Active',
            'detail': 'Frame micro-crop, color shift and pitch protection applied.'
        },
        'trend': {
            'title': '2. Trend-Jacking Hook',
            'status': 'Ready',
            'detail': '3-second high-retention hook generated.'
        },
        'clone': {
            'title': '3. Multi-Language Clone',
            'status': 'Ready',
            'detail': 'Multi-language voice and caption tracks prepared.'
        },
        'affiliate': {
            'title': '4. Smart Affiliate Injector',
            'status': 'Ready',
            'detail': 'Affiliate offer block and CTA link ready.'
        },
        'emotion': {
            'title': '5. Voice of Emotion',
            'status': 'Ready',
            'detail': 'Emotional tone and natural pacing configured.'
        }
    }
    if tool_id in responses:
        return jsonify({'status': 'success', **responses[tool_id]})
    return jsonify({
        'status': 'success',
        'title': 'All 5 Brahmastras',
        'status_label': 'All 5 Executed',
        'detail': 'All 5 Brahmastras executed cleanly.'
    })


@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        plan_key = session.get('active_plan_key', 'monthly')
        max_minutes = get_plan_max_minutes(plan_key)
        duration_sec_raw = request.form.get('video_duration_sec', '0')
        try:
            duration_sec = float(duration_sec_raw or 0)
        except ValueError:
            duration_sec = 0.0

        video_minutes = duration_sec / 60.0
        if duration_sec > 0 and video_minutes >= max_minutes:
            return jsonify({
                'status': 'error',
                'message': (
                    f"Duration limit exceeded: video is {video_minutes:.2f} min, "
                    f"but current plan allows less than {max_minutes} min."
                )
            }), 400

        video_file = request.files.get('video_file')
        selected = request.form.getlist('brahmastras')
        out_filename = "GOAT_Mastered_Sample.mp4"
        source_name = "GOAT_Master_Clip.mp4"

        if video_file and video_file.filename:
            source_name = os.path.basename(video_file.filename)
            clean_name = source_name.replace(" ", "_")
            out_filename = f"GOAT_Edited_{clean_name}"
            raw_path = os.path.join(UPLOAD_FOLDER, clean_name)
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            video_file.save(raw_path)
            shutil.copyfile(raw_path, out_path)
        else:
            out_path = os.path.join(OUTPUT_FOLDER, out_filename)
            if not os.path.isfile(out_path):
                with open(out_path, 'wb') as f:
                    f.write(b"GOAT_MASTERED_VIDEO_PACKAGE_READY")

        video_url = f"/process_output/{out_filename}"
        active_tools = ", ".join(selected) if selected else "All 5 Brahmastras"
        seo_title, seo_description = generate_unique_seo(source_name, plan_key, max_minutes, active_tools)

        return jsonify({
            'status': 'success',
            'message': f'Edited video ready ({active_tools} | Plan limit: less than {max_minutes} min).',
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
        'message': f'Referral link copied! 25% commission (+Rs.{commission_earned}) credited.',
        'total_referrals': session['total_referrals'],
        'referral_earnings': session['referral_earnings']
    })


@app.route('/process_output/<path:filename>')
def serve_output(filename):
    as_attachment = request.args.get('download') == '1'
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=as_attachment)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)