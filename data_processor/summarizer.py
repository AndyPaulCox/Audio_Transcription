import os
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

def process_text_file(file_path):
    """Process a text file to summarize and timestamp its content."""
    with open(file_path, 'r') as file:
        text = file.read()
    print("Reading meeting transcription:{file_path}")
    summarized_text = summarize_text(text)
    timestamped_summary = timestamp_text(summarized_text)

    # Save the summarized and timestamped text to a new file
    print("Saving meeting summary:{file_path}")
    output_file_path = file_path.replace('.txt', '_summarized.txt')
    with open(output_file_path, 'w') as file:
        file.write(timestamped_summary)
    print(f"Summarized text saved to: {output_file_path}")