// Load suggestions when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Search state management
let searchState = {
    currentQuery: '',
    isLoading: false,
    hasSearched: false
};

// Initialize the application
function initializeApp() {
    loadSuggestions();
    
    // Add form submission handler
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            searchBooks();
        });
    }
    
    // Add click listeners to suggestion tags
    document.addEventListener('click', function(e) {
        if (e.target && e.target.classList.contains('suggestion-tag')) {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = e.target.textContent;
                searchBooks();
            }
        }
    });
    
    // Add Enter key support
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchBooks();
            }
        });
    }
}

// Load search suggestions
async function loadSuggestions() {
    try {
        const response = await fetch('/suggestions');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update suggestion tags
        const container = document.getElementById('suggestionTags');
        if (container) {
            container.innerHTML = '';
            
            if (data.suggestions && Array.isArray(data.suggestions)) {
                data.suggestions.forEach(suggestion => {
                    const tag = document.createElement('div');
                    tag.className = 'suggestion-tag';
                    tag.textContent = suggestion;
                    container.appendChild(tag);
                });
            }
        }
    } catch (error) {
        console.error('Error loading suggestions:', error);
    }
}

// Main search function
async function searchBooks() {
    // Prevent multiple simultaneous searches
    if (searchState.isLoading) {
        return;
    }
    
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) {
        console.error('Search input not found');
        return;
    }
    
    const query = searchInput.value.trim();
    const category = document.getElementById('categoryFilter')?.value || '';
    const minRating = document.getElementById('ratingFilter')?.value || '0';
    
    // Validate inputs
    if (!query) {
        showError('Please enter a search query');
        return;
    }

    // Update search state
    searchState.currentQuery = query;
    searchState.isLoading = true;
    searchState.hasSearched = true;

    // Show loading, hide previous results and errors
    showElement('loading');
    hideElement('results');
    hideElement('error');

    try {
        console.log('Starting search for:', query);
        
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                category: category,
                min_rating: minRating ? parseFloat(minRating) : 0
            })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Search successful, results count:', data.count);
        
        if (!data || typeof data !== 'object') {
            throw new Error('Invalid response format from server');
        }
        
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        showError('Search failed. Please try again.');
        
        // Clear results on error
        const resultsContainer = document.getElementById('booksList');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="no-results"><p>Error loading results. Please try again.</p></div>';
        }
    } finally {
        searchState.isLoading = false;
        hideElement('loading');
    }
}

// Display search results
function displayResults(data) {
    console.log('Displaying results:', data);
    
    const resultsContainer = document.getElementById('booksList');
    const resultsTitle = document.getElementById('resultsTitle');
    const resultsCount = document.getElementById('resultsCount');
    const resultsSection = document.getElementById('results');
    
    // Validate DOM elements
    if (!resultsContainer || !resultsTitle || !resultsCount || !resultsSection) {
        console.error('Required DOM elements not found');
        showError('Page layout error. Please refresh the page.');
        return;
    }
    
    // Update titles and counts
    resultsTitle.textContent = data.query || 'Unknown';
    resultsCount.textContent = `${data.count || 0} book${(data.count || 0) !== 1 ? 's' : ''} found`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (!data.count || data.count === 0 || !data.results || data.results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <p>No books found matching your criteria. Try a different search or adjust your filters.</p>
            </div>
        `;
    } else {
        console.log('Creating book cards for', data.results.length, 'books');
        data.results.forEach((book, index) => {
            try {
                const bookCard = createBookCard(book);
                if (bookCard) {
                    resultsContainer.appendChild(bookCard);
                }
            } catch (cardError) {
                console.error('Error creating book card for index', index, cardError);
            }
        });
    }
    
    // Ensure results section is properly shown
    showElement('results');
    console.log('Results displayed successfully');
}

// Create book card HTML with fixed height and scrollable description
function createBookCard(book) {
    if (!book) {
        console.error('No book data provided to createBookCard');
        return document.createElement('div');
    }
    
    const card = document.createElement('div');
    card.className = 'book-card';
    
    // Safely handle book properties with better formatting
    const title = book.title || 'Unknown Title';
    const authors = book.authors || 'Unknown Author';
    const categories = book.categories || 'Unknown Category';
    const year = book.published_year || 'Unknown';
    const pages = book.num_pages || 'Unknown';
    
    // Format rating display
    let ratingHtml = '';
    if (book.average_rating && book.average_rating > 0) {
        ratingHtml = `<span class="meta-item rating">⭐ ${book.average_rating.toFixed(1)}</span>`;
    }
    
    // Clean and format description - show full description since we have scrolling
    let cleanDescription = book.description || 'No description available.';
    
    // Remove any extra quotes or formatting issues
    cleanDescription = cleanDescription
        .replace(/^['"]|['"]$/g, '') // Remove surrounding quotes
        .replace(/\s+/g, ' ') // Normalize whitespace
        .trim();
    
    card.innerHTML = `
        <h3 class="book-title">${escapeHtml(title)}</h3>
        <p class="book-author">by ${escapeHtml(authors)}</p>
        <div class="book-meta">
            ${ratingHtml}
            <span class="meta-item">📂 ${escapeHtml(categories)}</span>
            <span class="meta-item">📅 ${escapeHtml(year.toString())}</span>
            <span class="meta-item">📄 ${escapeHtml(pages.toString())} pages</span>
        </div>
        <div class="book-description-container">
            <p class="book-description">${escapeHtml(cleanDescription)}</p>
            <div class="scroll-indicator"></div>
        </div>
    `;
    
    return card;
}

// Utility functions
function showElement(id) {
    const element = document.getElementById(id);
    if (element) {
        element.classList.remove('hidden');
        element.style.display = '';
    }
}

function hideElement(id) {
    const element = document.getElementById(id);
    if (element) {
        element.classList.add('hidden');
    }
}

function showError(message) {
    const errorElement = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorElement && errorMessage) {
        errorMessage.textContent = message;
        showElement('error');
    }
}

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    
    if (typeof unsafe !== 'string') {
        unsafe = String(unsafe);
    }
    
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}