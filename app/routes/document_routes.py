# app/routes/document_routes.py

from flask import Blueprint, request, jsonify, json
from app.services import correction, verification
import PyPDF2

# Create a Blueprint for document-related routes
document_blueprint = Blueprint('documents', __name__)


@document_blueprint.route('/upload', methods=['POST'])
def upload_document():
    # Assume the document is sent via a form with the name 'document'
    file = request.files.get('document')
    if not file:
        return jsonify({'error': 'No document uploaded'}), 400

    # Replace spaces in the file name with underscores
    new_filename = file.filename.replace(" ", "_")

    # Process the document here (e.g., save it, analyze it)
    # For demonstration, let's assume we save it temporarily with the modified file name
    filepath = 'app/tmp/' + new_filename
    file.save(filepath)

    return jsonify({'message': 'Document uploaded successfully', 'filename': file.filename, 'path': filepath}), 200


@document_blueprint.route('/analyze', methods=['POST'])
def analyze_document():
    # This endpoint could be used to perform various analyses on the document
    # For simplicity, let's assume the document's path is sent in JSON format
    data = request.get_json()
    document_path = data.get('document_path')
    feature = data.get('feature')
    # Perform various analyses
    if feature == "Correction":
        corrections = correction.file_correction(document_path)
        my_set_as_list = list(corrections)
        json_data = json.dumps(my_set_as_list)
        return(json_data)

    # Perform various analyses
    elif feature == "Verification":
        verifications = verification.file_verification(document_path)
        return jsonify(correction)

    else:
        return "Feature Not Available"


@document_blueprint.route('/status', methods=['POST'])
def app_status():
    return "Working Absolutely Fine"
# Additional routes can be added here for other functionalities
