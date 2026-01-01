from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Backend is running!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.replace('.pdf', '.docx')
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    file.save(pdf_path)

    # --- ADVANCED SETTINGS FOR BETTER LAYOUT ---
    settings = {
        'connected_border_tolerance': 0.3,   # Keeps logos separate
        'float_image_ignorable_gap': 2.0,    # Prevents images from merging
        'line_margin': 0.1,                  # Better underline detection
        'shape_min_dimension': 0.1,          # Better bullet point detection
        'ocr': False                         
    }

    try:
        cv = Converter(pdf_path)
        # We use the settings here to solve your logo/bullet issues
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
