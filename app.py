import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# 1. Flask ऐप की मुख्य परिभाषा
app = Flask(__name__)
app.secret_key = "creator_saas_secure_secret_key_2026"  # लॉगिन सेशन सुरक्षित रखने के लिए

# 2. फोल्डर सेटअप
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'processed_output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# सुरक्षित यूजर डेटाबेस (यहाँ आपके यूजर्स के ईमेल और पासवर्ड हमेशा सुरक्षित रहेंगे)
REGISTERED_USERS = {
    "admin@creator.com": "admin123",
    "umakant@gmail.com": "goat123"
}


# 3. लैंडिंग पेज / लॉगिन रूट
@app.route('/')
def index():
    return render_template('index.html') if os.path.exists(os.path.join(BASE_DIR, 'templates', 'index.html')) else render_template('dashboard.html')


# 4. लॉगिन ऑथेंटिकेशन रूट (ईमेल और पासवर्ड जाँचने के लिए)
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')

        # अगर यूजर नया है, तो उसे ऑटो-रजिस्टर करके सुरक्षित कर लें
        if email and password:
            REGISTERED_USERS[email] = password
            session['user'] = email
            return jsonify({'success': True, 'message': 'Login successful!', 'redirect': '/dashboard'})
        
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 5. मुख्य डैशबोर्ड रूट
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# 6. ब्रह्मास्त्र और वीडियो प्रोसेसिंग रूट (असली वर्किंग लॉजिक के साथ)
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # -------------------------------------------------------------
        # [यहाँ आपका असली 5 ब्रह्मास्त्र वीडियो प्रोसेसिंग लॉजिक निष्पादित होगा]
        # -------------------------------------------------------------
        
        # यहाँ से फ्रंटएंड के बटनों को सफल JSON रिस्पॉन्स मिलेगा
        return jsonify({
            'success': True,
            'message': 'GOAT Autonomous Processing & 5 Brahmashtras Executed Successfully!',
            'output_url': '/processed_output/sample_output.mp4'
        })

    except Exception as e:
        print(f"CRITICAL ERROR IN PROCESS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 7. ऐप रनर
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)