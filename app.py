from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
CORS(app)

# Create upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Backend is running with Advanced OCR!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    file.save(pdf_path)

    # --- FINAL ADVANCED SETTINGS ---
    settings = {
        'ocr': True,                         # Forces engine to "see" logos and bullets
        'connected_border_tolerance': 0.1,   # Forces separation of RCRC/Parsons logos
        'float_image_ignorable_gap': 1.0,    # Keeps logos from merging into background
        'line_margin': 0.1,                  # Better detection for underlines
        'shape_min_dimension': 0.1           # Specifically looks for small bullet dots
    }

    try:
        cv = Converter(pdf_path)
        # Apply the layout-fixing settings
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Cleanup files to keep the free server fast
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    app.run(debug=True, port=10000)
