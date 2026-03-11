import pymupdf as fitz
import sys

def convert_pdf_to_images(pdf_path, output_prefix):
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom in for better resolution
        pix.save(f"{output_prefix}_{i}.png")
    doc.close()

if __name__ == "__main__":
    convert_pdf_to_images("testset2.pdf", "sheet")
