import os
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

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
    session['user'] = (
        username if username else 'upadhyayumakant2026@gmail.com'
    )
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
    return jsonify(
        {'status': 'redirect', 'url': url_for('dashboard') + '#plans'}
    )
  session['videos_used'] = used + 1
  return jsonify(
      {'status': 'success', 'message': 'Video Processed Successfully!'}
  )


# ---------------------------------------------------------
# 1. Advanced Auto Thumbnail & SEO Tags Generator API
# ---------------------------------------------------------
@app.route('/api/v1/generate-thumbnail-tags', methods=['POST'])
def generate_thumbnail_tags():
  try:
    data = request.json or {}
    video_title = data.get('title', 'Viral Creator Video')

    # मिलिट्री-ग्रेड एसईओ और थंबनेल ऑटोमेशन लॉजिक
    generated_tags = [
        'viralshorts',
        'trending',
        'creatorstudio',
        'autovideopublisher',
        'topcontent',
        'hindicinema',
        'retrohits',
    ]
    thumbnail_concept = (
        f'High-CTR Cinematic Thumbnail for: {video_title} [Military Grade Optimized]'
    )

    return jsonify({
        'success': True,
        'thumbnail_url': (
            'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe'
            '?w=800&auto=format&fit=crop&q=60'
        ),
        'tags': generated_tags,
        'concept': thumbnail_concept,
        'message': (
            'Auto Thumbnail and Viral SEO Tags generated successfully!'
        ),
    }), 200
  except Exception as e:
    return jsonify({'success': False, 'error': str(e)}), 500


# ---------------------------------------------------------
# 2. Telegram Community & Welcome Bridge
# ---------------------------------------------------------
@app.route('/telegram-community-join')
def telegram_community_join():
  # यूजर को आपके सीक्रेट ऑटोमेटेड टेलीग्राम ग्रुप पर रीडायरेक्ट करेगा
  return redirect('https://t.me/+your_secret_creator_community_link')


@app.route('/payment_success')
def payment_success():
  plan_type = request.args.get('plan', 'Starter')
  session['user_plan'] = plan_type
  # पेमेंट सफल होने पर सीधा होमपेज या बोनस ड्राइव लिंक पर भेजना
  return redirect(url_for('home'))


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)