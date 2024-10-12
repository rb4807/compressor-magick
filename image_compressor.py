import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image  # Pillow for handling images

# Function to compress an image using ImageMagick and save to output folder
def compress_image(image_path, output_folder):
    # Define the output path for the compressed image
    base_name = os.path.basename(image_path)
    compressed_image_path = os.path.join(output_folder, base_name)
    compressed_image_path = compressed_image_path.replace(".png", "_compressed.png").replace(".jpg", "_compressed.jpg").replace(".jpeg", "_compressed.jpeg")
    
    # ImageMagick command for compressing the image
    command = ["magick", image_path, "-strip", "-colors", "256", compressed_image_path]
    
    try:
        # Run ImageMagick command to compress the image
        subprocess.run(command, check=True)
        print(f"Compressed {compressed_image_path}")
        return compressed_image_path
    except subprocess.CalledProcessError as e:
        print(f"Error compressing {image_path}: {e}")
        return None

# Main function to compress images from input folder and store in output folder
def compress_images(input_folder, output_folder):
    # Ensure the input folder exists
    if not os.path.isdir(input_folder):
        print(f"Input folder {input_folder} does not exist.")
        return

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    image_extensions = ['.png', '.jpg', '.jpeg']  # Supported image types
    compressed_image_paths = []  # Store paths of compressed images

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = []
        
        # Compress each image in the input folder
        for filename in os.listdir(input_folder):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                image_path = os.path.join(input_folder, filename)
                future = executor.submit(compress_image, image_path, output_folder)
                futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            compressed_image = future.result()  # Ensure completion
            if compressed_image:
                compressed_image_paths.append(compressed_image)  # Collect compressed images

    print(f"All images have been compressed and saved to {output_folder}")

# Example usage:
input_dir = 'images_to_compress'  # Folder with original images
output_dir = 'compressed_images_folder'  # Folder to save compressed images

# Run the function to compress images from input_dir and store them in output_dir
compress_images(input_dir, output_dir)
