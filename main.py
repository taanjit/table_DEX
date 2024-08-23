import glob
import os
import pdfplumber
from PIL import Image
from Table_detection import find_table
import numpy as np
import time



def read_pdf_files_from_subfolders(root_folder):
    pdf_files = []

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.pdf') or file.endswith('.PDF'):
                pdf_files.append(os.path.join(root, file))

    return pdf_files




def detect_table(root_folder):
    pdf_files = read_pdf_files_from_subfolders(root_folder)
    for pdf_file in pdf_files:
        # Process each PDF file here
        with pdfplumber.open(pdf_file) as pdf:
            # print(len(pdf.pages)) 
            file_path=pdf_file.split('/')[:-1]
            file_name=pdf_file.split('/')[-1]
            folder_name='out_folder/'+file_name.split('.')[0]
            os.makedirs(folder_name, exist_ok=True)
            for page_number in range(len(pdf.pages)):
                page = pdf.pages[page_number - 1]
                image = page.to_image()
                image.save("temp.png")
                image = "temp.png"
                # # print(image.shape())
                image_out=find_table(image)
                image_out.save(folder_name+f'/page_{page_number}.jpg')

if __name__ == "__main__":
    # Example usage:
    root_folder = "source_pdf"
    detect_table(root_folder)
    