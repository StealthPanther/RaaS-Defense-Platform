// Get references to all the steps/scenes
const emailStep = document.getElementById('email-step');
const encryptionStep = document.getElementById('encryption-step');
const ransomNoteStep = document.getElementById('ransom-note-step');
const lessonStep = document.getElementById('lesson-step');
const allSteps = [emailStep, encryptionStep, ransomNoteStep, lessonStep];

// Get references to interactive elements
const openAttachmentBtn = document.getElementById('open-attachment-btn');
const payBtn = document.getElementById('pay-btn');
const dontPayBtn = document.getElementById('dont-pay-btn');
const lessonContent = document.getElementById('lesson-content');

// --- Simulation Flow Control ---

// Function to hide all steps and show only the current one
function showStep(stepToShow) {
    allSteps.forEach(step => step.classList.add('hidden'));
    stepToShow.classList.remove('hidden');
}

// Event listener for the "Open Attachment" button
openAttachmentBtn.addEventListener('click', () => {
    showStep(encryptionStep);
    startFakeEncryption();
});

// Event listeners for the ransom note buttons
payBtn.addEventListener('click', () => {
    showStep(lessonStep);
    lessonContent.innerHTML = `
        <h3>You Chose to Pay...</h3>
        <p>While it seems like the easy way out, paying the ransom is risky. There's no guarantee you'll get your files back, and it funds criminal organizations, encouraging more attacks.</p>
        <p><b>The Real-World Solution:</b> Never pay the ransom. The best defense is to have offline backups of your important files. You can restore your system and files from a clean backup without paying criminals.</p>
    `;
});

dontPayBtn.addEventListener('click', () => {
    showStep(lessonStep);
    lessonContent.innerHTML = `
        <h3>You Chose Not to Pay. Correct!</h3>
        <p>This is the recommended course of action. You resisted the pressure and did not fund the criminals.</p>
        <p><b>The Real-World Solution:</b> The next step in a real scenario would be to disconnect the infected machine from the network, reformat it, and restore your data from a clean, recent backup. This highlights why backups are the ultimate defense against ransomware.</p>
    `;
});

// --- Fake Encryption Simulation ---

function startFakeEncryption() {
    let progress = 0;
    const progressBar = document.getElementById('encryption-progress');
    const filesLog = document.getElementById('encrypted-files-log');
    const fakeFiles = [
        'C:/Users/You/Documents/resume.docx',
        'C:/Users/You/Photos/vacation_2025.jpg',
        'C:/Users/You/Photos/family_photo.png',
        'C:/Users/You/Desktop/passwords.txt',
        'D:/Work/project_alpha.mpp',
        'D:/Work/financials_q3.xlsx'
    ];
    
    const interval = setInterval(() => {
        progress += 2;
        progressBar.style.width = progress + '%';
        
        // Add a new "encrypted" file to the log
        if (progress % 10 === 0 && fakeFiles.length > 0) {
            const fileToEncrypt = fakeFiles.shift();
            const logEntry = document.createElement('p');
            logEntry.textContent = `ENCRYPTING: ${fileToEncrypt} -> ${fileToEncrypt}.locked`;
            filesLog.appendChild(logEntry);
            filesLog.scrollTop = filesLog.scrollHeight; // Auto-scroll
        }
        
        if (progress >= 100) {
            clearInterval(interval);
            // Wait a moment, then show the ransom note
            setTimeout(() => {
                showStep(ransomNoteStep);
                startCountdown();
            }, 500);
        }
    }, 100); // Update every 100ms
}

// --- Countdown Timer for Ransom Note ---

function startCountdown() {
    const timerDisplay = document.getElementById('countdown-timer');
    let time = 72 * 3600; // 72 hours in seconds

    const countdownInterval = setInterval(() => {
        time--;
        const hours = Math.floor(time / 3600);
        const minutes = Math.floor((time % 3600) / 60);
        const seconds = time % 60;
        
        // Format to always have two digits
        const fHours = String(hours).padStart(2, '0');
        const fMinutes = String(minutes).padStart(2, '0');
        const fSeconds = String(seconds).padStart(2, '0');

        timerDisplay.textContent = `${fHours}:${fMinutes}:${fSeconds}`;

        if (time <= 0) {
            clearInterval(countdownInterval);
            timerDisplay.textContent = "TIME'S UP!";
        }
    }, 1000);
}