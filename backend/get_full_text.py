import pymupdf as fitz
import json

def get_full_text_details(pdf_path):
    doc = fitz.open(pdf_path)
    res = []
    for i, page in enumerate(doc):
        # Extract dictionary with all details
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        res.append({
                            "page": i,
                            "bbox": s["bbox"],
                            "text": s["text"],
                            "font": s["font"],
                            "size": s["size"]
                        })
    doc.close()
    return res

if __name__ == "__main__":
    data = get_full_text_details("testset2.pdf")
    with open("full_text_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Extracted {len(data)} text spans.")
