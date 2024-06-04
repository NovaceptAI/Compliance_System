import os
import re
import PyPDF2
import docx
import cv2
import numpy as np

# Placeholder for predefined image hashes or patterns
predefined_hashes = {
    "icon1": np.array([123, 234, 345]),  # example hashes
    "logo1": np.array([456, 567, 678]),  # example hashes
    # Add more as needed
}


def extract_text_from_pdf(file_path):
    text = []
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            page_lines = page_text.splitlines()
            text.extend([(line, page_num + 1) for line in page_lines])
    return text


def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = [(paragraph.text, None) for paragraph in doc.paragraphs]
    return text


def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    text = [(line.strip(), None) for line in lines]
    return text


def check_flagged_phrases(text, flagged_phrases):
    issues = []
    for i, (line, page) in enumerate(text, start=1):
        for phrase in flagged_phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", line, re.IGNORECASE):
                if page:
                    issues.append(f"Page {page}, Line {i}: {phrase}")
                else:
                    issues.append(f"Line {i}: {phrase}")
    return issues


def process_text_file(file_path, flagged_phrases):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format")

    flagged_issues = check_flagged_phrases(text, flagged_phrases)
    return flagged_issues


def compute_image_hash(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")
    resized = cv2.resize(image, (32, 32), interpolation=cv2.INTER_AREA)
    return cv2.img_hash.blockMeanHash(resized)


def check_images_for_hashes(image_paths):
    issues = []
    # print ("I am Here")
    for image_path in image_paths:
        try:
            image_hash = compute_image_hash(image_path)
            for name, predefined_hash in predefined_hashes.items():
                if np.array_equal(image_hash, predefined_hash):
                    issues.append(f"Flagged Image: {name} in {image_path}")
        except ValueError as e:
            issues.append(str(e))
    return issues


def process_images(image_paths):
    return check_images_for_hashes(image_paths)


def file_verification(file_path, image_paths=None, flagged_phrases=None):
    # Text file processing
    text_issues = process_text_file(file_path, flagged_phrases)

    # Image file processing
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

    return all_issues


# Example usage
# if _name_ == "_main_":
#     file_path = "path/to/your/document.pdf"  # Change this to your file path
#     image_paths = ["path/to/your/image1.png", "path/to/your/image2.jpg"]  # Change this to your image paths
#     flagged_phrases = ["explicit phrase", "disclaimer", "unnecessary promise", "derogatory phrase"]
#
#     file_verification(file_path, image_paths, flagged_phrases)