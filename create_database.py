import pandas as pd
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

print("🔄 Creating enhanced vector database...")

# Step 1: Load your books data
books = pd.read_csv("books_cleaned.csv")
print(f"✅ Loaded {len(books)} books from CSV")

# Step 2: Create documents with ALL metadata
documents = []
for i, row in books.iterrows():
    if pd.notna(row.get('tagged_description')) and str(row['tagged_description']).strip():
        # Create document with all available metadata
        metadata = {
            "book_index": str(i),
            "title": str(row.get('title', '')),
            "authors": str(row.get('authors', '')),
            "categories": str(row.get('categories', '')),
            "published_year": str(row.get('published_year', '')),
            "average_rating": float(row.get('average_rating', 0)),
            "num_pages": float(row.get('num_pages', 0)),
            "ratings_count": float(row.get('ratings_count', 0)),
            "isbn": str(row.get('isbn13', ''))
        }

        documents.append(Document(
            page_content=str(row['tagged_description']).strip(),
            metadata=metadata
        ))

print(f"📚 Created {len(documents)} documents with complete metadata")

# Step 3: Create NEW vector database with full metadata
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db_books = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./book_vector_db_enhanced"
)

print("✅ Enhanced vector database created at ./book_vector_db_enhanced/")