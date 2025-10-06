const analyzeBtn = document.getElementById('analyze-situation-btn');
const filenameInput = document.getElementById('encrypted-filename');
const noteInput = document.getElementById('ransom-note');
const planArea = document.getElementById('recovery-plan-area');
const loadingState = document.getElementById('loading-state');
const loadingSpinner = document.querySelector('.loading-spinner');

analyzeBtn.addEventListener('click', async () => {
    const filename = filenameInput.value;
    const note_text = noteInput.value;

    if (!filename && !note_text) {
        alert('Please provide at least one clue (a filename or the ransom note text).');
        return;
    }

    // --- Start Loading State ---
    planArea.classList.add('hidden');
    planArea.classList.remove('visible');
    loadingState.classList.remove('hidden');
    loadingSpinner.classList.remove('hidden');
    analyzeBtn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/analyze-victim', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, note_text })
        });

        const plan = await response.json();

        // --- End Loading State ---
        loadingState.classList.add('hidden');
        loadingSpinner.classList.add('hidden');
        analyzeBtn.disabled = false;

        // --- Display Results ---
        displayRecoveryPlan(plan);

    } catch (error) {
        console.error("Analysis error:", error);
        loadingState.classList.add('hidden');
        loadingSpinner.classList.add('hidden');
        analyzeBtn.disabled = false;
        alert('An error occurred. Could not connect to the analysis server.');
    }
});

function displayRecoveryPlan(plan) {
    let decryptorHTML = '';

    if (plan.decryptor_available) {
        decryptorHTML = `
            <div class="advice-box" style="border-left-color: var(--success-color);">
                <h3>Good News: A Decryptor May Be Available!</h3>
                <p>A free tool might exist to recover your files. Be sure to use a legitimate source.</p>
                <p><strong>Recommended Resource:</strong> <a href="${plan.decryptor_link}" target="_blank" rel="noopener noreferrer">Check for a decryptor here</a></p>
            </div>`;
    } else {
        decryptorHTML = `
            <div class="advice-box" style="border-left-color: var(--danger-color);">
                <h3>Decryptor Status: Not Available</h3>
                <p>Unfortunately, there is no known public decryptor for this ransomware. Your best option is to restore your files from a clean backup.</p>
            </div>`;
    }

    planArea.innerHTML = `
        <h2>Your Recovery Plan</h2>
        <h3>Threat Identification</h3>
        <p><strong>Identified Ransomware Family:</strong> ${plan.identified_family}</p>
        <p><strong>Information:</strong> ${plan.info}</p>
        <h3>Immediate Actions</h3>
        <ol>
            <li><strong>ISOLATE:</strong> Disconnect the infected computer from the internet and any network immediately.</li>
            <li><strong>DO NOT PAY:</strong> It is not recommended to pay the ransom. There is no guarantee you will get your files back.</li>
            <li><strong>BACKUPS:</strong> Locate your offline or cloud backups. This is the safest way to recover your data.</li>
            <li><strong>REPORT:</strong> Report the crime to your local cybercrime authorities (e.g., CERT-In in India).</li>
        </ol>
        <h3>Decryption Possibility</h3>
        ${decryptorHTML}`;

    planArea.classList.remove('hidden');
    // Use a tiny timeout to allow the browser to render the element before animating it
    setTimeout(() => {
        planArea.classList.add('visible');
    }, 10);
}