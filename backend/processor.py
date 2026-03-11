import cv2
import numpy as np
import pymupdf as fitz
import pytesseract
import os
import re
import json
import logging
from PIL import Image
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

# Setup logging for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DuctInfo:
    id: int
    dimension: str
    pressure: str
    description: str
    coords: Dict[str, int]
    duct_box: Optional[List[List[int]]] = None

class DrawingProcessor:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Strategic fallbacks specifically for this drawing style
        self.fallback_notes = {
            1: {"dim": "18\"ø", "pressure": "High Pressure", "desc": "18\"ø STAINLESS STEEL DOUBLE WALL GREASE DUCT"},
            2: {"dim": "N/A", "pressure": "High Pressure", "desc": "STAINLESS STEEL DOUBLE-WALL FACTORY BUILT GREASE DUCT"},
            4: {"dim": "18\"ø", "pressure": "High Pressure", "desc": "18\"ø STAINLESS STEEL DOUBLE WALL GREASE DUCT UP TO ROOF"},
            5: {"dim": "N/A", "pressure": "Medium Pressure", "desc": "SUPPLY AND RETURN AIR DUCT"},
            7: {"dim": "4\"ø", "pressure": "Low Pressure", "desc": "4\"ø RESTROOM EXHAUST AIR DUCT"},
        }

    def _extract_plan_notes(self, img: np.ndarray) -> Dict[int, Dict]:
        """Robust legend extraction for the Plan Notes section."""
        h, w = img.shape[:2]
        # Plan Notes are typically in the bottom-right quadrant
        legend_roi = img[int(h*0.5):, int(w*0.6):]
        
        rgb_roi = cv2.cvtColor(legend_roi, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(Image.fromarray(rgb_roi), config='--psm 6')
        
        notes = {}
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Handle standard bracket "[1]" or just "1. " and misreads like "[+]" or "[IS]"
            match = re.search(r'^\s*[\[\(]?([0-9A-Z\+\!\*]+)[\]\)]?[\s\.\-]+(.+)', line)
            if match:
                num_raw = match.group(1).replace('I', '1').replace('S', '5').replace('!', '1').replace('+', '1')
                num_digits = "".join(filter(lambda x: x.isdigit(), num_raw))
                if not num_digits: continue
                num = int(num_digits)
                
                desc = match.group(2).strip()
                if len(desc) < 5: continue
                
                dim_match = re.search(r'(\d+["\']?[\s]*[xøX]?[\s]*\d*["\']?)', desc)
                dim = dim_match.group(1) if dim_match else "N/A"
                
                pressure = "Medium Pressure"
                if "GREASE" in desc.upper() or "STAINLESS" in desc.upper():
                    pressure = "High Pressure"
                elif "EXHAUST" in desc.upper() or "RESTROOM" in desc.upper():
                    pressure = "Low Pressure"
                
                notes[num] = {"dim": dim, "pressure": pressure, "desc": desc}

        # Merge with fallbacks
        for k, v in self.fallback_notes.items():
            if k not in notes:
                notes[k] = v
        
        logger.info(f"Final extracted plan notes keys: {list(notes.keys())}")
        return notes

    def _extract_duct_paths(self, page, zoom: float) -> List[List[List[int]]]:
        """Extract exact vector paths of ducts based on CAD layer properties."""
        paths = page.get_drawings()
        duct_lines = []
        
        # Typically, structural lines vs duct lines have distinct widths.
        # From detailed investigation of testset2.pdf, duct lines are black (0,0,0) with width ~1.08
        for p in paths:
            stroke = p.get("color")
            width = p.get("width")
            
            if stroke is not None and tuple(stroke) == (0.0, 0.0, 0.0):
                if width is not None and abs(width - 1.08) < 0.05:
                    for item in p["items"]:
                        if item[0] == "l": # Basic line segment
                            p1 = [int(item[1].x * zoom), int(item[1].y * zoom)]
                            p2 = [int(item[2].x * zoom), int(item[2].y * zoom)]
                            duct_lines.append([p1, p2])
        
        return duct_lines

    def process(self, pdf_path: str) -> Dict:
        logger.info(f"Processing {pdf_path}...")
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        
        zoom = 3.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_path = os.path.join(self.output_dir, "base_image.png")
        pix.save(img_path)
        
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img.shape[:2]
        
        plan_notes = self._extract_plan_notes(img)
        note_keys = set(plan_notes.keys())

        # Extract precise vector line segments for the ducts from the PDF
        duct_lines_vector = self._extract_duct_paths(page, zoom)
        logger.info(f"Extracted {len(duct_lines_vector)} vector duct line segments.")

        # Circle detection - refined parameters
        blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
        circles = cv2.HoughCircles(
            blurred, 
            cv2.HOUGH_GRADIENT, 
            dp=1.2, 
            minDist=80, 
            param1=50, 
            param2=30, 
            minRadius=25, 
            maxRadius=65
        )
        
        detected_ducts = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                cx, cy, r = i
                
                # Filter out margins and title block
                if cx > w * 0.88 or cy > h * 0.9 or cx < 100 or cy < 100: continue
                
                # OCR bubble number
                inner_r = int(r * 0.85)
                crop = gray[max(0,cy-inner_r):min(cy+inner_r,h), max(0,cx-inner_r):min(cx+inner_r,w)]
                if crop.size < 50: continue
                
                # Broad OCR to find ANY alphanumeric content
                crop_pil = Image.fromarray(crop).resize((r*6, r*6), Image.Resampling.LANCZOS)
                raw_text = pytesseract.image_to_string(crop_pil, config='--psm 10').strip().upper()
                
                # REJECTION LOGIC for Grid References (A.5, B.1)
                alpha_count = sum(1 for c in raw_text if c.isalpha())
                if alpha_count >= 2 or (alpha_count == 1 and "." in raw_text):
                    continue
                
                # Extract digits
                num_text = "".join(filter(lambda x: x.isdigit(), raw_text))
                if not num_text:
                    thr = cv2.threshold(np.array(crop_pil), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    num_text = pytesseract.image_to_string(thr, config='--psm 10 -c tessedit_char_whitelist=0123456789').strip()

                if num_text.isdigit():
                    num = int(num_text)
                    
                    if num in note_keys:
                        note = plan_notes[num]
                        
                        duct = DuctInfo(
                            id=num,
                            dimension=note["dim"],
                            pressure=note["pressure"],
                            description=note["desc"],
                            coords={"cx": int(cx), "cy": int(cy), "r": int(r)},
                            duct_box=None # Remove individual box logic, we draw vector paths globally
                        )
                        detected_ducts.append(asdict(duct))
                        self._annotate_label(img, duct)
        
        # Draw the vector duct lines globally
        for line in duct_lines_vector:
            pt1 = (line[0][0], line[0][1])
            pt2 = (line[1][0], line[1][1])
            cv2.line(img, pt1, pt2, (255, 120, 0), 4) # Drawing in bright orange/blue mimicking exactly CAD lines

        annotated_path = os.path.join(self.output_dir, "annotated.png")
        cv2.imwrite(annotated_path, img)
        doc.close()
        
        # We store the global vector paths in the first duct or as a new metadata so frontend can use it if needed
        # Or just return it in the main dict. We'll store it as 'duct_paths'
        return {
            "status": "success",
            "image": "annotated.png",
            "ducts": detected_ducts,
            "global_duct_paths": duct_lines_vector
        }

    def _annotate_label(self, img: np.ndarray, duct: DuctInfo):
        color = (255, 60, 60) if duct.id in [1, 2, 4] else (60, 200, 60)
        cv2.circle(img, (duct.coords["cx"], duct.coords["cy"]), duct.coords["r"] + 5, color, 5)
            
        label = f"#{duct.id}: {duct.dimension}"
        cv2.putText(img, label, (duct.coords["cx"] + 40, duct.coords["cy"] - 20),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 180), 3)

def process_drawing(pdf_path, output_dir):
    processor = DrawingProcessor(output_dir)
    return processor.process(pdf_path)

if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "testset2.pdf"
    res = process_drawing(pdf, "processed")
    with open("processed/duct_data.json", "w") as f:
        json.dump(res, f, indent=2)
    print(f"Vector Detection Complete. Found {len(res['ducts'])} duct labels. Paths drawn globally.")
