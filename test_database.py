from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def test_database():
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        db_books = Chroma(
            persist_directory="./book_vector_db_enhanced",
            embedding_function=embeddings
        )
        
        # Test a search
        results = db_books.similarity_search("children's book about nature", k=3)
        print(f"✅ Database works! Found {len(results)} results")
        
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.metadata.get('title', 'N/A')}")
            print(f"   Author: {doc.metadata.get('authors', 'N/A')}")
            print(f"   Rating: {doc.metadata.get('average_rating', 'N/A')}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_database()