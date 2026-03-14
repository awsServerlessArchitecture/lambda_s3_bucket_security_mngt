---

# Monitor Encrypted and Unencrypted S3 Buckets Using AWS Lambda and Boto3

## 📌 Objective
This project demonstrates how to use **AWS Lambda** with **Boto3** to detect S3 buckets without server‑side encryption.  
Since AWS now **mandates encryption by default** (all new buckets are automatically encrypted), the Lambda function has been updated to print **both encrypted and unencrypted buckets** for validation and auditing.

---

## ⚙️ Setup Instructions

### 1. S3 Buckets
- Navigate to the **S3 dashboard**.
- Create a few buckets.  
- By default, they will be encrypted (SSE‑S3 or SSE‑KMS).  
- If your account allows, disable encryption on one bucket for testing. Otherwise, all buckets will appear under “encrypted.”

---

### 2. IAM Role for Lambda
- In **IAM**, create a role for Lambda.
- Attach the following policies:
  - `AmazonS3ReadOnlyAccess` (to list buckets and check encryption).
  - `CloudWatchLogsFullAccess` (to allow Lambda to write logs).

For production, restrict permissions to just:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListAllMyBuckets","s3:GetBucketEncryption"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
      "Resource": "*"
    }
  ]
}
```

---

### 3. Lambda Function (Python 3.x)

```python
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
```

---

## 🧪 Testing Steps

### Step 1: Create the Lambda Function
1. Go to the **Lambda dashboard**.
2. Click **Create function** → Author from scratch.
3. Choose **Python 3.x** as the runtime.
4. Assign the IAM role created earlier. if not able to select role, then later under configuration of function you can edit.
5. Paste the code above into the function editor.
6. Click **Deploy**.

---

### Step 2: Invoke the Function
1. In the Lambda console, click **Test**.
2. Create a test event (any JSON payload is fine, e.g., `{}`).
3. Run the function.
4. The function will scan all buckets and print results.

---

### Step 3: View CloudWatch Logs
1. Navigate to **CloudWatch → Logs → Log groups**.
2. Find the log group:  
   `/aws/lambda/<your-function-name>`
3. Open the latest log stream.
4. You’ll see entries like:
   ```
   Bucket 'heroviredb1' has encryption enabled.
   Bucket 'legacybucket123' does NOT have encryption enabled.
   Scan complete
   ```

Return JSON:
```json
{
  "status": "Scan complete",
  "encrypted_buckets": ["heroviredb1"],
  "unencrypted_buckets": ["legacybucket123"]
}
```

---

## 🚀 Notes
- **AWS Mandate**: As of 2023, AWS automatically enables encryption for all new buckets.  
- **Validation Approach**: Printing both encrypted and unencrypted lists ensures the Lambda logic is correct, even if all buckets are encrypted.  
- **Enhancements**:
  - Schedule daily scans with **CloudWatch Event Rules**.
  - Send results to **SNS** or Slack for alerts.
  - Extend to check **object‑level encryption** if bucket‑level encryption is always enforced.

---

