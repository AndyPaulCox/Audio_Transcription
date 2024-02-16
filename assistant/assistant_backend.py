import os
import faiss
from openai import OpenAI

client = OpenAI()
import numpy as np
from openai import OpenAI

client = OpenAI()
from openai import OpenAI
from pathlib import Path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load your OpenAI API key from the environment

def embed_documents(docs):
    """
    Convert documents to embeddings.
    """
    # Example: Using OpenAI's embedding function (adjust model as needed)
    embeddings = [client.embeddings.create(input=doc,model="text-embedding-3-small").data[0].embedding for doc in docs]
    return np.array(embeddings)

def create_faiss_index(embeddings):
    """
    Create and return a FAISS index from embeddings.
    """
    d = embeddings.shape[1]  # Dimension of embeddings
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    return index

def gpt_query_processing(query, context_documents,chat_history):
    """
    Enhance the query using GPT-4, incorporating relevant context for a more sophisticated response.
    """
    # Prepare the context by concatenating relevant documents or summaries
    context = "\n".join(context_documents[:3])  # Example: using top 3 relevant documents

    # Adjust the prompt to include both the context and the user's query
    prompt = f"Given the following information: {context}\nAnswer the question: {query}"

    # Make the API call with adjusted parameters for a more detailed response
    ai_response = client.chat.completions.create(model="gpt-4",messages=[{"role": "system", "content": prompt},],max_tokens=250,temperature=0.5,stop=["\n", "END"])
    # Return the refined or generated answer
    return ai_response.choices[0].message.content.strip()

def search_documents(query, faiss_index, docs, k=5):
    """
    Convert query to embedding, process with GPT, search FAISS index, and return results.
    """
    processed_query = gpt_query_processing(query)
    print(f"Processed query is {processed_query}")
    query_embedding = embed_documents([processed_query])[0]
    return search_index(query_embedding, faiss_index, docs, k)
    
def search_index(query_embedding, faiss_index, docs, k=5):
    """
    Search the FAISS index for the query embedding and return top k results.
    Essentailly thjis returns the text of the k=5 closts matching documents in order
    """
    D, I = faiss_index.search(np.array([query_embedding]), k)
    return [docs[i] for i in I[0]]

def save_faiss_index(index, filepath):
    """
    Save the FAISS index to a specified file.
    """
    faiss.write_index(index, filepath)
    
def load_documents(document_folder):
    """
    Load documents from a specified folder.
    Returns a list of document texts.
    """
    documents = []
    for file_path in Path(document_folder).glob('*.txt'):
        with open(file_path, encoding='utf-8') as file:
            documents.append(file.read())
    return documents

def tokenize_and_save_chunks(directory_path, output_dir, chunk_size):
    """
    Processes each text file in a directory, breaking it into chunks of up to chunk_size tokens,
    and saves each chunk into a new file in the specified directory.
    
    Parameters:
    - directory_path: Path to the directory containing text files.
    - output_dir: Directory where chunked files will be saved.
    - chunk_size: Maximum number of tokens per chunk.
    """
    # Ensure the output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        input_path = os.path.join(directory_path, filename)
        # Check if it's a file and not a directory
        if os.path.isfile(input_path):
            # Read the input file
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Split text into words
            words = text.split()
            
            # Calculate the number of chunks
            num_chunks = len(words) // chunk_size + (1 if len(words) % chunk_size > 0 else 0)
            
            # Process and save each chunk
            for i in range(num_chunks):
                chunk_words = words[i*chunk_size:(i+1)*chunk_size]
                chunk_text = ' '.join(chunk_words)
                chunk_filename = f"{Path(input_path).stem}_chunk_{i+1}{Path(input_path).suffix}"
                chunk_path = os.path.join(output_dir, chunk_filename)
                
                with open(chunk_path, 'w', encoding='utf-8') as chunk_file:
                    chunk_file.write(chunk_text)
                print(f"Saved chunk {i+1} to {chunk_path}")


def perform_faiss_search(query, faiss_index, documents, k=5):
    """Perform a FAISS search to find relevant documents based on the query."""
    # Convert query to embedding
    query_embedding = embed_documents([query])[0]
    _, indices = faiss_index.search(np.array([query_embedding]), k) #There was a _,  at the start of this line 
    return [documents[i] for i in indices[0]]

def concatenate_context_docs(docs):
    """Concatenate texts or summaries of top documents into a single string."""
    return ' '.join(docs)

def gpt_generate_response(query, chat_history, document_context):
    """Use GPT-4 to generate a response based on the chat history, the latest query, and document context."""
    if not isinstance(chat_history, list):
        chat_history = []  # Fallback in case chat_history is not a list
    
    # Prepare document context for inclusion
    context_message = {
        'role': 'system',  # Use 'system' role for non-interaction messages like context
        'content': document_context  # This should be a summary or relevant excerpts from your documents
    }

    # Append the document context as the first message if it's not empty
    if document_context.strip():  # Ensure there's actual content to add
        chat_history = [context_message] + chat_history

    # Append the latest query to the chat history
    chat_history.append({'role': 'user', 'content': query})

    # Prepare the messages for the API call
    messages = chat_history  # Assuming chat_history is already in the correct format

    # Make the API call using the chat completion endpoint
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    # Extract the content of the AI's response
    ai_response_content = response.choices[0].message.content.strip()

    # Optionally, append the AI's response to the chat history here if you want to maintain it for the next call
    chat_history.append({'role': 'assistant', 'content': ai_response_content})

    return ai_response_content

def post_process_gpt_response(response):
    """Refine the GPT-4 response for clarity, conciseness, and relevance."""
    # This is a placeholder for any specific post-processing you might want to do
    return response

def embed_documents(documents):
    """Placeholder function for document embedding - to be defined based on your embedding method."""
    return np.array([[0.0]])  # Placeholder return
    
def update_chat_history(user_message, ai_response, max_history_length=25):
    # Append user message and AI response to the chat history
    if 'chat_history' not in session:
        session['chat_history'] = []

    session['chat_history'].append({'role': 'user', 'content': user_message})
    session['chat_history'].append({'role': 'assistant', 'content': ai_response})

    # Ensure chat history does not exceed max_history_length
    if len(session['chat_history']) > max_history_length:
        # Remove oldest entries to maintain the size limit
        over_limit = len(session['chat_history']) - max_history_length
        session['chat_history'] = session['chat_history'][over_limit:]

    session.modified = True  # Mark session as modified to ensure changes are saved


# Example usage (make sure to replace placeholders with actual implementations)
# faiss_index = faiss.IndexFlatL2(768)  # Assuming 768-dimensional embeddings


# Example function calls are commented out to avoid accidental execution without proper setup
# relevant_docs = perform_faiss_search("example query", faiss_index, embeddings, documents)
# context = concatenate_context_docs(relevant_docs)
# refined_query = gpt_query_processing("example query", context, openai_api_key)
# response = gpt_generate_response(refined_query, context, openai_api_key)
# processed_response = post_process_gpt_response(response)
