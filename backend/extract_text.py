import pymupdf as fitz
import json

def extract_text_with_bboxes(pdf_path):
    doc = fitz.open(pdf_path)
    text_data = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        words = page.get_text("words")  # Return list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        for w in words:
            text_data.append({
                "page": i,
                "bbox": [w[0], w[1], w[2], w[3]],
                "text": w[4]
            })
    doc.close()
    return text_data

if __name__ == "__main__":
    data = extract_text_with_bboxes("testset2.pdf")
    with open("text_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Extracted {len(data)} words.")
