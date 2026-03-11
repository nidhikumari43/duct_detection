import pymupdf as fitz
import json

def extract_paths(pdf_path):
    doc = fitz.open(pdf_path)
    path_data = []
    for i in range(len(doc)):
        page = doc.load_page(i)
        paths = page.get_drawings()  # Returns paths (shapes)
        for p in paths:
            path_data.append({
                "page": i,
                "bbox": [p["rect"].x0, p["rect"].y0, p["rect"].x1, p["rect"].y1],
                "type": p["type"]
                # "items": p["items"] # This can be huge, but maybe useful later
            })
    doc.close()
    return path_data

if __name__ == "__main__":
    data = extract_paths("testset2.pdf")
    with open("path_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Extracted {len(data)} paths.")
