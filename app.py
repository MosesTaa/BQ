from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import tempfile
import os
import cv2
import pytesseract

app = Flask(__name__)

def extract_from_vector(pdf_path):
    doc = fitz.open(pdf_path)
    rooms = []
    doors = []
    
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:  # text block
                for line in b['lines']:
                    for span in line['spans']:
                        text = span['text']
                        if 'Room' in text or 'RM' in text:
                            rooms.append(text)
                        if 'Door' in text or 'D' in text:
                            doors.append(text)
    return {
        "type": "vector",
        "rooms_found": len(rooms),
        "doors_found": len(doors),
        "room_labels": rooms,
        "door_labels": doors
    }

def extract_from_scanned(pdf_path):
    doc = fitz.open(pdf_path)
    rooms = []
    doors = []

    for page_index in range(len(doc)):
        pix = doc[page_index].get_pixmap(dpi=300)
        temp_img_path = tempfile.mktemp(suffix=".png")
        pix.save(temp_img_path)

        img = cv2.imread(temp_img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)

        for line in text.split('\n'):
            if 'Room' in line or 'RM' in line:
                rooms.append(line)
            if 'Door' in line or 'D' in line:
                doors.append(line)

        os.remove(temp_img_path)

    return {
        "type": "scanned",
        "rooms_found": len(rooms),
        "doors_found": len(doors),
        "room_labels": rooms,
        "door_labels": doors
    }

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    pdf_file = request.files['pdf']
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_file.save(tmp.name)
        pdf_path = tmp.name

    try:
        result = extract_from_vector(pdf_path)
        if result["rooms_found"] == 0:
            result = extract_from_scanned(pdf_path)
        return jsonify(result)
    finally:
        os.remove(pdf_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
