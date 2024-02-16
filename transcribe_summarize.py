import datetime
import time
import os
from data_processor import *


def main():
    bucket_name = 'r-sample-69c534b4'
    input_prefix = 'Input/'
    directory = '/Users/apcox/AWS_S3/'  # Update this path to your specific directory
    store_path = '/Users/apcox/AWS_S3/library/full_texts/'
    store_path_summaries = '/Users/apcox/AWS_S3/library/summaries/'
    write_file_path ='/Users/apcox/AWS_S3/temp/'
    chunk_size_words = 5500  #limit of LLM if larger than this the dociument will be split into chunks of this size, if less only a single chunk will be output
    
    while True:
        # Delete files starting with '._'
        delete_unwanted_files(bucket_name,include_subdirectories=False)
        for file_key in list_files(bucket_name, input_prefix):
            s3_uri = f's3://{bucket_name}/{file_key}'
            print(f"Processing file:: {s3_uri}")
            job_name = f"Transcribe_{os.path.basename(file_key)}_{int(time.time())}"
            print(f"Checking status for transcription job: {job_name}")
            start_transcribe_job(s3_uri, job_name, bucket_name)

            while True:
                status = check_job_status(job_name)
                print(f"Current status of job '{job_name}': {status}")
                if status in ['COMPLETED', 'FAILED']:
                    break
                time.sleep(30)  # Wait for 30 seconds before checking the status again

            if status == 'COMPLETED':
                print(f"Transcription job '{job_name}' completed successfully.")
                wav_file_path = f'{file_key}'
                delete_s3_object(bucket_name, wav_file_path)
                print(f"Deleting wav file at: {wav_file_path}")
                # List and process each JSON file in the output folder
        json_files = list_json_files(bucket_name)
        for json_file in json_files:
            print(f"Now processing json file: {json_file }")
            transcript_text = process_json_files(bucket_name)
            delete_s3_object(bucket_name, json_file)
        #If the file to summarize is larger than capacity of LLM split into chunks
        # Iterate over each item in the directory
            for item in os.listdir(directory):
                # Construct the full path of the item
                item_path = os.path.join(directory, item)
                # Check if the item is a file
                if os.path.isfile(item_path):
                    # Call your function to process each file
                    split_text_into_chunks(transcript_text, directory, chunk_size_words, store_path)
        
        # Now do the summary and action points
        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                process_text_file(directory, filename, write_file_path,store_path_summaries )
        delete_unwanted_files(bucket_name,include_subdirectories=False)
        delete_temp_files(directory)
        time.sleep(60)  # Check for new files every minute 
        
        
if __name__ == '__main__':
    main()