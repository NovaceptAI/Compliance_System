import os
import PyPDF2
import docx
import language_tool_python
from spellchecker import SpellChecker


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            # page = reader.getPage(page_num)
            text += page_text + "\n"
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
    misspelled_words = spell.unknown(text.split())
    return misspelled_words


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


def file_correction():
    file_path = input("Enter the path to the file: ")
    spelling_issues, grammar_issues = process_file(file_path)

    print("\nSpelling Issues:")
    for word in spelling_issues:
        print(word)

    print("\nGrammar Issues:")
    for match in grammar_issues:
        print(f"Sentence: {match.context}")
        print(f"Issue: {match.message}")
        print(f"Suggestions: {', '.join(match.replacements)}")
        print()

# if _name_ == "_main_":
#     main()
