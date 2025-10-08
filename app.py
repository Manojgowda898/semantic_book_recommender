from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'book-recommender-secret-key-2024'

# Global variables
model = None
books_df = None
vector_db = None

def load_model_and_data():
    """Load the embedding model, book data, and vector database"""
    global model, books_df, vector_db
    
    try:
        logger.info("Loading embedding model...")
        model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        logger.info("Loading book data...")
        books_df = pd.read_csv('books_cleaned.csv')
        
        # Clean and prepare data
        books_df = books_df.fillna({
            'categories': 'Unknown',
            'average_rating': 0,
            'num_pages': 0,
            'published_year': 0,
            'ratings_count': 0
        })
        
        logger.info("Loading vector database...")
        if os.path.exists('book_vector_db_enhanced'):
            vector_db = Chroma(
                persist_directory='book_vector_db_enhanced',
                embedding_function=model
            )
            logger.info("Enhanced vector database loaded successfully")
        else:
            logger.warning("No vector database found, using CSV fallback")
            vector_db = None
        
        logger.info(f"Successfully loaded {len(books_df)} books")
        
    except Exception as e:
        logger.error(f"Error loading model or data: {e}")
        # Create a simple fallback
        books_df = pd.DataFrame()

def clean_description(description):
    """Clean description by removing ISBN prefix and formatting issues"""
    if not description:
        return "No description available."
    
    description = str(description)
    
    # Remove ISBN prefix if present
    if description.startswith('978') and len(description) > 13:
        if description[13] == ' ':
            description = description[14:]
        else:
            description = description[13:]
    
    # Remove surrounding quotes and normalize whitespace
    description = description.strip().strip('"').strip("'")
    description = ' '.join(description.split())
    
    return description

@app.route('/')
def index():
    """Home page with search"""
    try:
        return render_template('index.html', total_books=len(books_df) if books_df is not None else 0)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', total_books=0)

@app.route('/search', methods=['POST'])
def search_books():
    """Search for books using semantic similarity"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        category_filter = data.get('category', '')
        min_rating = float(data.get('min_rating', 0))
        
        logger.info(f"Search request: query='{query}', category='{category_filter}', min_rating={min_rating}")
        
        if not query:
            return jsonify({'error': 'Please enter a search query'}), 400
        
        # Perform search
        results = perform_semantic_search(query, category_filter, min_rating)
        
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed. Please try again.'}), 500

@app.route('/suggestions')
def get_suggestions():
    """Get search suggestions"""
    suggestions = [
        "children's book about nature and animals",
        "science fiction space adventure", 
        "historical fiction romance",
        "mystery thriller suspense",
        "business leadership strategy",
        "self improvement motivation",
        "cooking recipes food",
        "fantasy magic dragons",
        "biography historical figure",
        "science environment ecology"
    ]
    return jsonify({'suggestions': suggestions})

def perform_semantic_search(query, category_filter='', min_rating=0, limit=10):
    """Perform semantic search using vector database"""
    try:
        if vector_db is None:
            return perform_text_search(query, category_filter, min_rating, limit)
        
        # Use vector database
        search_results = vector_db.similarity_search(query, k=limit)
        
        # Convert to our format
        results = []
        for doc in search_results:
            book_data = {
                'id': doc.metadata.get('book_index', ''),
                'title': doc.metadata.get('title', 'Unknown Title'),
                'authors': doc.metadata.get('authors', 'Unknown Author'),
                'categories': doc.metadata.get('categories', 'Unknown Category'),
                'published_year': doc.metadata.get('published_year', 'Unknown'),
                'average_rating': float(doc.metadata.get('average_rating', 0)),
                'num_pages': doc.metadata.get('num_pages', 'Unknown'),
                'description': clean_description(doc.page_content),
                'thumbnail': doc.metadata.get('thumbnail', '')
            }
            # Apply filters
            if category_filter and book_data['categories'] != category_filter:
                continue
            if min_rating > 0 and book_data['average_rating'] < min_rating:
                continue
            results.append(book_data)
        
        return results[:limit]
            
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return perform_text_search(query, category_filter, min_rating, limit)

def perform_text_search(query, category_filter='', min_rating=0, limit=10):
    """Fallback text-based search"""
    try:
        if books_df is None or len(books_df) == 0:
            return []
        
        filtered_books = books_df.copy()
        
        # Apply filters
        if category_filter:
            filtered_books = filtered_books[filtered_books['categories'] == category_filter]
        
        if min_rating > 0:
            filtered_books = filtered_books[filtered_books['average_rating'] >= min_rating]
        
        # Simple text search
        query_lower = query.lower()
        mask = (
            filtered_books['description'].str.lower().str.contains(query_lower, na=False) |
            filtered_books['title'].str.lower().str.contains(query_lower, na=False) |
            filtered_books['authors'].str.lower().str.contains(query_lower, na=False)
        )
        
        filtered_books = filtered_books[mask]
        
        return format_books_for_display(filtered_books.head(limit))
            
    except Exception as e:
        logger.error(f"Text search error: {e}")
        return []

def format_books_for_display(books_df_subset):
    """Format books for frontend display"""
    books = []
    for _, book in books_df_subset.iterrows():
        books.append(format_single_book(book))
    return books

def format_single_book(book):
    """Format a single book for display"""
    try:
        description = clean_description(book.get('description', ''))
        
        # Format year as integer if possible
        published_year = book.get('published_year', 'Unknown')
        if published_year and published_year != 'Unknown':
            try:
                published_year = str(int(float(published_year)))
            except:
                published_year = str(published_year)
        
        return {
            'id': str(book.get('isbn13', '')),
            'title': str(book.get('title', 'Unknown Title')),
            'authors': str(book.get('authors', 'Unknown Author')),
            'categories': str(book.get('categories', 'Unknown Category')),
            'published_year': published_year,
            'average_rating': float(book.get('average_rating', 0)),
            'num_pages': str(book.get('num_pages', 'Unknown')),
            'description': description,
            'thumbnail': str(book.get('thumbnail', ''))
        }
    except Exception as e:
        logger.error(f"Error formatting book: {e}")
        return {
            'id': 'unknown',
            'title': 'Unknown Title',
            'authors': 'Unknown Author',
            'categories': 'Unknown Category',
            'published_year': 'Unknown',
            'average_rating': 0,
            'num_pages': 'Unknown',
            'description': 'No description available.',
            'thumbnail': ''
        }

# Initialize when app starts
print("🚀 Starting Book Recommender Website...")
print("📚 Loading model and data...")
load_model_and_data()
print("✅ Setup complete! Flask server is ready.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)