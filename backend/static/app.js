// FaN-De Fake News Detector Client Logic

const API_BASE = window.location.origin;

// State Management
const state = {
    activeTab: 'tab-analyzer',
    isConnected: false,
    trustedFacts: [],
    history: [],
    currentAnalysis: null
};

// Prepopulated sample articles for easy testing
const sampleArticles = {
    "real-1": {
        title: "Certification of 2020 Election",
        text: "On January 6, 2021, the United States Congress met in a joint session to certify the Electoral College votes of the 2020 presidential election. The session was temporarily interrupted when a crowd breached the Capitol building. After order was restored by law enforcement, Congress reconvened and certified the electoral votes, officially confirming Joe Biden victory over the incumbent President Donald Trump. Joe Biden received 306 electoral votes compared to Donald Trump 232 electoral votes."
    },
    "real-2": {
        title: "NASA Artemis Lunar Flight",
        text: "NASA's Artemis program represents a major international effort to establish a sustainable human presence on the Moon. The Space Launch System (SLS) rocket, along with the Orion spacecraft, completed its first uncrewed test flight, gathering critical engineering data. NASA plans to launch crewed missions under Artemis II and III, with the goal of landing the first woman and person of color on the lunar surface, and building a lunar gateway orbital station."
    },
    "fake-1": {
        title: "Autism Vaccine Conspiracy",
        text: "A secret report recently leaked online claims that standard MMR vaccines contain harmful chemical tracking microchips and have been proven to cause autism in children. The study alleges that pharmaceutical companies and global health agencies have conspired to hide this data from the public to maintain profits, despite clear evidence showing a direct correlation between childhood immunizations and developmental delays."
    },
    "fake-2": {
        title: "Hidden Asteroid Collision",
        text: "Leaked documents from a high-level planetary defense coordinator warn that a massive, city-killing asteroid is on a direct collision course with Earth and is expected to strike within the next month. The report claims that NASA and other space agencies have detected this threat but are deliberately hiding the information to prevent global panic and financial market collapse."
    }
};

// DOM Elements
const elements = {
    body: document.body,
    themeToggle: document.getElementById('theme-toggle'),
    connectionPill: document.getElementById('connection-pill'),
    tabButtons: document.querySelectorAll('.tab-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    newsInput: document.getElementById('news-input'),
    charCount: document.getElementById('input-chars'),
    sampleSelector: document.getElementById('sample-selector'),
    toggleLiveRag: document.getElementById('toggle-live-rag'),
    claimsRange: document.getElementById('claims-range'),
    claimsVal: document.getElementById('claims-val'),
    btnAnalyze: document.getElementById('btn-analyze'),
    resultsPlaceholder: document.getElementById('results-placeholder'),
    resultsPanel: document.getElementById('results-panel'),
    scoreText: document.getElementById('score-text'),
    gaugeFill: document.getElementById('gauge-fill'),
    verdictBadge: document.getElementById('verdict-badge'),
    probRealVal: document.getElementById('prob-real-val'),
    probRealFill: document.getElementById('prob-real-fill'),
    probFakeVal: document.getElementById('prob-fake-val'),
    probFakeFill: document.getElementById('prob-fake-fill'),
    claimsList: document.getElementById('claims-list'),
    elementsEvidenceList: document.getElementById('evidence-list'),
    
    // Loader Modal
    loadingOverlay: document.getElementById('loading-overlay'),
    loaderStatus: document.getElementById('loader-status'),
    stepPreprocess: document.getElementById('step-preprocess'),
    stepClaims: document.getElementById('step-claims'),
    stepRag: document.getElementById('step-rag'),
    stepPredict: document.getElementById('step-predict'),
    
    // Database Tab
    addFactForm: document.getElementById('add-fact-form'),
    factTextInput: document.getElementById('fact-text-input'),
    dbActionStatus: document.getElementById('db-action-status'),
    dbCountBadge: document.getElementById('db-count-badge'),
    dbSearch: document.getElementById('db-search'),
    dbFactsList: document.getElementById('db-facts-list'),
    
    // News Browser Tab
    gnewsSearchInput: document.getElementById('gnews-search-input'),
    btnGnewsSearch: document.getElementById('btn-gnews-search'),
    gnewsResultsPlaceholder: document.getElementById('gnews-results-placeholder'),
    gnewsResults: document.getElementById('gnews-results'),
    
    // History Tab
    historyRows: document.getElementById('history-rows'),
    historyEmpty: document.getElementById('history-empty'),
    btnClearHistory: document.getElementById('btn-clear-history')
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initTabs();
    initEventListeners();
    checkAPIStatus();
    loadHistory();
    fetchTrustedFacts();
    
    // Check connection status periodically (every 10s)
    setInterval(checkAPIStatus, 10000);
});

