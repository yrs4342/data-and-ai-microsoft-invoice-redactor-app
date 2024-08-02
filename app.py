from flask import Flask, request, render_template, send_file, redirect, url_for, session
import fitz  # PyMuPDF
import os
import convertapi

app = Flask(__name__)
app.secret_key ='your_secret_key'
# Configuration
app.config['UPLOAD_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['CONVERTAPI_SECRET'] = 'KzwI9rW3uucW5dLE'
app.config['LOGO_PATH'] = 'static/Logo.PNG'  # Path to your logo file

# Set the ConvertAPI secret key
convertapi.api_secret = app.config['CONVERTAPI_SECRET']

# Define keywords, their width adjustments, number of times to redact, pages to redact on, and colors
KEYWORDS = {
    # Your keywords here
    'Invoice Number': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Invoice Date': {'left_adjustment': 20, 'right_adjustment': 200, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'PO Number': {'left_adjustment': 20, 'right_adjustment': 200, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'PO Date': {'left_adjustment': 20, 'right_adjustment': 230, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'PO Box': {'left_adjustment': 10, 'right_adjustment': 90, 'times': 2, 'pages': [0, 1], 'color': (1, 1, 1)},
    'Sold To': {'left_adjustment': 10, 'right_adjustment': 90, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Bill To': {'left_adjustment': 10, 'right_adjustment': 90, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Alpha Data LLC': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Alpha': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'ATTN': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'Contact': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'Customer #': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'DUBAI,': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'UNIT': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'Phone': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'VAT #': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Due Date': {'left_adjustment': 5, 'right_adjustment': 210, 'times': 1, 'pages': [0], 'color': (1, 1, 0.8)},
    'Payment Terms: Net payment': {'left_adjustment': 5, 'right_adjustment': 10, 'times': 1, 'pages': [0], 'color': (1, 1, 0.8)},
    '60 days from invoice date': {'left_adjustment': 5, 'right_adjustment': 5, 'times': 1, 'pages': [0], 'color': (1, 1, 0.8)},
    'PAYMENT': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'A/C Name': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Bank Name': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Bank A/C': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Swiftcode': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Sort Code': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'IBAN No': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'VAT Reg No': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Email': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Payment should': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Do not': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Exchange rate': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'Currency': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'USD': {'left_adjustment': 20, 'right_adjustment': 280, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'Learn more': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'https://': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'For additional': {'left_adjustment': 20, 'right_adjustment': 380, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'Learn more about': {'left_adjustment': 20, 'right_adjustment': 180, 'times': 1, 'pages': [2,3], 'color': (1, 1, 1)},
    'Microsoft Ireland': {'left_adjustment': 50, 'right_adjustment': 450, 'times': 4, 'pages': [0, 1, 2, 3], 'color': (1, 1, 1)},
    '(Amount in EUR)': {'left_adjustment': 5, 'right_adjustment': 5, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'EUR': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    '0.00': {'left_adjustment': 5, 'right_adjustment': 45, 'times': 2, 'pages': [0], 'color': (1, 1, 1)},
    'VAT @0%':{'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Export of services':{'left_adjustment': 5, 'right_adjustment': 45, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Charges': {'left_adjustment': -40, 'right_adjustment': 400, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'LESS: Commitment Usage':{'left_adjustment': -100, 'right_adjustment': 300, 'times': 1, 'pages': [0], 'color': (1, 1, 1)},
    'Net Amount': {'left_adjustment': -50, 'right_adjustment': 300, 'times': 1, 'pages': [0], 'color': (1, 1, 1)}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    session.pop('uploaded', None)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = 'uploaded.pdf'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Perform redaction
        redacted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'redacted.pdf')
        redact_pdf(file_path, KEYWORDS, redacted_path)
        
        # Add logo to the redacted PDF
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_with_logo.pdf')
        add_logo_to_pdf(redacted_path, app.config['LOGO_PATH'], output_path)
        
        session['uploaded'] = True

        return redirect(url_for('result'))
    return redirect(request.url)

def redact_pdf(file_path, keywords, redacted_path):
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for keyword, properties in keywords.items():
            left_adjustment = properties['left_adjustment']
            right_adjustment = properties['right_adjustment']
            times = properties['times']
            pages = properties.get('pages', [])
            color = properties.get('color', (1, 1, 1))
            
            if page_num in pages:
                text_instances = page.search_for(keyword)
                for i, inst in enumerate(text_instances):
                    if i < times:
                        inst.x0 -= left_adjustment
                        inst.x1 += right_adjustment
                        page.add_redact_annot(inst, fill=color)
                # Apply all redactions after marking
                page.apply_redactions()
    doc.save(redacted_path)
    doc.close()

def add_logo_to_pdf(input_pdf_path, logo_path, output_pdf_path):
    doc = fitz.open(input_pdf_path)
    logo_img = fitz.open(logo_path)
    logo_pix = logo_img[0].get_pixmap()
    logo_width = logo_pix.width
    logo_height = logo_pix.height

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_rect = page.rect
        
        # Calculate the position for the logo (center bottom)
        x0 = (page_rect.width - logo_width) / 2  # Center horizontally
        y0 = page_rect.height - logo_height - 60  # Bottom with a 60-point margin

        # Insert the logo image into the page
        page.insert_image(
            fitz.Rect(x0, y0, x0 + logo_width, y0 + logo_height),
            stream=logo_pix.tobytes()
        )
    
    doc.save(output_pdf_path)
    doc.close()

@app.route('/download')
def download_file():
    return send_file('static/output_with_logo.pdf', as_attachment=True)

@app.route('/result')
def result():
    #Check if a file has been uploaded 
    if not session.get('uploaded'):
        return redirect(url_for('index'))
    #Render a result page or perform actions as needed
    return render_template('result.html', redacted_file=url_for('static', filename='output_with_logo.pdf'))
    
if __name__ == '__main__':
    app.run(debug=True)