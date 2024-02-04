import os
import openai
from datetime import datetime

# It's a good practice to load sensitive information like API keys from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_text(text):
    """Send text to OpenAI's ChatGPT for summarization using the updated API syntax."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Updated to use a supported model, e.g., "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are an expert project manager."},
            {"role": "user", "content": f"Summarize the following text and highlight any action points:\n\n{text}"}
        ]
    )
    return response.choices[0].message['content'].strip()

def timestamp_text(text):
    """Append a timestamp to the text."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\nTimestamp: {timestamp}"

def process_text_file(file_path):
    """Process a text file to summarize and timestamp its content."""
    with open(file_path, 'r') as file:
        text = file.read()

    summarized_text = summarize_text(text)
    timestamped_summary = timestamp_text(summarized_text)

    # Save the summarized and timestamped text to a new file
    output_file_path = file_path.replace('.txt', '_summarized.txt')
    with open(output_file_path, 'w') as file:
        file.write(timestamped_summary)

    print(f"Summarized text saved to: {output_file_path}")

def main():
    directory = '/Users/apcox/AWS_S3/'  # Update this path to your specific directory
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            process_text_file(file_path)

if __name__ == "__main__":
    main()