// Theme Logic
function initTheme() {
    const savedTheme = localStorage.getItem('fande-theme') || 'dark';
    if (savedTheme === 'light') {
        elements.body.classList.remove('dark-theme');
        elements.body.classList.add('light-theme');
    } else {
        elements.body.classList.add('dark-theme');
        elements.body.classList.remove('light-theme');
    }
}

function toggleTheme() {
    if (elements.body.classList.contains('dark-theme')) {
        elements.body.classList.remove('dark-theme');
        elements.body.classList.add('light-theme');
        localStorage.setItem('fande-theme', 'light');
    } else {
        elements.body.classList.remove('light-theme');
        elements.body.classList.add('dark-theme');
        localStorage.setItem('fande-theme', 'dark');
    }
}

// Tabs Logic
function initTabs() {
    elements.tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabId) {
    state.activeTab = tabId;
    
    elements.tabButtons.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    elements.tabContents.forEach(content => {
        if (content.id === tabId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// Event Listeners
function initEventListeners() {
    elements.themeToggle.addEventListener('click', toggleTheme);
    
    // Character counter
    elements.newsInput.addEventListener('input', () => {
        const chars = elements.newsInput.value.length;
        elements.charCount.textContent = chars;
    });

    // Sample selection
    elements.sampleSelector.addEventListener('change', (e) => {
        const sampleKey = e.target.value;
        if (sampleArticles[sampleKey]) {
            elements.newsInput.value = sampleArticles[sampleKey].text;
            elements.charCount.textContent = sampleArticles[sampleKey].text.length;
        }
    });

    // Claims range slider
    elements.claimsRange.addEventListener('input', (e) => {
        elements.claimsVal.textContent = e.target.value;
    });

    // Analyze news click
    elements.btnAnalyze.addEventListener('click', handleAnalysis);

    // Database search filter
    elements.dbSearch.addEventListener('input', (e) => {
        filterDatabaseFacts(e.target.value);
    });

    // Add trusted fact form submit
    elements.addFactForm.addEventListener('submit', handleAddFact);

    // News Browser Search
    elements.btnGnewsSearch.addEventListener('click', handleGnewsSearch);
    elements.gnewsSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleGnewsSearch();
    });

    // Clear history
    elements.btnClearHistory.addEventListener('click', clearHistory);
}

// API Health Check
async function checkAPIStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        if (res.ok) {
            updateConnectionStatus('online');
            state.isConnected = true;
        } else {
            updateConnectionStatus('connecting');
            state.isConnected = false;
        }
    } catch (err) {
        updateConnectionStatus('offline');
        state.isConnected = false;
    }
}

function updateConnectionStatus(status) {
    elements.connectionPill.className = 'status-pill';
    const dot = elements.connectionPill.querySelector('.status-dot');
    const label = elements.connectionPill.querySelector('.status-label');

    if (status === 'online') {
        elements.connectionPill.classList.add('status-online');
        label.textContent = 'Connected';
    } else if (status === 'connecting') {
        elements.connectionPill.classList.add('status-connecting');
        label.textContent = 'Server Warning';
    } else {
        elements.connectionPill.classList.add('status-offline');
        label.textContent = 'Offline';
    }
}

// Load and Display Trusted Facts DB
async function fetchTrustedFacts() {
    try {
        const res = await fetch(`${API_BASE}/api/trusted-facts`);
        if (res.ok) {
            const data = await res.json();
            state.trustedFacts = data.facts || [];
            renderDatabaseFacts();
        }
    } catch (err) {
        console.error("Failed to load database facts: ", err);
    }
}

function renderDatabaseFacts() {
    elements.dbCountBadge.textContent = `${state.trustedFacts.length} entries`;
    elements.dbFactsList.innerHTML = '';
    
    state.trustedFacts.forEach(fact => {
        const li = document.createElement('li');
        li.textContent = fact;
        elements.dbFactsList.appendChild(li);
    });
}

