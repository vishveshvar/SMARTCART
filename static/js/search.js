/**
 * SmartCart - Search Suggestions & Autocomplete
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('scMainSearchInput');
    const dropdown = document.getElementById('scSearchSuggestions');
    let debounceTimer;

    if (searchInput && dropdown) {
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();

            if (query.length < 2) {
                dropdown.style.display = 'none';
                dropdown.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(async () => {
                try {
                    const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
                    const items = await response.json();

                    if (items.length > 0) {
                        dropdown.innerHTML = items.map(item => `
                            <a href="/product/${item.id}" class="sc-search-item">
                                <i class="bi bi-search text-muted"></i>
                                <div>
                                    <div class="fw-semibold text-truncate" style="max-width: 320px;">${item.name}</div>
                                    <div class="small text-muted">${item.brand || item.category} • ₹${item.price}</div>
                                </div>
                            </a>
                        `).join('');
                        dropdown.style.display = 'block';
                    } else {
                        dropdown.style.display = 'none';
                    }
                } catch (e) {
                    console.error('Autocomplete error:', e);
                }
            }, 250);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }
});
