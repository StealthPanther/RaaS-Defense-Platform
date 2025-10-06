from flask import Flask, request, jsonify, Response
import json
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import google.generativeai as genai
import math # Add this line at the top
import random
import time
# ADD THIS AT THE TOP OF app.py
import requests

# --- AI Model Training (Filename Analyzer) ---
try:
    df = pd.read_csv('filenames.csv')
    filenames = df['filename'].tolist()
    labels = df['label'].tolist()
    filename_model = make_pipeline(CountVectorizer(analyzer='char', ngram_range=(2, 4)), MultinomialNB())
    filename_model.fit(filenames, labels)
    print("✅ Filename AI Model trained successfully!")
except Exception as e:
    print(f"❌ Error training filename model: {e}")
    filename_model = None

# --- AI Chatbot Configuration (Gemini) ---
try:
    # IMPORTANT: PASTE YOUR API KEY HERE    AIzaSyCcErf-Dejf5VwhHW7b2-1NXLHVaH9nbo0
    GOOGLE_API_KEY = "AIzaSyCcErf-Dejf5VwhHW7b2-1NXLHVaH9nbo0" 
    genai.configure(api_key=GOOGLE_API_KEY)
    chat_model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ AI Chatbot configured successfully!")
except Exception as e:
    print(f"❌ Error configuring chatbot model: {e}")
    chat_model = None

# --- Flask Web Server ---
app = Flask(__name__)
CORS(app)

# --- Endpoint for Filename Analysis ---
@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    # ... (This function remains the same as before)
    data = request.get_json()
    filename = data.get('filename', '')
    if not filename: return jsonify({"error": "No filename provided"}), 400
    if not filename_model: return jsonify({"error": "Filename AI model is not available."})

    prediction = filename_model.predict([filename])
    probability = filename_model.predict_proba([filename])
    is_malicious = (prediction[0] == 1)
    confidence = probability[0][1]

    if is_malicious:
        score = int(75 + (confidence * 25))
        level, advice, reasons = "High-Risk/AI Detected 🔴", f"Our AI model is {confidence:.0%} confident this is a malicious filename pattern.", ["AI analysis detected patterns commonly associated with ransomware."]
    else:
        score = int(confidence * 100)
        level, advice, reasons = "Benign/AI Detected ✅", f"Our AI model is {1-confidence:.0%} confident this is a benign filename.", ["AI analysis did not find patterns associated with ransomware."]
    
    return jsonify({"score": score, "level": level, "reasons": reasons, "advice": advice})

# --- NEW Endpoint for AI Chatbot ---
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    if not chat_model:
        return jsonify({"reply": "Sorry, the AI chatbot is not available right now."})

    try:
        # This is a system prompt to keep the AI on topic.
        prompt = f"""You are a friendly and helpful cybersecurity assistant named CyBot.
        Your sole purpose is to answer questions about ransomware, malware, phishing, and general online safety.
        Politely refuse to answer any questions outside of this topic.
        User's question: "{user_message}"
        """
        response = chat_model.generate_content(prompt)
        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Error during chat generation: {e}")
        return jsonify({"reply": "Sorry, I encountered an error. Please try again."})
    
# --- NEW: FILE CONTENT ANALYSIS FUNCTIONS ---

