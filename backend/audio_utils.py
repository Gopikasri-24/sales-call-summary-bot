import os

UPLOAD_FOLDER = "uploads"

def save_uploaded_file(upload_file):
    # Create the uploads folder if it doesn't exist yet
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    file_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)

    # Save the file from FastAPI to our local disk
    with open(file_path, "wb") as file:
        file.write(upload_file.file.read())

    return file_path