function filterDatabaseFacts(query) {
    const q = query.toLowerCase().trim();
    const items = elements.dbFactsList.querySelectorAll('li');
    
    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(q)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Add Fact to DB
async function handleAddFact(e) {
    e.preventDefault();
    const factText = elements.factTextInput.value.trim();
    if (factText.length < 10) return;

    // Show status indicator
    elements.dbActionStatus.style.display = 'block';
    elements.dbActionStatus.className = 'alert-box alert-success';
    elements.dbActionStatus.textContent = 'Saving to database...';

    const submitBtn = document.getElementById('btn-add-fact');
    submitBtn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/api/trusted-facts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ fact: factText })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            elements.dbActionStatus.className = 'alert-box alert-success';
            elements.dbActionStatus.textContent = 'Successfully saved and indexed.';
            elements.factTextInput.value = '';
            
            // Re-fetch facts to update UI lists
            await fetchTrustedFacts();
            
            // Hide alert after 4s
            setTimeout(() => {
                elements.dbActionStatus.style.display = 'none';
            }, 4000);
        } else {
            elements.dbActionStatus.className = 'alert-box alert-danger';
            elements.dbActionStatus.textContent = `Error: ${data.detail || 'Failed to add fact'}`;
        }
    } catch (err) {
        elements.dbActionStatus.className = 'alert-box alert-danger';
        elements.dbActionStatus.textContent = 'Failed to connect to the database server.';
    } finally {
        submitBtn.disabled = false;
    }
}

// GNews Explorer Search
async function handleGnewsSearch() {
    const query = elements.gnewsSearchInput.value.trim();
    if (!query) return;

    elements.gnewsResultsPlaceholder.style.display = 'none';
    elements.gnewsResults.style.display = 'none';
    
    // Temporary Loading Indicator
    const searchBtn = elements.btnGnewsSearch;
    const oldText = searchBtn.textContent;
    searchBtn.disabled = true;
    searchBtn.textContent = 'Searching...';

    try {
        const res = await fetch(`${API_BASE}/api/live-search?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        
        if (res.ok && data.results && data.results.length > 0) {
            renderGnewsArticles(data.results);
        } else {
            elements.gnewsResultsPlaceholder.style.display = 'block';
            elements.gnewsResultsPlaceholder.innerHTML = `<p>No recent news found for "${query}". Try another query.</p>`;
        }
    } catch (err) {
        elements.gnewsResultsPlaceholder.style.display = 'block';
        elements.gnewsResultsPlaceholder.innerHTML = `<p class="txt-fake">Failed to fetch news articles.</p>`;
    } finally {
        searchBtn.disabled = false;
        searchBtn.textContent = oldText;
    }
}

function renderGnewsArticles(articles) {
    elements.gnewsResults.innerHTML = '';
    elements.gnewsResults.style.display = 'grid';
    
    articles.forEach(article => {
        const card = document.createElement('div');
        card.className = 'glass-card news-card';
        
        const dateStr = article.published ? new Date(article.published).toLocaleDateString() : 'Recent';
        
        card.innerHTML = `
            <div class="news-card-content">
                <div class="news-card-header">
                    <span>${article.publisher}</span>
                    <span>${dateStr}</span>
                </div>
                <h3>${article.title}</h3>
                <p>${article.desc || 'No description preview available.'}</p>
            </div>
            <button class="btn-secondary load-analyze-btn">Check Story</button>
        `;
        
        // Button trigger
        card.querySelector('.load-analyze-btn').addEventListener('click', () => {
            // Combine Title & Description as news text
            const combinedText = `${article.title}\n\n${article.desc || ''}`;
            elements.newsInput.value = combinedText;
            elements.charCount.textContent = combinedText.length;
            elements.sampleSelector.value = ''; // Clear test dropdown selection
            
            // Switch tabs
            switchTab('tab-analyzer');
            
            // Smooth scroll to top of textarea
            elements.newsInput.scrollIntoView({ behavior: 'smooth' });
        });
        
        elements.gnewsResults.appendChild(card);
    });
}

// News Analyzer Core Process
async function handleAnalysis() {
    const text = elements.newsInput.value.trim();
    
    if (text.length < 50) {
        alert("Please enter a news article of at least 50 characters to perform analysis.");
        return;
    }

    const useLiveRag = elements.toggleLiveRag.checked;
    const nClaims = parseInt(elements.claimsRange.value);

    // Show Loading Overlay
    showLoader(true);
    updateLoaderStep('preprocess', 'active');
    
    try {
        // Step 1: Preprocessing UI Update (simulated delay for styling visual)
        await delay(400);
        updateLoaderStep('preprocess', 'completed');
        updateLoaderStep('claims', 'active');
        
        // Step 2: Claims UI Update (simulated delay)
        await delay(400);
        updateLoaderStep('claims', 'completed');
        updateLoaderStep('rag', 'active');
        
        // Call backend API (RAG stage holds here for HTTP latency)
        const responsePromise = fetch(`${API_BASE}/api/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                use_live_rag: useLiveRag,
                n_claims: nClaims
            })
        });
        
        const res = await responsePromise;
        const data = await res.json();
        
        if (!res.ok) {
            throw new Error(data.detail || "Analysis request failed");
        }
        
        // RAG finished
        updateLoaderStep('rag', 'completed');
        updateLoaderStep('predict', 'active');
        
        // Step 4: Model Prediction logic completes
        await delay(300);
        updateLoaderStep('predict', 'completed');
        await delay(150);

        // Success: Render and save
        state.currentAnalysis = data;
        renderAnalysisResults(data, text);
        saveAnalysisToHistory(data, text);
        
    } catch (err) {
        alert(`Verification Error: ${err.message}`);
        console.error(err);
    } finally {
        showLoader(false);
    }
}

