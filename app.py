from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
# CORS allows your GitHub website to securely talk to this Render server
CORS(app)

# Setup upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Server is Live and Ready!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    file.save(pdf_path)

    # --- ADVANCED OCR SETTINGS ---
    # These fix the RCRC/Parsons logos and the bullet points
    settings = {
        'ocr': True,                         # Enables image recognition
        'connected_border_tolerance': 0.1,   # Forces logos to stay separate
        'float_image_ignorable_gap': 1.0,    # Prevents logos merging with banner
        'line_margin': 0.1,                  # Detects thin underlines
        'shape_min_dimension': 0.1           # Specifically finds bullet points
    }

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        # Cleanup server storage
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    # IMPORTANT: Render needs host '0.0.0.0' and port 10000 to connect
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
