RaaS Awareness, Prevention & Recovery Suite
A comprehensive, multi-featured web application designed to combat the threat of Ransomware-as-a-Service (RaaS) by providing tools for awareness, prevention, and post-attack recovery.

📜 Description
This project addresses the rising threat of ransomware by creating a single, user-friendly platform that does more than just detect threats. It serves as an all-in-one security utility that educates users about the RaaS business model, provides intelligent tools to prevent attacks, and offers a "first-aid kit" to guide victims through the critical steps of recovery. The application integrates machine learning, real-time threat intelligence, a generative AI chatbot, and proactive defensive tools to provide a holistic approach to cybersecurity.

✨ Features
This application is composed of several powerful, interconnected modules:

🤖 AI-Powered Filename Analysis: Uses a Machine Learning model (trained with Scikit-learn) to analyze filenames and predict the likelihood of them being ransomware, going beyond simple rule-based checks.

📂 File Content Scanner: Allows users to upload files to perform a deeper analysis, checking for high entropy (a common sign of encrypted or packed malware) and scanning for suspicious keywords.

🗺️ Live Cyber Threat Dashboard: A professional dashboard featuring:

A live animated map simulating global ransomware attacks in real-time.

A real threat intelligence feed that pulls the latest reported malicious IP addresses from the AbuseIPDB API.

💬 AI Chatbot Assistant: An integrated chatbot powered by the Google Gemini API that acts as a cybersecurity expert, answering user questions about ransomware, phishing, and online safety.

🚑 Ransomware Recovery Tool: A crisis-response utility for victims. Users can input clues (encrypted filename, ransom note text), and the tool identifies the ransomware family, advises on whether a free decryptor exists, and provides a step-by-step recovery plan.

🛡️ Canary File (Honeypot) Generator: A proactive defensive tool. Users can generate a custom Python "watcher" script that creates and monitors decoy files in any folder. If ransomware touches a decoy file, a loud, unmissable alert pops up on the user's screen, enabling them to stop the attack in progress.

👨‍🏫 Interactive Learning Modules:

An Attack Simulation that walks the user through a realistic phishing and encryption scenario.

An Animated RaaS Business Model Explainer that visually breaks down how the RaaS economy functions.

🛠️ Tech Stack
Backend: Python, Flask

Machine Learning: Scikit-learn, Pandas

Generative AI: Google Gemini API

Frontend: HTML5, CSS3, JavaScript (Vanilla JS)

Mapping Library: Leaflet.js

External APIs: AbuseIPDB API for threat intelligence

🚀 Setup and Usage
Follow these steps to run the project locally.

1.  Prerequisites
    Python 3.8 or newer
    pip (Python package installer)
    VS Code with the Live Server extension (recommended)

2.  Installation

    1. Clone the repository:
       Bash
       git clone https://github.com/StealthPanther/RaaS-Defense-Platform.git

    2. Navigate to the project's root directory.

    3. Create a requirements.txt file by running this command in the terminal to list all the packages you installed:
       Bash
       pip freeze > requirements.txt

    4. Install the required Python packages:
       Bash
       pip install -r requirements.txt

3.  Configuration
    You must add your secret API keys in the backend/app.py file:

    GOOGLE_API_KEY: For the AI Chatbot.
    ABUSEIPDB_API_KEY: For the Threat Intelligence Feed.

4.  Running the Application
    The project requires two terminals to run the backend and frontend.

    -To Start the Backend Server:

    Bash
    cd backend
    python app.py

    The server will start on http://127.0.0.1:5000.

    -To Start the Frontend:

    In VS Code, right-click on the frontend/index.html file.

    Select "Open with Live Server".

    Your browser will open the application.

🔭 Future Scope
This project has a strong foundation that can be extended with several professional features:

Desktop Application: Package the entire project into a standalone desktop application (.exe or .dmg) using PyWebView and PyInstaller, eliminating the need for terminals and making it accessible to any user.

Advanced Canary File System: Integrate the Canary File watcher directly into the desktop application, allowing it to be started and stopped from the UI and run as a true background service that launches on system startup.

Native Folder Picker: Use the desktop application's capabilities to provide a native "Select Folder" dialog, allowing users to easily choose which directories to protect with the Canary File system.
