# Python का ऑफिशियल हल्का वजन इमेज इस्तेमाल करें
FROM python:3.10-slim

# सिस्टम में FFmpeg और जरूरी टूल्स इंस्टॉल करें (ताकि वीडियो प्रोसेसिंग और थंबनेल मक्खन की तरह चलें)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# वर्कディレクトリ सेट करें
WORKDIR /app

# प्रोजेक्ट की सारी फाइलें कॉपी करें
COPY . /app

# Python की जरूरी लाइब्रेरीज इंस्टॉल करें
RUN pip install --no-cache-dir -r requirements.txt

# Render पर चलने के लिए पोर्ट और गनिकोड (Gunicorn) सर्वर कमांड सेट करें
ENV PORT=10000
EXPOSE 10000

CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "120", "app.py:app"]