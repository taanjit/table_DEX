# Table Detection

## Installation
```sh
  pip install -r requirements.txt
```
## Streamlit application
Run streamlit command
```sh
  streamlit run app.py
```
Navigate through pages "Table Detection", "Table Crop and Extraction", and "Clear Images".<br>

__"Table Detection"__ page : Browse your pdf file, Enter the pages you need the detection process to take place, Press Enter.
A progress bar shows the progress and then the detected images are displayed. You can navigate using the "Next" and "Back" buttons.
In Table_detection.py you can change the threshold, default= 0.4 in the function def crop_and_save(image_path, bboxes, output_dir, confidence_threshold=0.4):<br>

__"Table Crop and Extraction"__ page: You can go to this page only after doing the detection portion. Here all the detected results is shown as cropped tables as tiles, Scroll down to view all your cropped results. Under each image you can see "Process Cropped Image" button, Clickit. You will get table data, and an option to download to csv.

Currently for extraction purpose __openbmb/MiniCPM-Llama3-V-2_5-int4__ model is being used.
More preprocessing steps need to be done.


