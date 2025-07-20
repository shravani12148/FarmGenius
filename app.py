from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
from werkzeug.utils import secure_filename
from chatbot_logic import get_bot_response
import os
import uuid
import json
import base64
import logging
import requests
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO
from datetime import datetime

# Crop map dependencies
import folium
import random
from folium import LayerControl
from branca.element import Template, MacroElement

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ======================
# CONFIGURATION SETTINGS
# ======================
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'wav', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# =============
# LOGGING SETUP
# =============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# =================
# LANGUAGE SETTINGS
# =================
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'mr': 'Marathi',
    'hi': 'Hindi'
}

# =================
# HELPER FUNCTIONS
# =================
def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def text_to_speech(text, language='en'):
    """Convert text to speech audio file"""
    try:
        if language == 'mr':
            lang_code = 'mr-IN'
        elif language == 'hi':
            lang_code = 'hi-IN'
        else:
            lang_code = 'en-US'
        
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        tts.save(audio_path)
        return audio_filename
    except Exception as e:
        logging.error(f"Text-to-speech error: {str(e)}")
        return None

def speech_to_text(audio_file, language='en'):
    """Convert speech audio to text"""
    try:
        r = sr.Recognizer()
        
        if language == 'mr':
            lang_code = 'mr-IN'
        elif language == 'hi':
            lang_code = 'hi-IN'
        else:
            lang_code = 'en-US'
        
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language=lang_code)
            return text
    except Exception as e:
        logging.error(f"Speech-to-text error: {str(e)}")
        return None



# ======================
# CHATBOT ENHANCEMENTS
# ======================
chat_sessions = {}  # Stores conversation history

