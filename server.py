from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from text_generation import DialogManager
from rss_parser import RSSParser  
import uuid
import time
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
CORS(app)

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/server.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Инициализация RSS парсера
RSS_FEED_URL = "https://rss.app/feeds/i5rHPxsKfxBMdnO4.xml"  # Замените на ваш URL
rss_parser = RSSParser(RSS_FEED_URL)

# Initialize dialog manager
try:
    dialog_manager = DialogManager()
    app.logger.info("DialogManager initialized successfully")
except Exception as e:
    app.logger.error(f"Failed to initialize DialogManager: {str(e)}")
    raise

@app.route('/')
def index():
    """Serve the main index page"""
    return render_template("index.html")

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()}), 200

@app.route("/get_news", methods=["GET"])
def get_news():
    try:
        news = rss_parser.parse_feed()
        if not news:
            return jsonify({"error": "No news found"}), 404

        # Добавляем fallback-данные
        for item in news:
            if not item.get('image_url'):
                item['image_url'] = "/static/assets/img/news-placeholder.jpg"
            if not item.get('description'):
                item['description'] = "Новость из Telegram-канала EcoSurgut"

        return jsonify({"status": "success", "news": news})

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500
    
@app.route("/process", methods=["POST"])
def process_speech():
    """Process user input and generate response"""
    # Validate request
    if not request.is_json:
        app.logger.warning("Received non-JSON request")
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    user_text = data.get("text", "").strip()
    request_id = str(uuid.uuid4())

    if not user_text:
        app.logger.warning("Received empty request")
        return jsonify({"error": "Empty request"}), 400

    try:
        # Generate response
        start_time = time.time()
        response_text = dialog_manager.generate_response(user_text)
        processing_time = time.time() - start_time

        # Log the interaction
        app.logger.info(f"RequestID: {request_id} | Processing time: {processing_time:.2f}s")
        app.logger.debug(f"User: {user_text} | Bot: {response_text}")

        return jsonify({
            "request_id": request_id,
            "response": response_text,
            "processing_time": processing_time,
            "status": "success"
        })

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            "request_id": request_id,
            "error": "Internal server error",
            "status": "error"
        }), 500

if __name__ == "__main__":
    app.run(__name__ == "__main__")