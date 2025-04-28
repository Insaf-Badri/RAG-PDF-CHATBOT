from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/upload-pdf")

async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    
    # Save or process the file here
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)
    return JSONResponse(content={"message": "PDF uploaded successfully."})
