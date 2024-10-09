import fitz  # PyMuPDF
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

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

# Main function to convert PDF to PNG and compress in parallel
def pdf_to_png_and_compress(pdf_path, output_folder, zoom_x=4.0, zoom_y=4.0):
    pdf_document = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor() as executor:
        futures = []
        
        # Convert and compress pages in parallel
        for page_num in range(pdf_document.page_count):
            future = executor.submit(convert_and_compress_page, pdf_document, page_num, output_folder, zoom_x, zoom_y)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()  # Ensure completion

# Helper function to convert and compress a single page
def convert_and_compress_page(pdf_document, page_num, output_folder, zoom_x=4.0, zoom_y=4.0):
    # Convert the PDF page to PNG
    image_path = convert_page_to_png(pdf_document, page_num, output_folder, zoom_x, zoom_y)
    
    # Compress the image and remove the original
    if image_path:
        compress_and_remove_image(image_path)

# Example usage:
pdf_file = 'compress_pdf.pdf'
output_dir = 'output_images_folder'

# Run the function
pdf_to_png_and_compress(pdf_file, output_dir)
