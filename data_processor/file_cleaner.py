import boto3
import os

def delete_unwanted_files(bucket, prefix='', include_subdirectories=False):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    print(f"FdelUF: Response from S3: {response}")
    if 'Contents' in response:
        for obj in response['Contents']:
            file_key = obj['Key']
            print(f"FdelUF: File key from S3: {file_key}")
            # Check if the file is in the top level or in a subdirectory based on slashes in the key
            #in_top_level = '/' not in file_key[len(prefix):].lstrip('/')
            if file_key.startswith('.'):
                s3_client.delete_object(Bucket=bucket, Key=file_key)
                print(f"FdelUF: Deleted unwanted file: {file_key}")
                
        #s3_client = boto3.client('s3')
        # Ensure folder name ends with a '/'
        prefix = 'Input'
        # Continuously fetch objects and delete them until all are removed
        while True:
            # List objects within the specified folder
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
            # Check if there are contents to delete
            if 'Contents' not in response:
                print("No more files to delete.")
                break

            # Filter and delete each object that starts with '.'
            for obj in response['Contents']:
                file_key = obj['Key']
                if file_key.split('/')[-1].startswith('.'):
                    s3_client.delete_object(Bucket=bucket, Key=file_key)
                    print(f"Deleted: {file_key}")

            # Check if the response is truncated, indicating more objects to fetch
            if not response.get('IsTruncated'):
                break  # Exit loop if no more objects to list
                
def delete_s3_object(bucket, key):
    """
    Delete a specific file in an S3 bucket
    """
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket=bucket, Key=key)
    
    
def delete_temp_files(folder_path):
    """
    Delete temporary files with names like 'chunk1.txt', 'chunk2.txt', etc.
    
    Args:
    folder_path (str): The path to the folder containing the files.
    """
    # List all files in the folder
    files = os.listdir(folder_path)

    # Iterate through each file in the folder
    for file in files:
        # Check if the file name starts with 'chunk' and ends with '.txt'
        if file.startswith('chunk') and file.endswith('.txt'):
            # Construct the full file path
            file_path = os.path.join(folder_path, file)
            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {file_path}")


