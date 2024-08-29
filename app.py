import streamlit as st
import pdfplumber
import os 
import shutil
from Table_detection import find_table
from natsort import natsorted
import requests
import pandas as pd
import io
from pdf_conversion_methods import plumber_pdf_to_jpg, gs_pdf_to_jpg

def create_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def parse_page_numbers(page_input):
    pages = set()
    for part in page_input.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end +1))
        else:
            pages.add(int(part))
    return sorted(pages)


if 'image_index' not in st.session_state:
    st.session_state.image_index = 0
if 'detection_done' not in st.session_state:
    st.session_state.detection_done = False

# Function to change the image index
def change_image(index_change):
    st.session_state.image_index += index_change
    # Ensure the index is within bounds
    if st.session_state.image_index < 0:
        st.session_state.image_index = 0
    elif st.session_state.image_index >= len(processed_paths):
        st.session_state.image_index = len(processed_paths) - 1
    st.rerun()

def clear_images():
    for org_file in os.listdir(pdf_2_img_dir):
        org_file_path = os.path.join(pdf_2_img_dir, org_file)
        os.remove(org_file_path)
    for det_file in os.listdir(detection_dir):
        det_file_path = os.path.join(detection_dir, det_file)
        os.remove(det_file_path)
    for crp_file in os.listdir(cropped_dir):
        crp_file_path = os.path.join(cropped_dir, crp_file)
        os.remove(crp_file_path)
    st.session_state.image_index = 0


pdf_2_img_dir = './pdf_2_img'
detection_dir = './det_dir'
cropped_dir = './cropped_img'
create_dir(pdf_2_img_dir)
create_dir(detection_dir)
create_dir(cropped_dir)


st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Navigate to", ["Table Detection", "Table Crop and Extraction", "Clear Images"])

if page == "Table Detection":
    st.title("PDF Table Detection")
    st.sidebar.title("PDF Page Selector")
    uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
    page_input = st.sidebar.text_input("Enter page numbers (e.g., 1-5, 7, 9, 10-12, 15)")

    if uploaded_file and page_input:
        if st.session_state.get('last_uploaded_file') != uploaded_file:
            clear_images()
            st.session_state.last_uploaded_file = uploaded_file
        pages_to_show = parse_page_numbers(page_input)
        image_paths = []
        processed_paths =[]
        plumber_pdf_to_jpg(uploaded_file, pages_to_show, image_paths)
        # gs_pdf_to_jpg(uploaded_file, pages_to_show, image_paths)


        # with pdfplumber.open(uploaded_file) as pdf:
        #     for page_num in pages_to_show:
        #         if page_num <= len(pdf.pages):
        #             page = pdf.pages[page_num-1]  # pdfplumber uses 0-indexing for pages
        #             image = page.to_image().original

        #             image_name = f"page_{page_num}.png"
        #             image_path = os.path.join(pdf_2_img_dir, image_name)
        #             image.save(image_path)
        #             image_paths.append(image_path)
        #         else:
        #             st.write(f"Page {page_num} is out of range.")


        progress_bar = st.progress(0)
        total_images = len(list(os.listdir(pdf_2_img_dir)))

        for index, file in enumerate(os.listdir(pdf_2_img_dir)):
            source_path = os.path.join(pdf_2_img_dir, file)
            processed_path = os.path.join(detection_dir, file)
            if not os.path.exists(processed_path):
                detect_table, cropped_paths = find_table(source_path)
                detect_table.save(processed_path)
            if processed_path not in processed_paths:
                processed_paths.append(processed_path)
            progress_bar.progress((index + 1) / total_images)

        processed_paths = natsorted(processed_paths)
        print(processed_paths)
        print(pages_to_show)
        if processed_paths:
            st.image(processed_paths[st.session_state.image_index], f"Processed Page {pages_to_show[st.session_state.image_index]}", use_column_width=True)
            # Navigation buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Back"):
                    change_image(-1)
            with col2:
                if st.button("Next"):
                    change_image(1)   
                
            # Set detection as done
            st.session_state.detection_done = True


if page == "Table Crop and Extraction":
    if st.session_state.detection_done:
        st.title("Table Crop and Extraction")
        
        # Display cropped images as tiles
        cropped_images = [os.path.join(cropped_dir, file) for file in os.listdir(cropped_dir)]
        prompt = st.sidebar.text_input("Enter your prompt", 'convert the  table content into csv')
        for i, image_path in enumerate(cropped_images):
            st.image(image_path, caption=f"Cropped Image {i+1}", use_column_width=True)
            if st.button(f"Process Cropped Image {i+1}") and prompt:
                with open(image_path, 'rb') as img_file:
                    files = {'question':prompt, 'file': img_file}
                    print(prompt)
                    #api endpoint
                    api_url = "http://192.168.95.242:8888/convert-table/"
                    response = requests.post(api_url, files=files)
                    if response.status_code == 200:
                        st.success(f"Image {i+1} processed successfully!")
                        csv_data = response.json()['csv']
                        print(csv_data)
                        if csv_data.strip():
                            try:
                                df = pd.read_csv(io.StringIO(csv_data.strip()), skipinitialspace=True, on_bad_lines='warn')

                                # Display the DataFrame in Streamlit
                                st.dataframe(df)

                                # Provide a button to download the DataFrame as a CSV file
                                csv_download = df.to_csv(index=False).encode('utf-8')
                                st.download_button(
                                    label="Download as CSV",
                                    data=csv_download,
                                    file_name='output.csv',
                                    mime='text/csv',
                                )
                            except pd.errors.ParserError as e:
                                st.error(f"Error parsing CSV: {e}")
                                print(f"Error parsing CSV: {e}")
                        else:
                            st.error("CSV data is empty or invalid")

                    else:
                        st.error(f"Failed to process Image {i+1}. Error: {response.text}")




    else:
        st.write("Please detect the table first.")
        # Clean up saved images after app is closed
    

if page == "Clear Images":
    clear_images()
    st.write("Images cleared.")
    

