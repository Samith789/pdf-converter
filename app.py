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

    # Core conversion logic
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

    return send_file(docx_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)