@app.route("/start-chat", methods=["POST"])
def start_chat():
    """Initialize a new chat session"""
    session_id = str(uuid.uuid4())
    chat_sessions[session_id] = {
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    return jsonify({"session_id": session_id})

@app.route("/chat-enhanced", methods=["POST"])
def enhanced_chat():
    """Enhanced chat with Framer-like features"""
    session_id = request.json.get("session_id")
    user_message = request.json.get("message", "").strip()
    language = request.json.get("language", "en")
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    # Store user message
    if session_id in chat_sessions:
        chat_sessions[session_id]["messages"].append({
            "sender": "user",
            "text": user_message,
            "timestamp": datetime.now().isoformat()
        })
    
    # Generate bot response (simulate typing delay)
    bot_response = get_bot_response(user_message)
    
    # Add quick reply options (example)
    quick_replies = []
    if "disease" in user_message.lower():
        quick_replies = ["Show me images", "Treatment options", "Prevention tips"]
    
    # Store bot response
    if session_id in chat_sessions:
        chat_sessions[session_id]["messages"].append({
            "sender": "bot",
            "text": bot_response,
            "quick_replies": quick_replies,
            "timestamp": datetime.now().isoformat()
        })
    
    return jsonify({
        "response": bot_response,
        "quick_replies": quick_replies,
        "session_id": session_id
    })

@app.route("/chat-history/<session_id>")
def get_chat_history(session_id):
    """Retrieve conversation history"""
    return jsonify(chat_sessions.get(session_id, {}))

# ==============
# MODEL LOADING
# ==============
MODEL_PATH = r"C:\\FarmGenius\\runs\\train\\crop_disease_yolo3\\weights\\best.pt"
try:
    model = YOLO(MODEL_PATH)
    logging.info("YOLO model loaded successfully from %s", MODEL_PATH)
except Exception as e:
    logging.error("Failed to load YOLO model: %s", str(e))
    model = None

# =================
# DISEASE INFO
# =================
DISEASE_INFO_PATH = r"C:\\FarmGenius\\info.json"
try:
    if os.path.exists(DISEASE_INFO_PATH):
        with open(DISEASE_INFO_PATH, 'r') as f:
            disease_info = json.load(f)
        logging.info("Disease info loaded successfully from %s", DISEASE_INFO_PATH)
    else:
        logging.warning("Disease info file not found at %s", DISEASE_INFO_PATH)
        disease_info = {}
except Exception as e:
    logging.error("Error loading disease info: %s", str(e))
    disease_info = {}

# =================
# WEATHER API
# =================
WEATHER_API_KEY = "78fd66d611dc14f93972a5923b9cf237"
BASE_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    """Fetch weather data for a given city"""
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(BASE_WEATHER_URL, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "city": city,
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"]
        }
    except requests.exceptions.RequestException as e:
        logging.error("Weather API error: %s", str(e))
        return None

# =================
# ROUTES
# =================

@app.route("/")
def index():
    """Main page route"""
    return render_template("index.html")

@app.route("/languages")
def get_languages():
    """Get supported languages"""
    return jsonify({"languages": SUPPORTED_LANGUAGES})

@app.route("/text-to-speech", methods=["POST"])
def handle_text_to_speech():
    """Convert text to speech audio"""
    data = request.json
    text = data.get("text", "")
    language = data.get("language", "en")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    audio_filename = text_to_speech(text, language)
    if audio_filename:
        return jsonify({
            "audio_url": f"/audio/{audio_filename}",
            "language": language
        })
    else:
        return jsonify({"error": "Failed to generate speech"}), 500

@app.route("/speech-to-text", methods=["POST"])
def handle_speech_to_text():
    """Convert speech audio to text"""
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    language = request.form.get("language", "en")
    
    if audio_file.filename == '':
        return jsonify({"error": "No audio file selected"}), 400
    
    try:
        # Save temporary audio file
        temp_filename = f"temp_{uuid.uuid4()}.wav"
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        audio_file.save(temp_path)
        
        # Convert to text
        text = speech_to_text(temp_path, language)
        
        # Clean up
        os.remove(temp_path)
        
        if text:
            return jsonify({
                "text": text,
                "language": language
            })
        else:
            return jsonify({"error": "Could not recognize speech"}), 400
    except Exception as e:
        logging.error("Speech recognition error: %s", str(e))
        return jsonify({"error": "Error processing audio"}), 500

@app.route("/audio/<filename>")
def get_audio(filename):
    """Serve generated audio files"""
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chatbot messages"""
    user_message = request.form.get("message", "").strip()
    language = request.form.get("language", "en")
    
    if not user_message:
        return jsonify({"response": "Please enter a message."})
    
    try:
        bot_response = get_bot_response(user_message)
        
        # Add audio generation if requested
        if request.form.get("generate_audio") == "true":
            audio_filename = text_to_speech(bot_response, language)
            audio_url = f"/audio/{audio_filename}" if audio_filename else None
            return jsonify({
                "response": bot_response,
                "audio_url": audio_url,
                "language": language
            })
        
        return jsonify({"response": bot_response})
    except Exception as e:
        logging.error("Chat error: %s", str(e))
        return jsonify({"response": "Error processing your message."})

@app.route("/weather", methods=["POST"])
def weather():
    """Handle weather requests"""
    city = request.form.get("city", "").strip()
    language = request.form.get("language", "en")
    
    if not city:
        return jsonify({"response": "Please enter a city."})

    weather_data = get_weather(city)
    if weather_data:
        # Add audio generation if requested
        if request.form.get("generate_audio") == "true":
            weather_text = f"Weather in {weather_data['city']}: Temperature {weather_data['temp']}°C, {weather_data['description']}, Humidity {weather_data['humidity']}%"
            audio_filename = text_to_speech(weather_text, language)
            weather_data['audio_url'] = f"/audio/{audio_filename}" if audio_filename else None
        
        weather_data['language'] = language
        return jsonify({"response": weather_data})
    else:
        return jsonify({"response": "Could not fetch weather data. Please try again later."})

@app.route("/upload", methods=["POST"])
def upload():
    """Handle image uploads for disease detection"""
    if model is None:
        return jsonify({"response": "Model not loaded. Please check the server configuration."})

    if 'image' not in request.files:
        return jsonify({"response": "No image found in the request."})

    file = request.files['image']
    if file.filename == '':
        return jsonify({"response": "No image selected."})

    if not allowed_file(file.filename):
        return jsonify({"response": "Unsupported file format. Please upload JPG, JPEG, or PNG."})

    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(image_path)

        # Convert image to base64 for response
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{image_base64}"

        # Process image with YOLO model
        results = model.predict(image_path, conf=0.3)
        names = results[0].names
        detections = results[0].boxes.cls.tolist() if results[0].boxes else []
        confidences = results[0].boxes.conf.tolist() if results[0].boxes else []

        seen = set()
        response_messages = []

        for idx, conf in zip(detections, confidences):
            disease_label = names[int(idx)]
            if disease_label not in seen and conf > 0.3:
                seen.add(disease_label)

                info = disease_info.get(disease_label, {})
                description = info.get("description", "No description available.")
                precautions = info.get("precautions", [])

                message = f"""
🦠 Disease: {disease_label}
🔍 Confidence: {conf:.2f}
📖 Description:
{description}

✅ Precautions:"""
                if precautions:
                    for p in precautions:
                        message += f"\n- {p}"
                else:
                    message += "\n- No specific precautions listed."

                message += "\n" + "-" * 60
                response_messages.append(message.strip())

        response_data = {
            "response": "\n\n".join(response_messages) if response_messages else "No visible disease detected in the image.",
            "image_data": image_data_url
        }

        # Add audio generation if requested
        language = request.form.get("language", "en")
        if request.form.get("generate_audio") == "true":
            audio_filename = text_to_speech(response_data["response"], language)
            if audio_filename:
                response_data["audio_url"] = f"/audio/{audio_filename}"
                response_data["language"] = language

        return jsonify(response_data)

    except Exception as e:
        logging.error("Upload processing error: %s", str(e))
        return jsonify({"response": f"Error while processing image: {str(e)}"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/key")
def key():
    """Disease key information page"""
    return render_template("key.html")

@app.route("/map")
def map_view():
    """Serve the crop map HTML file"""
    MAP_FILE_PATH = r"C:\Users\ASUS\Downloads\maharashtra_crop_info_map_with_prices_and_seasons.html"
    return send_from_directory(os.path.dirname(MAP_FILE_PATH), os.path.basename(MAP_FILE_PATH))

# =================
# APPLICATION ENTRY
# =================
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)