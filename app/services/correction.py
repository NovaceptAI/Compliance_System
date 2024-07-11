import os
import PyPDF2
import docx
import language_tool_python
from spellchecker import SpellChecker
from flask import Flask, request, jsonify

# Ensure JAVA_HOME is set within the script
os.environ['JAVA_HOME'] = 'C:\\Program Files\\Java\\jdk-11'
os.environ['PATH'] = os.environ['JAVA_HOME'] + '\\bin;' + os.environ['PATH']

app = Flask(__name__)


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def check_spelling(text):
    spell = SpellChecker()
    lines = text.split("\n")
    spelling_issues = []
    for line_num, line in enumerate(lines, start=1):
        misspelled_words = spell.unknown(line.split())
        for word in misspelled_words:
            spelling_issues.append({"line_number": line_num, "word": word})
    return spelling_issues


def check_grammar(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    return matches


def process_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

    spelling_issues = check_spelling(text)
    grammar_issues = check_grammar(text)

    return spelling_issues, grammar_issues


def file_correction(file_path):
    spelling_issues, grammar_issues = process_file(file_path)

    issues = {
        "spelling_issues": [],
        "grammar_issues": []
    }

    for issue in spelling_issues:
        issues["spelling_issues"].append({"line_number": issue["line_number"], "word": issue["word"]})

    for match in grammar_issues:
        grammar_issue = {
            "sentence": match.context,
            "issue": match.message,
            "suggestions": match.replacements[:5],  # Limit suggestions to 5
            "line_number": match.offsetInContext
            # Adding line number (approximate, since grammar tools usually don't provide exact line numbers)
        }
        issues["grammar_issues"].append(grammar_issue)

    return issues

