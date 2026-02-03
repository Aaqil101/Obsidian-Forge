let allMedia = [];
let filteredMedia = [];
let currentTab = 'all';

// Load media on page load
async function loadMedia() {
    try {
        const response = await fetch('/api/media');
        const data = await response.json();

        // Flatten data structure
        allMedia = [];
        for (const [type, items] of Object.entries(data)) {
            items.forEach(item => {
                // Use the media_type from the item, or fall back to the key
                if (!item.media_type) {
                    item.media_type = type;
                }
                allMedia.push(item);
            });
        }

        console.log('Loaded media:', allMedia.length, 'items');
        console.log('Sample item:', allMedia[0]);

        filteredMedia = allMedia;
        updateStats();
        renderMedia();
        document.getElementById('loadingState').style.display = 'none';
    } catch (error) {
        console.error('Error loading media:', error);
        document.getElementById('loadingState').innerHTML = '<p>Error loading media library</p>';
    }
}

// Handle tab switching
function switchTab(tabType) {
    console.log('Switching to tab:', tabType);
    currentTab = tabType;

    // Update active tab styling
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-type="${tabType}"]`).classList.add('active');

    // Apply filters with new tab
    applyFilters();
}

function renderMedia() {
    const grid = document.getElementById('mediaGrid');
    const emptyState = document.getElementById('emptyState');

    grid.innerHTML = '';

    if (filteredMedia.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    grid.style.display = 'grid';
    emptyState.style.display = 'none';

    filteredMedia.forEach(item => {
        const card = createMediaCard(item);
        grid.appendChild(card);
    });
}

function createMediaCard(item) {
    const card = document.createElement('div');
    card.className = `media-card ${item.media_type}`;

    const coverUrl = item.cover_image || '';
    const typeLabel = formatType(item.media_type);

    // Get external URL based on media type
    const externalUrl = item.metadata?.youtube_url || item.metadata?.book_url || null;

    card.innerHTML = `
        ${externalUrl ? `<img src="/static/icons/external_link.svg" class="external-link-icon" data-url="${externalUrl}" title="Open external link">` : ''}
        <img src="${coverUrl || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg"%3E%3C/svg%3E'}"
             class="media-card-cover"
             onerror="this.style.background='linear-gradient(135deg, #414868 0%, #2f3241 100%)'">
        <div class="media-card-body">
            <div class="media-card-type">${typeLabel}</div>
            <div class="media-card-title">${escapeHtml(item.title)}</div>
            <div class="media-card-meta">
                <span>${item.year || 'N/A'}</span>
                ${item.rating ? `<span class="media-card-rating">⭐ ${item.rating.toFixed(1)}</span>` : ''}
            </div>
        </div>
    `;

    // Add click handler for external link icon
    const externalLinkIcon = card.querySelector('.external-link-icon');
    if (externalLinkIcon) {
        externalLinkIcon.onclick = (e) => {
            e.stopPropagation();
            window.open(externalLinkIcon.dataset.url, '_blank');
        };
    }

    card.onclick = () => openInObsidian(item);

    return card;
}

function formatType(type) {
    const map = {
        'books': 'Book',
        'movies': 'Movie',
        'tv_shows': 'TV Show',
        'youtube': 'YouTube',
        'documentaries': 'Documentary'
    };
    return map[type] || type;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function openInObsidian(item) {
    try {
        const response = await fetch(`/api/open/${item.media_type}/${item.id}`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.uri) {
            window.location.href = data.uri;
        }
    } catch (error) {
        console.error('Error opening in Obsidian:', error);
    }
}

function updateStats() {
    document.getElementById('showingCount').textContent = filteredMedia.length;
    document.getElementById('totalCount').textContent = allMedia.length;
}

function applyFilters() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const sortBy = document.getElementById('sortBy').value;

    console.log('Applying filters - currentTab:', currentTab, 'searchTerm:', searchTerm);

    filteredMedia = allMedia.filter(item => {
        const matchesSearch = !searchTerm ||
            item.title.toLowerCase().includes(searchTerm) ||
            (item.metadata && item.metadata.authors && item.metadata.authors.toLowerCase().includes(searchTerm));

        const matchesType = currentTab === 'all' || item.media_type === currentTab;

        return matchesSearch && matchesType;
    });

    console.log('Filtered from', allMedia.length, 'to', filteredMedia.length, 'items');

    // Sort
    if (sortBy === 'title') {
        filteredMedia.sort((a, b) => {
            const titleA = String(a.title || '');
            const titleB = String(b.title || '');
            return titleA.localeCompare(titleB);
        });
    } else if (sortBy === 'rating') {
        filteredMedia.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    } else if (sortBy === 'year') {
        filteredMedia.sort((a, b) => (b.year || 0) - (a.year || 0));
    }

    updateStats();
    renderMedia();
}

// Initialize when DOM is ready
function init() {
    // Event listeners
    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('sortBy').addEventListener('change', applyFilters);

    // Tab click handlers
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            switchTab(tab.dataset.type);
        });
    });

    // Load media first, then apply URL filters
    loadMedia().then(() => {
        // Check if type filter is specified in URL
        const urlParams = new URLSearchParams(window.location.search);
        const typeParam = urlParams.get('type');
        if (typeParam) {
            switchTab(typeParam);
        }
    });
}

// Run init when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
