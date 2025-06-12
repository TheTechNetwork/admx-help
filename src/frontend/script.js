let allPolicies = [];
const searchInput = document.getElementById('search-input');
const resultsContainer = document.getElementById('results-container');
const loadingMessage = document.getElementById('loading-message');
const noResultsMessage = document.getElementById('no-results');

async function loadPolicies() {
    try {
        // Add a cache-busting parameter to ensure fresh data after deployment
        const timestamp = new Date().getTime();
        const response = await fetch(`data/policies.json?t=${timestamp}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allPolicies = await response.json();
        loadingMessage.style.display = 'none';
        displayPolicies(allPolicies); // Display all initially or prompt for search
    } catch (error) {
        console.error('Error loading policies:', error);
        loadingMessage.textContent = 'Error loading policies. Please check the console for details.';
    }
}

function displayPolicies(policies) {
    resultsContainer.innerHTML = ''; // Clear previous results
    if (policies.length === 0) {
        noResultsMessage.style.display = 'block';
        return;
    }
    noResultsMessage.style.display = 'none';

    policies.forEach(policy => {
        const card = document.createElement('div');
        card.className = 'policy-card';
        card.innerHTML = `
            <h3>${policy.name}</h3>
            <div class="path">${policy.category_path}</div>
            <p>${policy.description}</p>
            ${policy.registry_key ? `<p><strong>Registry Key:</strong> <code>${policy.registry_key}</code></p>` : ''}
            ${policy.registry_value_name ? `<p><strong>Registry Value:</strong> <code>${policy.registry_value_name}</code></p>` : ''}
            ${policy.registry_value !== undefined ? `<p><strong>Value:</strong> <code>${policy.registry_value}</code></p>` : ''}
            ${policy.supported_on ? `<p><strong>Supported On:</strong> ${policy.supported_on}</p>` : ''}
            <p><small>Source ADMX: ${policy.admx_file}</small></p>
        `;
        resultsContainer.appendChild(card);
    });
}

function searchPolicies() {
    const query = searchInput.value.toLowerCase().trim();
    if (query.length < 2 && query.length !== 0) { // Require at least 2 chars, unless empty
        resultsContainer.innerHTML = '<p>Please enter at least 2 characters to search.</p>';
        noResultsMessage.style.display = 'none';
        return;
    }

    const filteredPolicies = allPolicies.filter(policy =>
        (policy.name && policy.name.toLowerCase().includes(query)) ||
        (policy.description && policy.description.toLowerCase().includes(query)) ||
        (policy.registry_key && policy.registry_key.toLowerCase().includes(query)) ||
        (policy.registry_value_name && policy.registry_value_name.toLowerCase().includes(query))
    );
    displayPolicies(filteredPolicies);
}

// Debounce search input to avoid too many calls
let searchTimeout;
searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(searchPolicies, 300); // Wait 300ms after typing stops
});

// Initial load
loadPolicies();
