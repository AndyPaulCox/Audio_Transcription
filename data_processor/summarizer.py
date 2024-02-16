import os
import shutil  # Import shutil for moving files
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def summarize_text(text):
    """Send text to OpenAI's ChatGPT for summarization using the updated API syntax."""
    response = client.chat.completions.create(model="gpt-4",  # Updated to use a supported model, e.g., "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": "You are an expert project manager."},
        {"role": "user", "content": f"Please produce a summary ofthe following text and add a section noting any action points:\n\n{text}"}
    ])
    print("completed Summarization")
    return response.choices[0].message.content.strip()

def timestamp_text(text):
    """Append a timestamp to the text."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\nTimestamp: {timestamp}"

def process_text_file(read_file_path,filename,write_file_path,summaries_store_path):
    """Process a text file to summarize and timestamp its content."""
    read_file_name = f'{read_file_path}/{filename}'
    with open(read_file_name, 'r') as file:
        text = file.read()
    print(f"Reading meeting transcription:{read_file_path}")
    summarized_text = summarize_text(text)
    timestamped_summary = timestamp_text(summarized_text)

    # Save the summarized and timestamped text to a new file
    print(f"Saving meeting summary:{read_file_path}temp/{filename}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    filename = f'Summary_{timestamp}.txt'
    output_file_path = f'{summaries_store_path}{filename}'
    with open(output_file_path, 'w') as file:
        file.write(timestamped_summary)
    print(f"Summarized text saved to: {output_file_path}")
    
def split_text_into_chunks(transcript_text, output_folder_path, chunk_size_words, store_path):
    """
    Splits the text from the input file into chunks of approximately chunk_size_words each, 
    saves the chunks into separate files within the specified output folder, 
    and moves the original document to a specified storage folder.
     Returns:
    - A list of paths to the generated chunk files.
    """
    # Ensure the output and storage directories exist
    os.makedirs(output_folder_path, exist_ok=True)
    os.makedirs(store_path, exist_ok=True)
    
    # Read the input file
    # with open(input_file_name, 'r', encoding='utf-8') as file:
    text = transcript_text
    
    # Split the text into words
    words = text.split()
    
    # Calculate how many chunks are needed
    total_chunks = len(words) // chunk_size_words + (1 if len(words) % chunk_size_words > 0 else 0)
    
    chunk_files = []
    
    for i in range(total_chunks):
        # Extract the chunk of words
        chunk = words[i*chunk_size_words : (i+1)*chunk_size_words]
        chunk_text = ' '.join(chunk)
        
        # Define the filename for this chunk
        chunk_filename = f'chunk_{i+1}.txt'
        chunk_file_path = os.path.join(output_folder_path, chunk_filename)
        
        # Save the chunk to a file
        with open(chunk_file_path, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(chunk_text)
        
        chunk_files.append(chunk_file_path)
    
    # Move the original document to the storage folder
    
    return chunk_files
