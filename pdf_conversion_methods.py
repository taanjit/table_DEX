import subprocess
import pdfplumber
import os
import streamlit as st

pdf_2_img_dir = './pdf_2_img'


def get_pdf_count(uploaded_file):
     with pdfplumber.open(uploaded_file) as pdf:
          return len(pdf.pages)


def plumber_pdf_to_jpg(uploaded_file, pages_to_show, image_paths):
    with pdfplumber.open(uploaded_file) as pdf:
         for page_num in pages_to_show:
             if page_num <= len(pdf.pages):
                image_name = f"page_{page_num}.png"
                output_file_path = os.path.join(pdf_2_img_dir, image_name)
                if not os.path.exists(output_file_path):
                    page = pdf.pages[page_num-1]  # pdfplumber uses 0-indexing for pages
                    image = page.to_image().original
                    image.save(output_file_path)
                image_paths.append(output_file_path)
             else:
                st.write(f"Page {page_num} is out of range.")

def gs_pdf_to_jpg(uploaded_file, pages_to_show, image_paths):
    # Save the uploaded file to a temporary location
    temp_pdf_path = "temp.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Get the total number of pages in the PDF
    total_pages = get_pdf_count(uploaded_file)
    for page_num in pages_to_show:
        if page_num <= total_pages:
            output_file_path = os.path.join(pdf_2_img_dir, f"page_{page_num:03d}.jpg")
            if not os.path.exists(output_file_path):
                gs_command = [
                    "gs",
                    "-dNOPAUSE",
                    "-dBATCH",
                    "-sDEVICE=jpeg",
                    "-r300",
                    "-dUseCropBox",
                    f"-dFirstPage={page_num}",
                    f"-dLastPage={page_num}",
                    f"-sOutputFile={output_file_path}",
                    temp_pdf_path
                ]
                try:
                    #running ghostscript
                    subprocess.run(gs_command, check=True)
                except subprocess.CalledProcessError:
                    st.write(f"Failed to convert {page_num} to image")  
            image_paths.append(output_file_path)
        else:
            st.write(f"Page {page_num} is out of range. The document has {total_pages} pages.")
             

# import module
# from pdf2image import convert_from_path


# # Store Pdf with convert_from_path function
# images = convert_from_path('./OneDrive_2024-08-22/1. INTEGRATED DESIGN/B17-B0034000-A-Final EEDI Technical File-S1940.pdf')
# print(images)
# for i in range(len(images)):

# 	# Save pages as images in the pdf
# 	images[i].save('./image/page'+ str(i) +'.jpg', 'JPEG')

# pdf_path = "./docs/HF27-LIFE BOAT.pdf"
# output_folder = "test_out_images"
# pages = [1, 3, 5, 7]  # List of pages you want to convert

# convert_pdf_to_jpg(pdf_path, output_folder, pages)
