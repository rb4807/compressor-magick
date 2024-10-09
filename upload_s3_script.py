import os
import boto3
from datetime import datetime

# Replace with your S3 bucket name
AWS_STORAGE_BUCKET_NAME = 'bucket name'

def get_s3_client():
    aws_access_key_id = "key"
    aws_secret_access_key = "keyF"
    print(aws_access_key_id,aws_secret_access_key)
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

def upload_files_to_s3(folder='images', output_file='uploaded_files.txt'):
    # Get all files from the specified folder
    try:
        files = os.listdir(folder)
    except FileNotFoundError:
        print(f"The folder '{folder}' does not exist.")
        return

    # Filter out image files based on their extensions
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']  # Add any other image formats if necessary
    image_files = [file for file in files if file.split('.')[-1].lower() in image_extensions]

    if not image_files:
        print("No image files found in the folder.")
        return

    s3 = get_s3_client()

    # Open the output text file in write mode
    with open(output_file, 'w') as txt_file:
        for image_file in image_files:
            file_path = os.path.join(folder, image_file)
            file_extension = image_file.split('.')[-1].lower()
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_file_name = f"{os.path.splitext(image_file)[0]}_{current_date}.{file_extension}"

            try:
                # Upload the file to S3
                with open(file_path, 'rb') as f:
                    s3.upload_fileobj(f, AWS_STORAGE_BUCKET_NAME, s3_file_name)
                s3_file_url = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{s3_file_name}'

                # Write the URL to the text file
                txt_file.write(s3_file_url + '\n')

                print(f"File '{image_file}' uploaded successfully. URL: {s3_file_url}")
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")
            except Exception as e:
                print(f"Failed to upload '{image_file}': {e}")

    print(f"S3 file URLs saved to '{output_file}'")

if __name__ == "__main__":
    upload_files_to_s3()
