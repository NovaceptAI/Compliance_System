# app/routes/document_routes.py

from flask import Blueprint, request, jsonify, json
from app.services import correction, verification
import PyPDF2
import boto3
import os
import requests
# Create a Blueprint for document-related routes
document_blueprint = Blueprint('documents', __name__)


def download_file_from_s3(s3_url, local_path):
    response = requests.get(s3_url, stream=True)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    else:
        raise ValueError(f"Unable to download file from S3. Status code: {response.status_code}")

@document_blueprint.route('/upload', methods=['POST'])
def upload_document():
    # Check if the document is sent via a form with the name 'document'
    file = request.files.get('document')
    if not file:
        # Check if the document path is sent via JSON
        data = request.get_json()
        s3_url = data.get('s3_url')
        if not s3_url:
            return jsonify({'error': 'No document uploaded or S3 URL provided'}), 400

        # Extract the filename from the S3 URL
        new_filename = os.path.basename(s3_url).replace(" ", "_")
        filepath = os.path.join('app/tmp', new_filename)

        # Download the file from the S3 URL
        try:
            download_file_from_s3(s3_url, filepath)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        # Replace spaces in the file name with underscores
        new_filename = file.filename.replace(" ", "_")

        # Save the file temporarily with the modified file name
        filepath = os.path.join('app/tmp', new_filename)
        file.save(filepath)

    return jsonify({'message': 'Document uploaded successfully', 'filename': new_filename, 'path': filepath}), 200


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
        return json_data

    # Perform various analyses
    elif feature == "Verification":
        feature = data.get('feature')
        image_path = data.get('image_path')
        flagged_phrases = data.get('flagged_phrases')
        verifications = verification.file_verification(document_path, image_path, flagged_phrases)
        return jsonify(verifications)

    else:
        return "Feature Not Available"


@document_blueprint.route('/status', methods=['POST'])
def app_status():
    return "Working Absolutely Fine"
# Additional routes can be added here for other functionalities
