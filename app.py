from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
# CORS allows your GitHub website to talk to this Render server
CORS(app)

# Create upload folder if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Backend is running on Port 10000 with OCR!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    
    # Define file paths
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    # Save the uploaded PDF
    file.save(pdf_path)

    # --- ADVANCED OCR & LAYOUT SETTINGS ---
    # These settings specifically target the RCRC/Parsons logos and bullets
    settings = {
        'ocr': True,                         # Uses image recognition to "see" layout
        'connected_border_tolerance': 0.1,   # Forces separation of logos
        'float_image_ignorable_gap': 1.0,    # Prevents logos merging with banner
        'line_margin': 0.1,                  # Detects thin underlines
        'shape_min_dimension': 0.1           # Detects small bullet points
    }

    try:
        # Initialize and run conversion
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        
        # Send the Word file back to your website
        return send_file(docx_path, as_attachment=True)
        
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Cleanup: Remove the files from the server after conversion
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    # Render requires host '0.0.0.0' and port 10000 for the free tier
    app.run(host='0.0.0.0', port=10000)
