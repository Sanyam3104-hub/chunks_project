from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import pdfplumber
from typing import List
from sentence_transformers import SentenceTransformer

app = FastAPI()

UPLOAD_DIR = "uploads"
CHUNK_DIR = "chunks"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHUNK_DIR, exist_ok=True)

def extract_text_by_page(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return pages

def fixed_length_chunks(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]

def semantic_chunks(text):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = text.split(". ")
    embeddings = model.encode(sentences)  # placeholder use
    return sentences

@app.post("/upload_pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        if file.filename.endswith(".pdf"):
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            uploaded_files.append(file.filename)
    return {"status": "success", "uploaded_files": uploaded_files}

@app.post("/create_chunks/")
async def create_chunks():
    response = {}
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        pages = extract_text_by_page(file_path)
        full_text = " ".join(pages)

        chunks_by_technique = {
            "by_page": {f"chunk_{i+1}": page for i, page in enumerate(pages)},
            "fixed_length": {f"chunk_{i+1}": chunk for i, chunk in enumerate(fixed_length_chunks(full_text))},
            "semantic_chunking": {f"chunk_{i+1}": chunk for i, chunk in enumerate(semantic_chunks(full_text))}
        }

        # Save as JSON
        import json
        with open(os.path.join(CHUNK_DIR, f"{filename}.json"), "w") as f:
            json.dump(chunks_by_technique, f, indent=2)

        response[filename] = {"chunks_by_technique": chunks_by_technique}

    return JSONResponse(content=response)


