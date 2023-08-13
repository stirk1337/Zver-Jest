import base64
import string
import subprocess
import random

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.responses import FileResponse

from egor_prikol import translate, whisper

from video_demo import process_video

app = FastAPI()

FILE_NAME = 'converted_xd.mp4'

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the directory where uploaded files will be stored
UPLOAD_DIR = ""


def convert_webm_to_mp4(input_path, output_path):
    # ffmpeg -fflags +genpts -i 1.webm -r 24 1.mp4
    try:
        subprocess.run(['ffmpeg', '-fflags', '+genpts', '-y', '-i', input_path, '-r', str(24), output_path])
        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


def convert_webm_to_mp3(input_path, output_path):
    # ffmpeg -fflags +genpts -i 1.webm -r 24 1.mp4
    command = [
        'ffmpeg',
        '-i', input_path,
        '-vn',  # Disable video processing
        '-acodec', 'libmp3lame',  # MP3 codec
        '-ab', '320k',  # Audio bitrate
        output_path
    ]
    try:
        #subprocess.run(['ffmpeg', '-fflags', '+genpts', '-y', '-i', input_path, output_path])
        subprocess.run(command)
        return True
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False


@app.get("/download_mp3/{file_name}")
async def download_mp3(file_name: str):
    file_path = os.path.join(UPLOAD_DIR, file_name)
    return FileResponse(file_path, media_type="audio/mpeg")


@app.post("/get_predict")
async def get_predict(file: UploadFile = File(...)):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        convert_webm_to_mp4(file_path, FILE_NAME)
        result = process_video(FILE_NAME, 'config.json', stride=30)


        return set(result)
        # return {"message": "File uploaded and saved successfully", "file_path": file_path}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload")
def upload(filename: str = Form(...), filedata: str = Form(...)):
    image_as_bytes = str.encode(filedata)  # convert string to bytes
    img_recovered = base64.b64decode(image_as_bytes)  # decode base64string
    try:
        with open(filename, "wb") as f:
            f.write(img_recovered)
    except Exception:
        return {"message": "There was an error uploading the file"}
    convert_webm_to_mp4(filename, FILE_NAME)
    result = process_video(FILE_NAME, 'config.json', stride=30)

    #result = ['я']

    print(result)
    if "nothing" in result:
        print('deleted net jesta')
        result.remove("nothing")

    print(result)
    if len(result) == 0:
        return 'Nothing, bro'
    result = set(result)
    result = ' '.join(result)
    print(result)

    # file_path = os.path.join(UPLOAD_DIR, random_str + '.mp3')
    additional_response, file_path = translate(result, filename)
    #additional_response = 'Я.'
    response_dict = {
        "audio_response": file_path,
        "additional_response": additional_response
    }

    return response_dict

"""
@app.post("/get_transcribe")
async def get_transcribe(filename: str = Form(...), filedata: str = Form(...)):
    image_as_bytes = str.encode(filedata)  # convert string to bytes
    img_recovered = base64.b64decode(image_as_bytes)  # decode base64string
    try:
        with open(filename, "wb") as f:
            f.write(img_recovered)
    except Exception:
        return {"message": "There was an error uploading the file"}
    convert_webm_to_mp3(filename, 'whisper.mp3')
    return whisper()
"""


@app.post("/get_transcribe")
async def get_transcribe(file: UploadFile = File(...)):
    os.makedirs('uploaded_files', exist_ok=True)
    file_path = os.path.join('uploaded_files', file.filename)
    print(file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    result = whisper()
    return result
