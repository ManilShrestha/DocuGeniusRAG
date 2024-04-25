from flask import Flask, render_template, request, jsonify
import pdfplumber

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        # Using pdfplumber to extract text from the PDF
        with pdfplumber.open(file) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
        text = ' '.join(pages)
        return jsonify({'text': text})
    return jsonify({'error': 'Failed to process file'})

if __name__ == '__main__':
    app.run(debug=True)
