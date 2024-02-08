import boto3
import datetime


def list_files(bucket, prefix):
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    # Print the entire response for debugging
    print(f"Response from S3: {response}")
    if 'Contents' not in response or not response['Contents']:
        # Print a message if no files are found
        print(f"No files found in {bucket} with prefix '{prefix}'")
    else:
        for obj in response['Contents']:
            # Check if the object represents a file (not a folder)
            if obj['Size'] > 0:
                yield obj.get('Key')


def start_transcribe_job(s3_uri, job_name, output_bucket):
    transcribe_client = boto3.client('transcribe')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    output_filename = f"transcript-{timestamp}.json"
    output_path = f"{output_bucket}"
    print(f"Initiating transcription job for file: {s3_uri} with job name: {job_name}")
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat='wav', # Change this depending on your file format
        LanguageCode='en-US', # Change this depending on your language
        OutputBucketName=output_path
    )

def check_job_status(job_name):
    """
    Check the status of a Amazon Transcribe job
    """
    transcribe_client = boto3.client('transcribe')
    response = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    return response['TranscriptionJob']['TranscriptionJobStatus']

