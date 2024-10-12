import fitz  # PyMuPDF
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image  # Pillow for handling images
from reportlab.pdfgen import canvas  # ReportLab to create PDFs

# Function to convert PDF page to PNG
def convert_page_to_png(pdf_document, page_num, output_folder, zoom_x=4.0, zoom_y=4.0):
    page = pdf_document.load_page(page_num)
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    output_path = os.path.join(output_folder, f'page_{page_num + 1}.png')
    pix.save(output_path)
    return output_path

# Function to compress PNG using ImageMagick and remove original PNG
def compress_and_remove_image(image_path):
    compressed_image_path = image_path.replace(".png", "_compressed.png")
    command = ["magick", image_path, "-strip", "-colors", "256", compressed_image_path]
    
    try:
        # Run ImageMagick command to compress the image
        subprocess.run(command, check=True)
        print(f"Compressed {compressed_image_path}")
        
        # Remove the original uncompressed image
        os.remove(image_path)
        print(f"Removed original {image_path}")
        return compressed_image_path
    except subprocess.CalledProcessError as e:
        print(f"Error compressing {image_path}: {e}")
        return None

# Function to merge compressed PNGs into a single PDF
def merge_images_to_pdf(image_paths, output_pdf_path):
    # Open images and convert them to RGB (PDF doesn't support transparency)
    images = [Image.open(img).convert("RGB") for img in image_paths]
    
    # Save images as a single PDF file
    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        print(f"PDF saved as {output_pdf_path}")
    else:
        print("No images to merge into PDF.")

# Main function to convert PDF to PNG, compress, and merge into PDF
def pdf_to_png_and_compress(pdf_path, output_folder, output_pdf, zoom_x=4.0, zoom_y=4.0):
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    compressed_image_paths = []  # Store compressed images for PDF merging

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = []
        
        # Convert and compress pages in parallel
        for page_num in range(pdf_document.page_count):
            future = executor.submit(convert_and_compress_page, pdf_document, page_num, output_folder, zoom_x, zoom_y)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            compressed_image = future.result()  # Ensure completion
            if compressed_image:
                compressed_image_paths.append(compressed_image)  # Collect compressed images
    
    # Merge all compressed PNGs into a PDF
    merge_images_to_pdf(compressed_image_paths, output_pdf)

# Helper function to convert and compress a single page
def convert_and_compress_page(pdf_document, page_num, output_folder, zoom_x=4.0, zoom_y=4.0):
    # Convert the PDF page to PNG
    image_path = convert_page_to_png(pdf_document, page_num, output_folder, zoom_x, zoom_y)
    
    # Compress the image and remove the original
    if image_path:
        return compress_and_remove_image(image_path)

# Example usage:
pdf_file = 'compress_pdf.pdf'
output_dir = 'output_images_folder'
output_pdf = 'merged_output.pdf'

# Run the function
pdf_to_png_and_compress(pdf_file, output_dir, output_pdf)
