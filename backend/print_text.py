import pymupdf as fitz

def print_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        print(f"--- Page {i} ---")
        print(text)
    doc.close()

if __name__ == "__main__":
    print_all_text("testset2.pdf")
