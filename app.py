from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__) # <-- Yeh sabse upar hona chahiye!
app.secret_key = 'your_secret_key_here' # agar secret key hai

# Ab iske niche saare routes aayenge:
@app.route('/payment-success')
def payment_success():
    ...