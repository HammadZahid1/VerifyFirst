const analyzeBtn = document.getElementById('analyze-btn');
const inputField = document.getElementById('news-input');
const inputCard = document.getElementById('input-card');
const resultCard = document.getElementById('result-card');
const scoreValue = document.getElementById('score-value');
const statusBadge = document.getElementById('status-badge');
const reasonsList = document.getElementById('reasons-list');

// Configuration
const API_URL = "http://localhost:5000/predict";

analyzeBtn.addEventListener('click', async () => {
    const text = inputField.value.trim();
    if (!text) return;

    // UI Loading State
    setLoading(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            setLoading(false);
            return;
        }

        // Simulate a small delay for "Analysis" feel if API is too fast
        setTimeout(() => {
            showResults(data);
        }, 800);

    } catch (error) {
        console.error("Error:", error);
        // Fallback for network error - still show "Uncertain" as per requirements
        showResults({
            credibility_score: 50,
            label: "Uncertain",
            classification: "UNCERTAIN",
            reasons: ["Network connection to analysis server failed."]
        });
    }
});

function setLoading(isLoading) {
    if (isLoading) {
        const originalText = analyzeBtn.querySelector('span').innerText;
        analyzeBtn.innerHTML = `<div class="spinner"></div><span class="ml-2">Analyzing...</span>`;
        analyzeBtn.disabled = true;
        analyzeBtn.classList.add('opacity-80', 'cursor-not-allowed');
    } else {
        analyzeBtn.innerHTML = `<span>Analyze Credibility</span>
        <svg class="w-5 h-5 group-hover:rotate-180 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`;
        analyzeBtn.disabled = false;
        analyzeBtn.classList.remove('opacity-80', 'cursor-not-allowed');
    }
}

function showResults(data) {
    setLoading(false);

    // Update Score Color
    let scoreColor = "text-white";
    if (data.classification === "REAL") scoreColor = "text-green-400";
    else if (data.classification === "FAKE") scoreColor = "text-red-500";
    else scoreColor = "text-yellow-400";

    scoreValue.className = `text-6xl font-bold ${scoreColor}`;
    scoreValue.innerText = `${data.credibility_score}%`;

    // Update Badge
    updateBadge(data.label, data.classification);

    // Update Reasons
    reasonsList.innerHTML = "";
    data.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.className = "flex items-start gap-3 text-gray-300";
        li.innerHTML = `
            <svg class="w-5 h-5 text-neonCyan mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>${reason}</span>
        `;
        reasonsList.appendChild(li);
    });

    // Show Result Card
    resultCard.classList.remove('hidden');
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function updateBadge(label, classification) {
    let classes = "";
    let icon = "";

    if (classification === "REAL") {
        classes = "bg-green-900/30 text-green-400 border-green-800";
        icon = "🟢";
    } else if (classification === "FAKE") {
        classes = "bg-red-900/30 text-red-400 border-red-800";
        icon = "🔴";
    } else {
        classes = "bg-yellow-900/30 text-yellow-400 border-yellow-800";
        icon = "🟡";
    }

    statusBadge.className = `px-4 py-2 rounded-full font-bold text-sm border flex items-center gap-2 w-max ${classes}`;
    statusBadge.innerHTML = `<span>${icon}</span> ${label.toUpperCase()}`;
}

function resetApp() {
    resultCard.classList.add('hidden');
    inputField.value = "";
    inputField.focus();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
