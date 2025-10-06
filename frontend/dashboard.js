// Initialize the map and set its view
const map = L.map('map').setView([20, 0], 2.5);

// Add a dark-themed map layer from CartoDB
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Function to draw an attack on the map
function drawAttack(attack) {
    const source = L.latLng(attack.source.lat, attack.source.lon);
    const target = L.latLng(attack.target.lat, attack.target.lon);

    // Draw a pulsing dot for the source
    const sourceCircle = L.circle(source, {
        radius: 50000,
        color: '#ef4444',
        fillColor: '#ef4444',
        fillOpacity: 0.8
    }).addTo(map);

    // Add a pulsing animation to the source dot
    sourceCircle.getElement().classList.add('pulse');

    // Draw a curved line from source to target
    const latlngs = [
        [source.lat, source.lng],
        [target.lat, target.lng]
    ];
    const animatedLine = L.polyline(latlngs, { color: '#ef4444', weight: 2 }).addTo(map);

    // Create a popup with attack details
    animatedLine.bindPopup(`
        <b>Ransomware Attack</b><br>
        <b>Family:</b> ${attack.family}<br>
        <b>From:</b> ${attack.source.city}, ${attack.source.country}<br>
        <b>To:</b> ${attack.target.city}, ${attack.target.country}
    `);

    // Remove the attack visuals after 5 seconds to keep the map clean
    setTimeout(() => {
        map.removeLayer(sourceCircle);
        map.removeLayer(animatedLine);
    }, 5000);
}

// Fetch a new attack from our backend simulator every 3 seconds
setInterval(async () => {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/live-threat');
        const attackData = await response.json();
        drawAttack(attackData);
    } catch (error) {
        console.error("Could not fetch threat data:", error);
    }
}, 3000);

// Add this CSS for the pulsing animation (could be in styles.css too)
const style = document.createElement('style');
style.innerHTML = `
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.5); opacity: 0.2; }
        100% { transform: scale(2.5); opacity: 0; }
    }
    .pulse {
        animation: pulse 1.5s ease-out infinite;
        stroke: none;
    }
`;
document.head.appendChild(style);

// ADD THIS AT THE END OF dashboard.js

const threatFeedList = document.getElementById('threat-feed-list');

async function fetchAndDisplayThreatIntel() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/threat-intel');
        const intelData = await response.json();

        if (intelData.error) {
            threatFeedList.innerHTML = `<li>Error: ${intelData.error}</li>`;
            return;
        }

        threatFeedList.innerHTML = ''; // Clear old data
        intelData.forEach(ip => {
            const listItem = document.createElement('li');
            listItem.classList.add('feed-item');
            listItem.innerHTML = `
                <strong>IP:</strong> ${ip.ipAddress}<br>
                <strong>Country:</strong> ${ip.countryCode || 'N/A'}<br>
                <strong>Reported:</strong> ${ip.abuseConfidenceScore}% confidence
            `;
            threatFeedList.appendChild(listItem);
        });

    } catch (error) {
        console.error("Could not fetch threat intel:", error);
        threatFeedList.innerHTML = `<li>Error connecting to server.</li>`;
    }
}

// Fetch the data when the page loads, and then every 15 minutes
fetchAndDisplayThreatIntel();
setInterval(fetchAndDisplayThreatIntel, 900000); // 15 minutes in ms