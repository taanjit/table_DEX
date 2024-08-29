from ultralyticsplus import YOLO, render_result
import os
from PIL import Image


def crop_and_save(image_path, bboxes, output_dir, confidence_threshold=0.4):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract original filename without extension
    original_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Open the image
    image = Image.open(image_path)
    
    # Loop over each bounding box and crop the image if the confidence is above the threshold
    cropped_images = []
    for i in range(bboxes.xyxy.shape[0]):  # Loop over the number of bounding boxes
        xmin, ymin, xmax, ymax = bboxes.xyxy[i].tolist()  # Extract bounding box coordinates
        confidence = bboxes.conf[i].item()  # Extract confidence score
        label = int(bboxes.cls[i].item())  # Extract class label # Extract bbox coordinates, confidence, and label
        
        # Only process the bounding box if the confidence is greater than the threshold
        if confidence > confidence_threshold:
            cropped_image = image.crop((xmin, ymin, xmax, ymax))
            
            # Save the cropped image with the format: originalfilename_labelname_i.png
            labelname = "bordered" if label == 1 else "borderless"  # Example label names
            cropped_image_path = os.path.join(output_dir, f"{original_filename}_{labelname}_{i}.png")
            cropped_image.save(cropped_image_path)
            cropped_images.append(cropped_image_path)
    
    return cropped_images


def find_table(image):
    # load model
    # model = YOLO('foduucom/table-detection-and-extraction')
    model = YOLO('./best.pt')

    # set model parameters
    model.overrides['conf'] = 0.25  # NMS confidence threshold
    model.overrides['iou'] = 0.45  # NMS IoU threshold
    model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    model.overrides['max_det'] = 1000  # maximum number of detections per image



    # perform inference
    results = model.predict(image)

    # observe results
    bbox_tensor = results[0].boxes
    print(bbox_tensor)
    # Crop images and save them
    cropped_image_paths = crop_and_save(image, bbox_tensor, './cropped_img')
    render = render_result(model=model, image=image, result=results[0])
    # render.show()
    return render, cropped_image_paths


if __name__ == "__main__":
    # set image
    image = 'a.jpg'
    image_out=find_table(image)
    image_out.save("out.png")