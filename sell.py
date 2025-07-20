import json
import sys
import io

# Ensure UTF-8 support for printing emojis in Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Function to load the crop price data from a JSON file
def load_crop_data(filename=r"C:\FarmGenius\sell.json"):
    with open(filename, 'r', encoding='utf-8') as f:  # Add encoding to handle special chars
        return json.load(f)

# Function to recommend where to sell a crop
def recommend_market(crop, crop_data):
    crop = crop.lower()  # Convert the crop name to lowercase to handle case-insensitivity

    if crop in crop_data:
        info = crop_data[crop]
        response = (
            f"📍 Sell your {crop} at {info['location']} – {info['price']}\n"
            f"🕐 Best days to sell: {info['best_days']}\n"
            f"✅ Tip: {info['tip']}"
        )
    else:
        response = (
            f"Sorry, I don't have market info for '{crop}' right now.\n"
            "Try checking eNAM or your local APMC."
        )
    return response

# Load the crop data from the JSON file
crop_data = load_crop_data()

# Example of using the function
user_input_crop = "soybean"
reply = recommend_market(user_input_crop, crop_data)
print(reply)
