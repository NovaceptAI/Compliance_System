import os
import pandas as pd
import PyPDF2
from flask import Blueprint, request, jsonify, Flask

document_blueprint = Blueprint('document', __name__)


# Function to load the specified rules from the Excel file
def load_rules_from_tabs(excel_path):
    try:
        excel_data = pd.ExcelFile(excel_path)
        sheet_names = excel_data.sheet_names
        print("Sheet names:", sheet_names)  # Debugging: List all sheet names

        rules = {}

        # Check if each sheet exists before reading it
        if 'Disclaimers' in sheet_names:
            rules['Disclaimers'] = excel_data.parse('Disclaimers')[['Examples of Triggers']]
        else:
            print("Sheet 'Disclaimers' not found.")

        if 'Misleading Claims' in sheet_names:
            rules['Misleading Claims'] = excel_data.parse('Misleading Claims')[['Example Trigger Language']]
        else:
            print("Sheet 'Misleading Claims' not found.")

        if 'OffersCompetitions' in sheet_names:
            rules['OffersCompetitions'] = excel_data.parse('OffersCompetitions')[['Example Trigger']]
        else:
            print("Sheet 'OffersCompetitions' not found.")

        return rules
    except Exception as e:
        print(f"Error loading rules from Excel file: {e}")
        return None


# Extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text


# Function to flag triggers in text based on rules
def flag_triggers_in_text(text, rules):
    flagged_phrases = []

    # Flag triggers from 'Disclaimers'
    for trigger in rules['Disclaimers']['Examples of Triggers'].dropna():
        if trigger.lower() in text.lower():
            flagged_phrases.append(f"Trigger: {trigger} (Disclaimers)")

    # Flag triggers from 'Misleading Claims'
    for trigger in rules['Misleading Claims']['Example Trigger Language'].dropna():
        if trigger.lower() in text.lower():
            flagged_phrases.append(f"Trigger: {trigger} (Misleading Claims)")

    # Flag triggers from 'Offers Competitions'
    for trigger in rules['OffersCompetitions']['Example Trigger'].dropna():
        if trigger.lower() in text.lower():
            flagged_phrases.append(f"Trigger: {trigger} (Offers Competitions)")

    return flagged_phrases

