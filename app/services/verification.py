import os
import re
import PyPDF2
import docx
import cv2
import numpy as np

# Initial list of phrases/words to be flagged
flagged_phrases = [
    "explicit phrase",
    "disclaimer",
    "unnecessary promise",
    "derogatory phrase"
]

# Placeholder for predefined image hashes or patterns
predefined_hashes = {
    "icon1": np.array([123, 234, 345]),  # example hashes
    "logo1": np.array([456, 567, 678]),  # example hashes
    # Add more as needed
}


# Function to add new phrases/words to be flagged
def add_flagged_phrase(phrase):
    flagged_phrases.append(phrase)


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfFileReader(file)
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def check_flagged_phrases(text):
    issues = []
    for phrase in flagged_phrases:
        if re.search(rf"\b{re.escape(phrase)}\b", text, re.IGNORECASE):
            issues.append(phrase)
    return issues


def process_text_file(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

    flagged_issues = check_flagged_phrases(text)
    return flagged_issues


def compute_image_hash(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    return cv2.img_hash.blockMeanHash(resized)


def check_images_for_hashes(image_paths):
    issues = []
    for image_path in image_paths:
        image_hash = compute_image_hash(image_path)
        for name, predefined_hash in predefined_hashes.items():
            if np.array_equal(image_hash, predefined_hash):
                issues.append(f"Flagged Image: {name} in {image_path}")
    return issues


def process_images(image_paths):
    return check_images_for_hashes(image_paths)


def verification():
    # Text file processing
    file_path = input("Enter the path to the text file (PDF, DOCX, TXT): ")
    text_issues = process_text_file(file_path)

    # Image file processing
    image_paths = input("Enter the paths to the images, separated by commas: ").split(',')
    image_issues = process_images(image_paths)

    # Combined issues
    all_issues = {
        "Text Issues": text_issues,
        "Image Issues": image_issues
    }

    # Display results
    if all_issues["Text Issues"]:
        print("\nText Issues:")
        for issue in all_issues["Text Issues"]:
            print(issue)
    else:
        print("No text issues found.")

    if all_issues["Image Issues"]:
        print("\nImage Issues:")
        for issue in all_issues["Image Issues"]:
            print(issue)
    else:
        print("No image issues found.")
