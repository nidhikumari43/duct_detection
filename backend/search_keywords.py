import pymupdf as fitz
import re

def search_keywords(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    
    # Duct labels: 14"ø, 10x8, 12"ø, etc.
    labels = re.findall(r'\b\d+["\']?[xøX]?[\s]*\d*["\']?\b', all_text)
    
    # Pressure class: LP, MP, HP, low pressure, medium pressure, high pressure
    pressure_classes = re.findall(r'(?i)\b(LP|MP|HP|LOW PRESSURE|MEDIUM PRESSURE|HIGH PRESSURE)\b', all_text)
    
    print("Labels found:", list(set(labels))[:20])
    print("Pressure classes found:", list(set(pressure_classes)))
    
    doc.close()

if __name__ == "__main__":
    search_keywords("testset2.pdf")
