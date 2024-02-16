# initialize.py
import os
from assistant.assistant_backend import tokenize_and_save_chunks,embed_documents,create_faiss_index,save_faiss_index,load_documents
from pathlib import Path

def main():
    # cunking files for processing:
    output_directory = '/Users/apcox/AWS_S3/library/temp'  # Replace with your desired output directory
    chunk_size = 150  # Set your desired chunk size here
    document_folder = '/Users/apcox/AWS_S3/library/summaries'  # Update this to your document folder
    

    # Call the function
    tokenize_and_save_chunks(document_folder, output_directory, chunk_size)
    
    documents = load_documents(document_folder)

    print("Embedding documents...")
    document_embeddings = embed_documents(documents)

    print("Creating FAISS index...")
    faiss_index = create_faiss_index(document_embeddings)

    index_path = "/Users/apcox/AWS_S3/library/faiss_index/faiss_index.index"  # Update this to where you want to save the FAISS index
    print(f"Saving FAISS index to {index_path}...")
    save_faiss_index(faiss_index, index_path)

    print("Initialization complete.")

if __name__ == '__main__':
    main()
    
    
    
    
    


