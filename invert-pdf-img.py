import argparse
import sys
import os
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import numpy as np
from fpdf import FPDF

def parse_page_range(range_str, total_pages):
    """
    Parse a page range string into a list of page numbers.
    
    Args:
        range_str (str): Range string (e.g., "1-3,5,7-9")
        total_pages (int): Total number of pages in the PDF
    
    Returns:
        list: List of page numbers (0-based indices)
    """
    if not range_str:
        return list(range(total_pages))
    
    pages = set()
    for part in range_str.split(','):
        if '-' in part:
            start, end = map(str.strip, part.split('-'))
            start = int(start) - 1  # Convert to 0-based index
            end = int(end) - 1  # Convert to 0-based index
            pages.update(range(start, end + 1))  # Include the end page
        else:
            pages.add(int(part.strip()) - 1)  # Convert to 0-based index
    
    # Validate page numbers
    if any(p < 0 or p >= total_pages for p in pages):
        raise ValueError(f"Page numbers must be between 1 and {total_pages}")
    
    return sorted(list(pages))

def adjust_inversion(image, intensity=0.95, text_darkness=0.8):
    """
    Invert image colors with adjustable intensity and text darkness.
    
    Args:
        image (PIL.Image): Input image
        intensity (float): Overall inversion intensity (0.0 to 1.0)
        text_darkness (float): How dark the text should be (0.0 to 1.0)
                             1.0 means pure white text, 0.8 means slightly darker
    
    Returns:
        PIL.Image: Processed image
    """
    # Convert to numpy array for easier manipulation
    img_array = np.array(image)
    
    # Invert the image
    inverted = 255 - img_array
    
    # Apply intensity adjustment
    if intensity < 1.0:
        # Blend between original and inverted based on intensity
        img_array = (1 - intensity) * img_array + intensity * inverted
    else:
        img_array = inverted
    
    # Adjust text brightness (values closer to 255 are brighter)
    if text_darkness < 1.0:
        # Only adjust pixels that are close to white (text)
        white_threshold = 200
        text_mask = img_array > white_threshold
        img_array[text_mask] = img_array[text_mask] * text_darkness
    
    # Ensure values are within valid range
    img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array)

def invert_pdf_colors(input_pdf, output_pdf, page_range=None, intensity=1.0, text_darkness=0.8):
    """
    Convert specified pages of a PDF from black text on white background to light text on dark background.
    
    Args:
        input_pdf (str): Path to input PDF file
        output_pdf (str): Path where the modified PDF will be saved
        page_range (str): Range of pages to invert (e.g., "1-3,5,7-9")
        intensity (float): Overall inversion intensity (0.0 to 1.0)
        text_darkness (float): How dark the text should be (0.0 to 1.0)
    """
    # Convert PDF to images
    pages = convert_from_path(input_pdf)
    
    # Parse page range
    pages_to_invert = parse_page_range(page_range, len(pages))
    
    # Create a directory for temporary files
    if not os.path.exists('temp'):
        os.makedirs('temp')
    
    # Process each page
    temp_paths = []
    try:
        for i, page in enumerate(pages):
            temp_path = f'temp/page_{i}.jpg'
            
            if i in pages_to_invert:
                # Convert to grayscale and apply adjusted inversion
                gray_page = page.convert('L')
                processed_page = adjust_inversion(gray_page, intensity, text_darkness)
                processed_page.save(temp_path, 'JPEG', quality=95)
            else:
                # Save original page without inversion
                page.convert('RGB').save(temp_path, 'JPEG', quality=95)
            
            temp_paths.append(temp_path)
        
        # Create new PDF with processed pages
        pdf = FPDF()
        for page in temp_paths:
            pdf.add_page()
            pdf.image(page, x=0, y=0, w=210)  # A4 width = 210mm
        
        # Save the modified PDF
        pdf.output(output_pdf)
        
    finally:
        # Clean up temporary files
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        if os.path.exists('temp'):
            os.rmdir('temp')

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Convert specified pages of a PDF from dark text on light background to light text on dark background.'
    )
    parser.add_argument(
        'input_pdf',
        help='Path to the input PDF file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Path for the output PDF file (default: input_inverted.pdf)',
        default=None
    )
    parser.add_argument(
        '-p', '--pages',
        help='Range of pages to invert (e.g., "1-3,5,7-9"). If not specified, all pages will be inverted.',
        default=None
    )
    parser.add_argument(
        '-i', '--intensity',
        help='Inversion intensity (0.0 to 1.0, default: 1.0)',
        type=float,
        default=1.0
    )
    parser.add_argument(
        '-t', '--text-darkness',
        help='Text darkness level (0.0 to 1.0, default: 0.8). Lower values make text darker.',
        type=float,
        default=0.8
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate intensity and text darkness
    if not (0 <= args.intensity <= 1):
        print("Error: Intensity must be between 0.0 and 1.0")
        sys.exit(1)
    if not (0 <= args.text_darkness <= 1):
        print("Error: Text darkness must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Check if input file exists
    if not os.path.exists(args.input_pdf):
        print(f"Error: Input file '{args.input_pdf}' does not exist.")
        sys.exit(1)
    
    # Generate output filename if not provided
    if args.output is None:
        base, ext = os.path.splitext(args.input_pdf)
        args.output = f"{base}_inverted{ext}"
    
    try:
        print(f"Processing '{args.input_pdf}'...")
        invert_pdf_colors(
            args.input_pdf,
            args.output,
            args.pages,
            args.intensity,
            args.text_darkness
        )
        print(f"Successfully created modified PDF: '{args.output}'")
    except Exception as e:
        print(f"Error: Failed to process PDF: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()