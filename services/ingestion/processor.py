import os
from typing import List, Tuple
from pdf2image import convert_from_path, convert_from_bytes
import io
from PIL import Image
from pypdf import PdfReader

class PDFProcessor:
    def __init__(self):
        pass

    def process_pdf(self, file_content: bytes, filename: str) -> List[Tuple[int, str, Image.Image]]:
        """
        Converts PDF bytes to images (one per page) and extracting text.
        Returns a list of tuples: (page_number, text_content, image_object)
        """
        results = []
        try:
            # Try converting to images first (requires poppler)
            try:
                images = convert_from_bytes(file_content)
                poppler_available = True
            except Exception as e:
                print(f"Poppler check failed (Image extraction disabled): {e}")
                poppler_available = False
                images = []

            if poppler_available:
                # Flow with images available
                for i, image in enumerate(images):
                    page_num = i + 1
                    text_content = f"Page {page_num} of {filename}" 
                    try:
                        import pytesseract
                        text_content = pytesseract.image_to_string(image)
                    except Exception:
                        pass # OCR failed, use placeholder or pypdf fallback if mixed
                    
                    results.append((page_num, text_content, image))
            else:
                # Fallback to Text-Only using pypdf
                print("Falling back to text-only extraction using pypdf.")
                pdf_reader = PdfReader(io.BytesIO(file_content))
                for i, page in enumerate(pdf_reader.pages):
                    page_num = i + 1
                    text_content = page.extract_text()
                    # Create a blank placeholder image or None
                    # For compatibility with downstream which expects PIL Image, create a blank one.
                    blank_image = Image.new('RGB', (100, 100), color = (255, 255, 255))
                    results.append((page_num, text_content, blank_image))
                
            return results

        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise e
