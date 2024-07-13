# app/routes/document_routes.py

from flask import Blueprint, request, jsonify, json
from app.services import correction, verification, compliance
import PyPDF2
# import boto3
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
    # Check if the main document is sent via a form with the name 'document'
    main_file = request.files.get('document')
    if main_file:
        # Replace spaces in the file name with underscores
        main_filename = main_file.filename.replace(" ", "_")

        # Save the main file temporarily with the modified file name
        main_filepath = os.path.join('app/tmp', main_filename)
        main_file.save(main_filepath)
    else:
        return jsonify({'message': 'Main document upload failed'}), 200

    # Check if the rule document is sent via a form with the name 'rule_document'
    rule_file = request.files.get('rule_document')
    if rule_file:
        # Replace spaces in the file name with underscores
        rule_filename = rule_file.filename.replace(" ", "_")

        # Save the rule file under the rule_book folder with the modified file name
        rule_filepath = os.path.join('app/rule_book', rule_filename)
        rule_file.save(rule_filepath)

        return jsonify({
            'message': 'Documents uploaded successfully',
            'main_filename': main_filename,
            'main_path': main_filepath,
            'rule_filename': rule_filename,
            'rule_path': rule_filepath
        }), 200
    else:
        return jsonify({
            'message': 'Process Document uploaded successfully. No Rule File Added',
            'main_filename': main_filename,
            'main_path': main_filepath
        }), 200


@document_blueprint.route('/analyze', methods=['POST'])
def analyze_document():
    # This endpoint could be used to perform various analyses on the document
    # For simplicity, let's assume the document's path is sent in JSON format
    data = request.get_json()
    document_path = data.get('document_path')

    # Check if the document path is valid
    if not os.path.exists(document_path):
        return jsonify({'message': 'Document Not Found. Please re-upload'}), 404

    feature = data.get('feature')
    # Perform various analyses
    if feature == "Correction":
        corrections = correction.file_correction(document_path)
        return corrections

    # Perform various analyses
    elif feature == "Verification":
        image_path = data.get('image_path')
        flagged_phrases = data.get('flagged_phrases')
        verifications = verification.file_verification(document_path, image_path, flagged_phrases)
        return jsonify(verifications)

    # Perform various analyses
    elif feature == "Compliance":
        rules_filepath = "app/rules2.xlsx"
        # Load rules
        rules = compliance.load_rules_from_tabs(rules_filepath)
        text = compliance.extract_text_from_pdf(document_path)
        flagged_phrases = compliance.flag_triggers_in_text(text, rules)
        return jsonify({'flagged_phrases': flagged_phrases})

    else:
        return "Feature Not Available"


@document_blueprint.route('/status', methods=['POST'])
def app_status():
    return "Working Absolutely Fine"
# Additional routes can be added here for other functionalities


@document_blueprint.route('/count', methods=['POST'])
def count():
    data = request.get_json()
    file_path = data.get('file_path')

    spelling_issues, grammar_issues = correction.process_file(file_path)

    count_data = {
        "spelling_mistakes_count": len(spelling_issues),
        "grammar_issues_count": len(grammar_issues),
        "suggestions_count": sum(len(match.replacements[:5]) for match in grammar_issues)
    }
    return jsonify(count_data)
