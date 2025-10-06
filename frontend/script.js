// Get references to our HTML elements
const analyzeBtn = document.getElementById('analyze-btn');
const filenameInput = document.getElementById('filename-input');
const resultsArea = document.getElementById('results-area');
const threatLevelText = document.getElementById('threat-level-text');
const meterBar = document.getElementById('meter-bar');
const reasonsList = document.getElementById('reasons-list');
const adviceText = document.getElementById('advice-text');

// Listen for a click on the "Analyze" button
analyzeBtn.addEventListener('click', () => {
    const filename = filenameInput.value;

    // Make sure the user typed something
    if (!filename) {
        alert("Please enter a filename to analyze.");
        return;
    }

    // This is the core function that talks to our Python backend
    fetch('http://127.0.0.1:5000/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json()) // Get the response and turn it into a JavaScript object
    .then(data => {
        // Now we have the analysis data from Python! Let's display it.
        displayResults(data);
    })
    .catch(error => {
        // Handle errors, like if the Python server isn't running
        console.error("Error:", error);
        alert("Could not connect to the analysis server. Make sure the backend is running.");
    });
});

function displayResults(data) {
    // Make the results area visible
    resultsArea.classList.remove('hidden');

    // Update the threat level text
    threatLevelText.textContent = data.level;

    // Update the meter bar width and color
    const score = Math.min(data.score, 100); // Cap score at 100 for the bar
    meterBar.style.width = score + '%';
    
    // Remove any old color classes
    meterBar.className = 'meter-bar'; 
    if (score >= 51) {
        meterBar.classList.add('high-risk');
    } else if (score >= 31) {
        meterBar.classList.add('suspicious');
    } else if (score >= 11) {
        meterBar.classList.add('low-risk');
    } else {
        meterBar.classList.add('safe');
    }


    // Display the reasons
    reasonsList.innerHTML = ''; // Clear old reasons
    if (data.reasons.length > 0) {
        let reasonHTML = '<ul>';
        data.reasons.forEach(reason => {
            reasonHTML += `<li>${reason}</li>`;
        });
        reasonHTML += '</ul>';
        reasonsList.innerHTML = reasonHTML;
    }

    // Display the advice with a typewriter effect
    typeWriterEffect(adviceText, data.advice, 20); // 20ms speed
}

function typeWriterEffect(element, text, speed) {
    let i = 0;
    element.innerHTML = ""; // Clear existing text
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// ADD THIS CODE AT THE END OF script.js

const chatBox = document.getElementById('chat-box');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('chat-send-btn');

// Function to handle sending a message
async function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (userMessage === '') return;

    // Display user's message
    appendMessage(userMessage, 'user');
    chatInput.value = '';

    // Get bot's response
    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });
        const data = await response.json();
        appendMessage(data.reply, 'bot');
    } catch (error) {
        console.error("Chat error:", error);
        appendMessage("Sorry, I couldn't connect to the AI. Please check the server.", 'bot');
    }
}

// Function to add a message to the chat window
function appendMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
}

// Event listeners for sending message
sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// ADD THIS CODE AT THE END OF script.js

const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');
const fileResultsArea = document.getElementById('file-results-area');
const fileReportContent = document.getElementById('file-report-content');

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameDisplay.textContent = file.name;
        handleFileUpload(file);
    }
});

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show a "loading" message
    fileResultsArea.classList.remove('hidden');
    fileReportContent.innerHTML = '<p>Analyzing file, please wait...</p>';

    try {
        const response = await fetch('http://12.0.0.1:5000/analyze-file', {
            method: 'POST',
            body: formData 
            // Note: Don't set Content-Type header, browser does it for FormData
        });

        const data = await response.json();
        
        if (data.error) {
            fileReportContent.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }

        // Build the HTML report
        let reportHTML = `
            <ul>
                <li><strong>Filename:</strong> ${data.filename}</li>
                <li><strong>File Size:</strong> ${data.filesize} bytes</li>
                <li><strong>Entropy Score:</strong> ${data.entropy_score} <strong>(${data.entropy_level})</strong></li>
                <li><strong>Suspicious Keywords Found:</strong> ${data.found_keywords.length > 0 ? data.found_keywords.join(', ') : 'None'}</li>
            </ul>
        `;
        
        if (data.entropy_level.includes("Suspicious") || data.found_keywords.length > 0) {
            reportHTML += `<p><strong>Verdict:</strong> This file displays characteristics that could be associated with malicious code. Please handle with extreme caution.</p>`;
        } else {
            reportHTML += `<p><strong>Verdict:</strong> No obvious malicious characteristics were found in the file's content.</p>`;
        }
        
        fileReportContent.innerHTML = reportHTML;

    } catch (error) {
        console.error("File upload error:", error);
        fileReportContent.innerHTML = `<p>Error: Could not connect to the analysis server.</p>`;
    }
}