def calculate_entropy(data):
    """Calculates the entropy of a byte string."""
    if not data:
        return 0, "Normal"
    
    entropy = 0
    for x in range(256):
        p_x = float(data.count(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    
    # Classify the entropy level
    if entropy > 7.5:
        level = "Very High (Suspicious)"
    elif entropy > 7.0:
        level = "High (Potentially Suspicious)"
    else:
        level = "Normal"
        
    return entropy, level

def scan_for_strings(content):
    """Scans text content for suspicious keywords."""
    suspicious_strings = {
        "bitcoin", "wallet", "encrypt", "decrypt", "ransom", "tor ",
        "admin", "root ", "powershell", "invoke-expression", "payload",
        "secret", "private key"
    }
    found_strings = []
    
    # We decode with errors='ignore' to handle non-text files gracefully
    text_content = content.decode('utf-8', errors='ignore').lower()
    
    for s_string in suspicious_strings:
        if s_string in text_content:
            found_strings.append(s_string)
            
    return found_strings

# --- NEW: API ENDPOINT FOR FILE ANALYSIS ---
@app.route('/analyze-file', methods=['POST'])
def analyze_file_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        file_content = file.read()
        
        # Perform analyses
        entropy_score, entropy_level = calculate_entropy(file_content)
        found_keywords = scan_for_strings(file_content)
        
        return jsonify({
            "filename": file.filename,
            "filesize": len(file_content),
            "entropy_score": f"{entropy_score:.4f}",
            "entropy_level": entropy_level,
            "found_keywords": found_keywords
        })

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500    

# --- NEW: LIVE THREAT SIMULATOR ---
# A list of cities with their coordinates and country for realistic simulation
CITIES = [
    {"city": "New York", "lat": 40.7128, "lon": -74.0060, "country": "USA"},
    {"city": "London", "lat": 51.5074, "lon": -0.1278, "country": "UK"},
    {"city": "Tokyo", "lat": 35.6895, "lon": 139.6917, "country": "Japan"},
    {"city": "Pune", "lat": 18.5204, "lon": 73.8567, "country": "India"},
    {"city": "Sydney", "lat": -33.8688, "lon": 151.2093, "country": "Australia"},
    {"city": "Moscow", "lat": 55.7558, "lon": 37.6173, "country": "Russia"},
    {"city": "Beijing", "lat": 39.9042, "lon": 116.4074, "country": "China"},
    {"city": "São Paulo", "lat": -23.5505, "lon": -46.6333, "country": "Brazil"},
]
RANSOMWARE_FAMILIES = ["WannaCry", "Ryuk", "Conti", "LockBit", "REvil", "CryptoLocker"]

@app.route('/api/live-threat')
def live_threat():
    source = random.choice(CITIES)
    target = random.choice([c for c in CITIES if c != source]) # Ensure target is different
    
    attack_data = {
        "source": source,
        "target": target,
        "family": random.choice(RANSOMWARE_FAMILIES),
        "timestamp": int(time.time() * 1000)
    }
    return jsonify(attack_data)
    


# --- NEW: REAL THREAT INTELLIGENCE FEED --- 2169eb1cbb1ef34eab6789672466fa65a704b3090601e23919d45a40e7c8f0991fb590ff4e1095d6
ABUSEIPDB_API_KEY = "2169eb1cbb1ef34eab6789672466fa65a704b3090601e23919d45a40e7c8f0991fb590ff4e1095d6"
# We will cache the results to avoid hitting the API limit too often
threat_intel_cache = {"data": None, "timestamp": 0}

@app.route('/api/threat-intel')
def get_threat_intel():
    current_time = time.time()
    # Check if cache is older than 15 minutes (900 seconds)
    if current_time - threat_intel_cache["timestamp"] > 900:
        print("Fetching new threat intel data from AbuseIPDB...")
        try:
            headers = {'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'}
            params = {'limit': 50} # Get the 50 most recently reported IPs
            response = requests.get('https://api.abuseipdb.com/api/v2/blacklist', headers=headers, params=params)
            response.raise_for_status() # Raise an exception for bad status codes
            
            # Update cache
            threat_intel_cache["data"] = response.json().get("data", [])
            threat_intel_cache["timestamp"] = current_time
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from AbuseIPDB: {e}")
            # Return old cache data if available, otherwise an error
            if not threat_intel_cache["data"]:
                return jsonify({"error": "Could not fetch threat intelligence data."}), 500

    return jsonify(threat_intel_cache["data"])

# ADD THIS CODE AT THE END of app.py

# --- NEW: CANARY FILE SCRIPT GENERATOR ---

# This is the template for the watcher script we will generate.
# The {file_list} placeholder will be filled in, and the {{...}} are escaped.
SCRIPT_TEMPLATE = """
import os
import time
import hashlib
import tkinter as tk
from tkinter import messagebox

# --- CONFIGURATION ---
# These are the decoy files this script will create and monitor.
DECOY_FILES = {file_list}

# --- DO NOT EDIT BELOW THIS LINE ---

def get_file_hash(filepath):
    \"\"\"Calculates the SHA-256 hash of a file.\"\"\"
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None

def show_alert():
    \"\"\"Displays a critical warning message to the user.\"\"\"
    root = tk.Tk()
    root.withdraw() # Hide the main window
    root.attributes("-topmost", True) # Keep the alert on top of all other windows
    messagebox.showerror(
        "!!! RANSOMWARE ALERT !!!",
        "A decoy file has been modified or deleted!\\n\\n"
        "This is a strong indicator of a RANSOMWARE ATTACK in progress.\\n\\n"
        "IMMEDIATE ACTION RECOMMENDED:\\n"
        "1. DISCONNECT your computer from the Internet NOW.\\n"
        "2. SHUT DOWN your computer to stop further encryption."
    )
    root.destroy()

def main():
    print("--- Ransomware Early Warning System: ACTIVE ---")
    print("This script is now monitoring decoy files. Do not close this window.")
    
    # Create decoy files if they don't exist
    for filename in DECOY_FILES:
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(f"This is a decoy file for ransomware detection. Do not delete or modify. Timestamp: {{time.time()}}")
            print(f"Created decoy file: {{filename}}")
    
    # Get the initial state (hashes) of the decoy files
    initial_hashes = {{f: get_file_hash(f) for f in DECOY_FILES}}
    print("Initial state recorded. Monitoring for changes...")
    
    try:
        while True:
            time.sleep(5) # Check every 5 seconds
            for filename in DECOY_FILES:
                current_hash = get_file_hash(filename)
                if current_hash != initial_hashes.get(filename):
                    print(f"!!! ALERT: Change detected in {{filename}} !!!")
                    print("Initial Hash: ", initial_hashes.get(filename))
                    print("Current Hash: ", current_hash)
                    show_alert()
                    return # Stop monitoring after an alert

    except KeyboardInterrupt:
        print("\\nMonitoring stopped by user.")

if __name__ == "__main__":
    main()
"""

@app.route('/generate-watcher')
def generate_watcher():
    # Get the list of filenames from the URL parameter
    files_json = request.args.get('files', '[]')
    try:
        selected_files = json.loads(files_json)
        if not isinstance(selected_files, list) or not selected_files:
            raise ValueError("Invalid file list")
    except (json.JSONDecodeError, ValueError):
        return "Error: Invalid file selection.", 400
    
    # Format the file list for injection into the Python script template
    file_list_str = str(selected_files)
    
    # Generate the final script content from the template
    final_script = SCRIPT_TEMPLATE.format(file_list=file_list_str)
    
    # Send the generated script to the user as a downloadable file
    return Response(
        final_script,
        mimetype="text/x-python",
        headers={"Content-disposition": "attachment; filename=watcher.py"}
    )
    
# ADD THIS CODE AT THE END of app.py

# --- NEW: RANSOMWARE RECOVERY INTELLIGENCE ---

# This acts as our mini-database of ransomware profiles.
# In a real-world app, this would be a large, constantly updated database.
RANSOMWARE_PROFILES = {
    "WannaCry": {
        "extensions": [".wncry", ".wnryt"],
        "keywords": ["Wanna Decryptor", "send $300 dollars to bitcoin"],
        "decryptor_available": True,
        "decryptor_link": "https://www.nomoreransom.org/en/decryption-tools.html",
        "info": "One of the most infamous ransomware worms. A public decryptor was developed after a flaw was found."
    },
    "LockBit": {
        "extensions": [".lockbit", ".abcd"],
        "keywords": ["LockBit 3.0", "restore-my-files.txt", "personal ID"],
        "decryptor_available": False,
        "decryptor_link": None,
        "info": "A highly active and professional Ransomware-as-a-Service group. No public decryptor is available."
    },
    "Conti": {
        "extensions": [".CONTI", ".contiv2"],
        "keywords": ["Conti News", "CONTI_README.txt"],
        "decryptor_available": True,
        "decryptor_link": "https://www.nomoreransom.org/en/decryption-tools.html",
        "info": "A notorious RaaS group. After internal chats were leaked, some decryption keys became available."
    },
    "STOP/Djvu": {
        "extensions": [".djvu", ".promos"],
        "keywords": ["_readme.txt", "don't worry, you can return all your files"],
        "decryptor_available": True,
        "decryptor_link": "https://www.emsisoft.com/ransomware-decryption-tools/stop-djvu",
        "info": "One of the most common families targeting home users. Decryption is possible for many variants if the files were encrypted with an 'offline key'."
    }
}

@app.route('/analyze-victim', methods=['POST'])
def analyze_victim():
    data = request.json
    filename = data.get('filename', '').lower()
    note_text = data.get('note_text', '').lower()

    identified_family = "Unknown"
    profile = None

    # Try to identify the ransomware by its indicators
    for family, indicators in RANSOMWARE_PROFILES.items():
        # Check by file extension
        for ext in indicators["extensions"]:
            if filename.endswith(ext):
                identified_family = family
                profile = indicators
                break
        if profile: break

        # Check by keywords in the ransom note
        for keyword in indicators["keywords"]:
            if keyword.lower() in note_text:
                identified_family = family
                profile = indicators
                break
        if profile: break

    # Prepare the recovery plan
    if profile:
        recovery_plan = {
            "identified_family": identified_family,
            "info": profile["info"],
            "decryptor_available": profile["decryptor_available"],
            "decryptor_link": profile["decryptor_link"]
        }
    else:
        recovery_plan = {
            "identified_family": "Unknown",
            "info": "We could not identify the ransomware family from the information provided. The steps below are general best practices.",
            "decryptor_available": False,
            "decryptor_link": None
        }

    return jsonify(recovery_plan)    

# --- Run the Server ---
if __name__ == '__main__':
    app.run(debug=True)