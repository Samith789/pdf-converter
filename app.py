from flask import Flask, request, send_file
from flask_cors import CORS
from pdf2docx import Converter
import os

app = Flask(__name__)
# This line is vital - it allows your website to talk to the server
CORS(app, resources={r"/*": {"origins": "*"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return "Backend is Live!"

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files['file']
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    file.save(pdf_path)

    # High-accuracy OCR settings for your logos and bullets
    settings = {
        'ocr': True,
        'connected_border_tolerance': 0.1,
        'float_image_ignorable_gap': 1.0,
        'line_margin': 0.1,
        'shape_min_dimension': 0.1
    }

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None, **settings) 
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == '__main__':
    # Render requires host 0.0.0.0 and uses the PORT environment variable
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
