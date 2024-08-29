# installations have not done, done this part in gpu
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
import io
import csv

app = FastAPI()

model = AutoModel.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5-int4', trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained('openbmb/MiniCPM-Llama3-V-2_5-int4', trust_remote_code=True)
model.eval()

def convert_to_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Assuming data is a dict with 'header' and 'rows'
    if isinstance(data, dict):
        header = data.get('header', [])
        rows = data.get('rows', [])
        writer.writerow(header)
        writer.writerows(rows)
    else:
        # If the data is not in the expected format, just return it as is.
        output.write(str(data))
    
    return output.getvalue()

@app.post("/convert-table/")
async def convert_table(file: UploadFile = File(...), question: str = 'convert the all table content into csv'):
    image = Image.open(io.BytesIO(await file.read())).convert('RGB')
    
    msgs = [{'role': 'user', 'content': question}]
    res = model.chat(
        image=image,
        msgs=msgs,
        tokenizer=tokenizer,
        sampling=True,
        temperature=0.7,
    )
    
    # Log or print res to see its structure
    print("Model Response:", res)

    csv_data = convert_to_csv(res)
    
    return JSONResponse(content={"csv": csv_data})

# To run the FastAPI server, use: uvicorn test:app --reload

# To run the FastAPI server, use: uvicorn test:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)