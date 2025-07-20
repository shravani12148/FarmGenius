# 🌾 Farm-Genius

Smart way to Grow the Right way to Farm 🌱  
An AI-powered precision agriculture system that provides:
- Crop recommendations based on location, soil type, and climate
- Plant disease detection and advice using AI
- Chatbot assistant for farmers in multiple languages
- Weather-based smart suggestions

---

## 🚀 Features

- 🌍 Location-based climate and soil analysis
- 🤖 AI chatbot for crop and disease queries
- 🧠 AI model integration for disease detection
- ☁️ Live weather data via API
- 📱 Voice and image input support
- 🗺️ Map integration for location assistance

---

## 🛠️ How to Run the Project

```bash
# Clone the repository
git clone https://github.com/your-username/farm-genius.git

# Navigate to the project folder
cd farm-genius

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python main.py

Project Structure:-

farmgenius/
├── app.py                # Main Python file for the Flask app
├── requirements.txt      # Project dependencies
├── templates/            # Folder containing all HTML files
│   ├── index.html        # Main page of the app
│   ├── dashboard.html    # Dashboard page
│   └── ...               # Other HTML templates
├── static/               # Folder for static files (CSS, JS, images)
│   ├── styles.css        # CSS file for styling
│   ├── script.js         # JavaScript file for interactivity
│   └── ...               # Other static files
└── models/               # Folder for machine learning models (if applicable)
    └── disease_model.h5  # Trained AI model for disease detection
