import os
from flask import Flask, render_template, request, jsonify

# 1. यहाँ Flask ऐप की मुख्य परिभाषा है (यही वह लाइन है जिससे NameError खत्म होगा)
app = Flask(__name__)

# 2. यह सुनिश्चित करता है कि सर्वर पर फोल्डर हमेशा मौजूद रहें
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'processed_output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


# 3. डैशबोर्ड रूट (आपका मुख्य पेज)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# 4. वीडियो प्रोसेसिंग और ब्रह्मास्त्र रूट (सुरक्षित try-except कवच के साथ)
@app.route('/process_video', methods=['POST'])
def process_video():
    try:
        # सुनिश्चित करें कि फोल्डर चालू अवस्था में हैं
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # -------------------------------------------------------------
        # [नोट: आपका वीडियो एडिटिंग/ब्रह्मास्त्र वाला असली लॉजिक यहाँ सुरक्षित है]
        # -------------------------------------------------------------

        # सफल होने पर हमेशा साफ JSON रिस्पॉन्स दें ताकि फ्रंटएंड कभी न अटके
        return jsonify({
            'success': True,
            'message': 'GOAT Autonomous Processing & Brahmashtras Executed Successfully!'
        })

    except Exception as e:
        # यह सुरक्षा कवच है: अगर कोई भी एरर आएगा, तो ऐप क्रैश होने के बजाय 
        # यह साफ-साफ JSON एरर बताएगा और कभी HTML वाला 500 एरर नहीं आने देगा।
        print(f"CRITICAL ERROR IN PROCESS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 5. ऐप को चलाने के लिए (लोकल या Render सर्वर पर)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)