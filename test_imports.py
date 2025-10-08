# test_complete_imports.py
try:
    # Core data science
    import numpy as np
    import pandas as pd
    import sklearn
    print("✅ Core data science packages")
    
    # Visualization
    import seaborn as sns
    import matplotlib.pyplot as plt
    print("✅ Visualization packages")
    
    # Web framework
    import flask
    print("✅ Web framework")
    
    # AI/ML
    from sentence_transformers import SentenceTransformer
    import torch
    from transformers import pipeline
    print("✅ AI/ML packages")
    
    # Database & LangChain
    import chromadb
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings
    print("✅ Database & LangChain packages")
    
    print("\n🎉 ALL PACKAGES IMPORT SUCCESSFUL!")
    print(f"NumPy: {np.__version__}")
    print(f"Pandas: {pd.__version__}")
    print(f"Flask: {flask.__version__}")
    print(f"PyTorch: {torch.__version__}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")