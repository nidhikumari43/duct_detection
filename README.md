# HVAC Duct Detector

An automated system to detect HVAC ducts from mechanical drawings, provide dimensions, and identify pressure classes.

## Features
- **PDF/Image Processing**: Converts engineering drawings to high-resolution images.
- **Duct Detection**: Uses OpenCV and Tesseract to identify duct bubbles and associated rectangular duct bodies.
- **Smart Analysis**: Maps note numbers to descriptions to extract dimensions (e.g., `14"ø`) and determine pressure class (Low/Medium/High Pressure).
- **Interactive UI**: Modern Next.js interface with glassmorphism, dynamic SVG overlays, and a detailed sidebar for engineering metadata.

## Tech Stack
- **Frontend**: Next.js, Tailwind CSS, Framer Motion (visuals).
- **Backend**: FastAPI, PyMuPDF, OpenCV, Tesseract OCR.

## Setup Instructions

### 1. Requirements
Ensure you have the following installed:
- Python 3.9+
- Node.js 18+
- Tesseract OCR (e.g., `brew install tesseract`)

### 2. Backend Setup
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 main.py
```
*Backend runs on http://localhost:8001*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on http://localhost:3000 (or 3001)*

## Usage
1. Open the web app.
2. Click **🚀 Run Sample Analysis** to see the results for the provided `testset2.pdf`.
3. Click on any red circular bubble to view the duct's dimension and pressure class in the sidebar.
4. You can also upload your own mechanical drawing for analysis.

## Assignment Requirements Fulfilled
- ✅ Read ducts in the drawing.
- ✅ Annotate ducts with lines (highlights).
- ✅ Provide dimensions (e.g., `14"ø`).
- ✅ Identify pressure class (Low/Medium/High).
- ✅ Video/Screenshot demonstration provided in the workspace.