// UI Loader control
function showLoader(show) {
    if (show) {
        elements.loadingOverlay.style.display = 'flex';
        // Reset all steps
        ['preprocess', 'claims', 'rag', 'predict'].forEach(s => {
            const el = document.getElementById(`step-${s}`);
            el.className = 'step-item';
        });
    } else {
        elements.loadingOverlay.style.display = 'none';
    }
}

function updateLoaderStep(step, status) {
    const el = document.getElementById(`step-${step}`);
    if (!el) return;

    if (status === 'active') {
        el.className = 'step-item active';
        elements.loaderStatus.textContent = getStepStatusText(step);
    } else if (status === 'completed') {
        el.className = 'step-item completed';
    }
}

// Humanized step labels
function getStepStatusText(step) {
    switch(step) {
        case 'preprocess': return 'Formatting article text...';
        case 'claims': return 'Identifying claims to verify...';
        case 'rag': return 'Searching news and database for evidence...';
        case 'predict': return 'Calculating credibility rating...';
        default: return 'Processing...';
    }
}

// Render Results Dashboard
function renderAnalysisResults(data, originalText) {
    // Hide placeholder, show results panel
    elements.resultsPlaceholder.style.display = 'none';
    elements.resultsPanel.style.display = 'flex';

    const score = data.credibility_score;
    
    // 1. Update Gauge score text
    elements.scoreText.textContent = `${score}%`;
    
    // Calculate SVG Stroke offset
    // Radius of track is 50, circumference is 2 * PI * r = 314.15
    const circumference = 314.15;
    const offset = circumference - (circumference * score / 100);
    elements.gaugeFill.style.strokeDashoffset = offset;
    
    // Change Gauge fill color theme depending on verdict
    const isReal = data.verdict === 'REAL';
    
    if (isReal) {
        elements.gaugeFill.style.stroke = 'var(--accent-emerald)';
        elements.verdictBadge.textContent = 'LIKELY RELIABLE';
        elements.verdictBadge.className = 'verdict-badge badge-real';
    } else {
        elements.gaugeFill.style.stroke = 'var(--accent-red)';
        elements.verdictBadge.textContent = 'LIKELY MISLEADING';
        elements.verdictBadge.className = 'verdict-badge badge-fake';
    }

    // 2. Probability Splits
    const realProb = Math.round((data.probabilities.REAL || 0.0) * 100);
    const fakeProb = Math.round((data.probabilities.FAKE || 0.0) * 100);

    elements.probRealVal.textContent = `${realProb}%`;
    elements.probRealFill.style.width = `${realProb}%`;
    elements.probFakeVal.textContent = `${fakeProb}%`;
    elements.probFakeFill.style.width = `${fakeProb}%`;

    // 3. Claims list rendering
    elements.claimsList.innerHTML = '';
    if (data.claims && data.claims.length > 0) {
        data.claims.forEach(claim => {
            const li = document.createElement('li');
            li.textContent = claim;
            elements.claimsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No claims could be extracted from the text.';
        elements.claimsList.appendChild(li);
    }

    // 4. Evidence Matches list rendering
    elements.elementsEvidenceList.innerHTML = '';
    if (data.evidence && data.evidence.length > 0) {
        data.evidence.forEach(item => {
            const card = document.createElement('div');
            card.className = 'evidence-card';
            
            const scorePercent = Math.round((item.similarity || 0.0) * 100);
            
            // Humanize evidence verdict tag
            let displayVerdict = "Unrelated";
            let tagClass = "tag-neutral";
            if (item.verdict === "Supports") {
                displayVerdict = "Supports claim";
                tagClass = "tag-supports";
            } else if (item.verdict === "Related") {
                displayVerdict = "Discusses claim";
                tagClass = "tag-related";
            }

            // Build link if URL available
            const linkHtml = item.url 
                ? `<a href="${item.url}" target="_blank" rel="noopener noreferrer" class="evidence-link">
                    Read Article
                   </a>` 
                : '';

            card.innerHTML = `
                <div class="evidence-header-row">
                    <div class="evidence-source">
                        <span class="evidence-title">${item.title}</span>
                        <span class="evidence-meta">${item.publisher} • ${item.published}</span>
                    </div>
                    <span class="evidence-tag ${tagClass}">${displayVerdict}</span>
                </div>
                <div class="evidence-snippet">"${item.desc || item.text}"</div>
                <div class="evidence-footer">
                    <div class="similarity-metric">
                        <span>Match strength:</span>
                        <div class="sim-track">
                            <div class="sim-fill" style="width: ${scorePercent}%; background-color: ${getSimilarityColor(item.similarity)}"></div>
                        </div>
                        <span style="color: ${getSimilarityColor(item.similarity)}">${scorePercent}%</span>
                    </div>
                    ${linkHtml}
                </div>
            `;
            elements.elementsEvidenceList.appendChild(card);
        });
    } else {
        elements.elementsEvidenceList.innerHTML = '<p class="setting-desc" style="text-align: center; padding: 1.5rem 0;">No matching fact corroboration could be mapped.</p>';
    }
}

function getSimilarityColor(score) {
    if (score > 0.55) return 'var(--accent-emerald)';
    if (score > 0.35) return 'var(--accent-blue)';
    return 'var(--text-muted)';
}

// Local Storage History Operations
function loadHistory() {
    try {
        const data = localStorage.getItem('fande-history');
        state.history = data ? JSON.parse(data) : [];
        renderHistory();
    } catch(err) {
        state.history = [];
    }
}

function renderHistory() {
    elements.historyRows.innerHTML = '';
    
    if (state.history.length === 0) {
        elements.historyEmpty.style.display = 'block';
        return;
    }
    
    elements.historyEmpty.style.display = 'none';

    state.history.forEach((run, idx) => {
        const tr = document.createElement('tr');
        const date = new Date(run.timestamp).toLocaleDateString();
        const snippet = run.text.substring(0, 80) + (run.text.length > 80 ? '...' : '');
        const scoreClass = run.score >= 50 ? 'txt-real' : 'txt-fake';
        
        // Translate visual verdict string
        const displayVerdict = run.verdict === 'REAL' ? 'RELIABLE' : 'MISLEADING';

        tr.innerHTML = `
            <td>${date}</td>
            <td class="history-verdict ${run.verdict === 'REAL' ? 'txt-real' : 'txt-fake'}">${displayVerdict}</td>
            <td class="${scoreClass}" style="font-weight: 700;">${run.score}%</td>
            <td class="history-snippet">${escapeHtml(snippet)}</td>
            <td><span class="badge" style="text-transform: capitalize;">${run.mode}</span></td>
            <td>
                <button class="btn-secondary view-hist-btn" data-index="${idx}" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;">Recall</button>
                <button class="btn-secondary del-hist-btn" data-index="${idx}" style="padding: 0.25rem 0.5rem; font-size: 0.75rem; color: var(--accent-red); border-color: rgba(239,68,68,0.1);">Del</button>
            </td>
        `;
        
        // Click action for Load Recall
        tr.querySelector('.view-hist-btn').addEventListener('click', () => {
            const item = state.history[idx];
            elements.newsInput.value = item.text;
            elements.charCount.textContent = item.text.length;
            
            // Switch tabs
            switchTab('tab-analyzer');
            
            // Instant render results from history (no API run required!)
            state.currentAnalysis = item.results;
            renderAnalysisResults(item.results, item.text);
        });

        // Click action for Delete
        tr.querySelector('.del-hist-btn').addEventListener('click', () => {
            deleteHistoryItem(idx);
        });
        
        elements.historyRows.appendChild(tr);
    });
}

function saveAnalysisToHistory(results, text) {
    const historyItem = {
        timestamp: new Date().toISOString(),
        text: text,
        verdict: results.verdict,
        score: results.credibility_score,
        mode: results.rag_mode,
        results: results
    };
    
    // Add to top of list
    state.history.unshift(historyItem);
    
    // Cap at 20 items
    if (state.history.length > 20) {
        state.history.pop();
    }
    
    localStorage.setItem('fande-history', JSON.stringify(state.history));
    renderHistory();
}

function deleteHistoryItem(index) {
    state.history.splice(index, 1);
    localStorage.setItem('fande-history', JSON.stringify(state.history));
    renderHistory();
}

function clearHistory() {
    if (confirm("Are you sure you want to delete all past verification runs?")) {
        state.history = [];
        localStorage.removeItem('fande-history');
        renderHistory();
    }
}

// Helpers
function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Escapes special HTML tags to prevent cross site script injections in lists
function escapeHtml(text) {
    return text
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}
