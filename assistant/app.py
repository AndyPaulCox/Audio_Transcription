# This is assistant/app.py
import faiss
from flask import Flask, request, render_template,session
from .assistant_backend import (perform_faiss_search, concatenate_context_docs, 
                                gpt_query_processing, gpt_generate_response, 
                                post_process_gpt_response, load_documents) 

# Load or initialize your index and documents
faiss_index = faiss.read_index('/Users/apcox/AWS_S3/library/faiss_index/faiss_index.index')
docs = load_documents('/Users/apcox/AWS_S3/library/temp/')

app = Flask(__name__)
app.secret_key = '1964'  # Set a secret key for session management

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []  # Initialize chat history
    if request.method == 'POST':
        query = request.form['query']
        faiss_search_results = perform_faiss_search(query=query, faiss_index=faiss_index, documents=docs, k=5)
        conc_results = concatenate_context_docs(faiss_search_results)
        # Retrieve chat_history from the session
        chat_history = session.get('chat_history', [])
        enhanced_query = gpt_query_processing(query, conc_results, chat_history)
        raw_results = gpt_generate_response(enhanced_query,chat_history,conc_results)
        PP_response = post_process_gpt_response(raw_results)
        # Update the chat history in the session if needed
        session['chat_history'] = PP_response  # Assuming you update chat history somewhere
        return render_template('index.html', results=[PP_response])
    return render_template('index.html', results=[])
    
    
    

