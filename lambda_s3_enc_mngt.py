import boto3
from botocore.exceptions import ClientError

# Initialize S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    encrypted_buckets = []
    unencrypted_buckets = []

    # List all buckets
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            # Try to get bucket encryption
            s3.get_bucket_encryption(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' has encryption enabled.")
            encrypted_buckets.append(bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                print(f"Bucket '{bucket_name}' does NOT have encryption enabled.")
                unencrypted_buckets.append(bucket_name)
            else:
                print(f"Error checking bucket '{bucket_name}': {e}")

    return {
        "status": "Scan complete",
        "encrypted_buckets": encrypted_buckets,
        "unencrypted_buckets": unencrypted_buckets
    }
