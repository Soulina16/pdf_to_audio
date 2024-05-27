import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import PyPDF2
from gtts import gTTS
import uvicorn

app = FastAPI()

@app.post("/pdf-to-audio/")
async def pdf_to_audio(file: UploadFile = File(...), language: str = 'en'):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    # Save the uploaded PDF file temporarily
    temp_pdf_path = "temp_uploaded.pdf"
    with open(temp_pdf_path, "wb") as temp_file:
        temp_file.write(file.file.read())
    
    # Extract text from PDF
    text = ""
    with open(temp_pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    
    if text:
        # Convert text to speech
        tts = gTTS(text=text, lang=language)
        audio_path = "output.mp3"
        tts.save(audio_path)

        # Clean up the temporary PDF file
        os.remove(temp_pdf_path)

        # Return the generated audio file
        return FileResponse(audio_path, media_type="audio/mpeg", filename="output.mp3")
    else:
        # Clean up the temporary PDF file
        os.remove(temp_pdf_path)
        raise HTTPException(status_code=400, detail="No text found in the PDF.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
