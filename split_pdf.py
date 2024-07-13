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
            words_with_pm = re.findall(r'\bPM\w+', text)  # Find all words starting with "PM"
            for word in words_with_pm:
                print(word)
            extracted_words_by_page.append(words_with_pm)
    return extracted_words_by_page

# Function to split PDF pages based on factory code
def split_pdf_pages(pdf_path, pages_by_factory):
    for factory_code, page_numbers in pages_by_factory.items():
        writer = PdfWriter()
        reader = PdfReader(pdf_path)

        for page_number in sorted(set(page_numbers)):  # Ensure unique and sorted page numbers
            writer.add_page(reader.pages[page_number])

        output_pdf_path = f"Merged_{factory_code}.pdf"
        with open(output_pdf_path, 'wb') as output_pdf:
            writer.write(output_pdf)
        print(f"Created PDF for factory {factory_code}: {output_pdf_path}")

# Read the CSV file to get the 資材品コード and 関東工場 values
def read_csv_file(csv_file_path):
    extracted_data = []
    try:
        with open(csv_file_path, 'r', encoding='shift-jis') as file:  # Try 'shift-jis' encoding
            reader = csv.DictReader(file)
            for row in reader:
                shizaihin_code = row.get('資材品コード', '')  # Extract data from the '資材品コード' column
                kanto_factory = row.get('関東工場', '')  # Extract data from the '関東工場' column
                extracted_data.append((shizaihin_code, kanto_factory))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return extracted_data

# Main script logic
if __name__ == "__main__":
    folder_path = "C:\\Users\\21332\\Desktop\\po_split_test"  # Folder path containing PDF files
    csv_file_path = "C:\\Users\\21332\\Desktop\\po_split_test\\shizaihin.csv"  # CSV file path

    # Read the CSV file to get the PM codes and factory codes
    csv_data = read_csv_file(csv_file_path)

    # Extract PM codes from all PDF files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            print(f"Processing file: {pdf_path}")
            extracted_words_by_page = extract_and_print_text(pdf_path)

            pages_by_factory = {}
            for shizaihin_code, kanto_factory in csv_data:
                for page_num, words_on_page in enumerate(extracted_words_by_page):
                    if shizaihin_code in words_on_page:
                        if kanto_factory not in pages_by_factory:
                            pages_by_factory[kanto_factory] = []
                        if page_num not in pages_by_factory[kanto_factory]:
                            pages_by_factory[kanto_factory].append(page_num)

            if pages_by_factory:
                split_pdf_pages(pdf_path, pages_by_factory)
            else:
                print("No pages were grouped by factory. Check the PM codes and CSV mappings.")
