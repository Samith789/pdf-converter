from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
CORS(app)

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Backend is running with OCR enabled!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    # Check if a file was sent
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    
    # Define paths
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    # Save the uploaded PDF
    file.save(pdf_path)

    # --- ADVANCED OCR & LAYOUT SETTINGS ---
    # These settings help separate the RCRC/Parsons logos and find bullets
    settings = {
        'ocr': True,                         # Use OCR to "see" logos and bullets
        'connected_border_tolerance': 0.1,   # Strict separation to stop logos from merging
        'float_image_ignorable_gap': 1.0,    # Prevents banner from "eating" the logos
        'line_margin': 0.1,                  # Better detection for underlines
        'shape_min_dimension': 0.1           # Don't ignore small dots like bullets
    }

    try:
        # Initialize converter
        cv = Converter(pdf_path)
        
        # Convert with advanced settings
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        
        # Send the converted file back to the user
        return send_file(docx_path, as_attachment=True)
        
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Optional: Clean up files to save space on Render
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    # For local testing
    app.run(debug=True, port=10000)
