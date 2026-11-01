from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)  # <-- Yeh sabse upar hona chahiye!

# Ab iske niche aapke saare routes aane chahiye:
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# (Aur file ke bilkul aakhir mein niche yeh hona chahiye):
if __name__ == '__main__':
    app.run(debug=True, port=5001)