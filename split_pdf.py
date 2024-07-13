import os
import csv
import pdfplumber
import pytesseract
import re  # 追加
from PyPDF2 import PdfReader, PdfWriter

# Function to extract and print text from a PDF file
def extract_and_print_text(pdf_path):
    extracted_words_by_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            im = page.to_image(resolution=300)  # Enhance resolution
            text = pytesseract.image_to_string(im.original, lang='jpn')  # Perform OCR for Japanese text
            text = text.replace('O', '0')  # Replace letter 'O' with number '0'
            print(f"--- Page {page_number + 1} of {os.path.basename(pdf_path)} ---")
            words_you_select = re.findall(r'\b\w+', text)  # change the atribute of re.findall() to the words your want to extract from the PDF file
            for word in words_you_select:
                print(word)
            extracted_words_by_page.append(words_you_select)
    return extracted_words_by_page

# Function to split PDF pages based on factory code
def split_pdf_pages(pdf_path, pages_by_group):
    for group_num, page_numbers in pages_by_group.items():
        writer = PdfWriter()
        reader = PdfReader(pdf_path)

        for page_number in sorted(set(page_numbers)):  # Ensure unique and sorted page numbers
            writer.add_page(reader.pages[page_number])

        output_pdf_path = f"Merged_{group_num}.pdf"
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        print(f"Created PDF for factory {group_num}: {output_pdf_path}")

# Read the CSV file to get the row a and row b values
def read_csv_file(csv_file_path):
    extracted_data = []
    try:
        with open(csv_file_path, 'r', encoding='shift-jis') as file:  # Try 'shift-jis' encoding
            reader = csv.DictReader(file)
            for row in reader:
                row_a = row.get('row_a', '')  # Extract data from the 'row a' column
                row_b = row.get('row_b', '')  # Extract data from the 'row b' column
                extracted_data.append((row_a, row_b))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return extracted_data

# Main script logic
if __name__ == "__main__":
    folder_path = ""  # Folder path = Location of the folder containing PDF files, search the "Location" from properties,To access the properties of a file or folder, right-click on it and select Properties.
    csv_file_path = ""  # CSV file path = Location of the CSV file, search the "Location" from properties,To access the properties of a file or folder, right-click on it and select Properties.

    # Read the CSV file to get the selected words and group
    csv_data = read_csv_file(csv_file_path)

    # Extract selected words from all PDF files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing file: {pdf_path}")
            extracted_words_by_page = extract_and_print_text(pdf_path)

            pages_by_group = {}
            for row_a, row_b in csv_data:
                for page_num, words_on_page in enumerate(extracted_words_by_page):
                    if row_a in words_on_page:
                        if row_b not in pages_by_group:
                            pages_by_group[row_b] = []
                        if page_num not in pages_by_group[row_b]:
                            pages_by_group[row_b].append(page_num)

            if pages_by_group:
                split_pdf_pages(pdf_path, pages_by_group)
            else:
                print("No pages were grouped by factory. Check the selected words and CSV mappings.")
