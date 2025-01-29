from fastapi import FastAPI, UploadFile, File, Form, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import uvicorn
import io
import uuid
from typing import List, Optional, Union
import os
from FormExtractor.preprocessing_main import *
from FormExtractor.id_extractionn import *
from main_extractor import main_executor
app = FastAPI()



# Define your static API key (store it securely in production)
STATIC_API_KEY = "C0Fb9Dsj1SBYHgQDYBYPYshKvj4o8NAPN4DFqVcrSYQ"
API_KEY_NAME = "x-api-key"  # The header name for the API key
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)




# Function to validate the API key
async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key == STATIC_API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )




# Utility function to save uploaded files
def read_pdf(file: UploadFile) -> str:
    file_location = f"{uuid.uuid1()}.pdf"
    with open(file_location, "wb+") as file_object:
        while content := file.file.read(1024):  # Read in chunks
            file_object.write(content)
    return file_location


# Utility function to save uploaded files
def read_id_pdf(file: UploadFile,extension) -> str:
    file_location = f"{uuid.uuid1()}."+extension
    # Write the uploaded file in binary mode
    with open(file_location, "wb") as file_object:
        while content := file.file.read(1024):  # Read in chunks
            file_object.write(content)
    return file_location





@app.post("/uploadfile/")
async def upload_file(
    name: Union[str, None] = Form(None),
    dob: Union[str, None] = Form(None),
    address: Union[str, None] = Form(None),
    id_proof: Optional[UploadFile] = File(None),
    uploadfiles: List[Union[UploadFile, None]] = File(None),
    user_type: Union[str, None] = Form(None),
    income_type: Union[str, None] = Form(None),
    business_name: Optional[str] = Form(None),
    cdr_number: Optional[int] = Form(None),
    document_types: Union[list, None] = Form(None),
    certification: Optional[UploadFile] = File(None),
    aggrement: Optional[UploadFile] = File(None),
    pi_key: str = Security(validate_api_key),  # API key dependency
     ):


    document_types= document_types.split(',')
    files_list = []
    # result = {}

    # Process uploaded files
    if uploadfiles:
        for file in uploadfiles:
            if file.filename:
                file_location = read_pdf(file)
                files_list.append(file_location)

    # Handle id_proof if provided
    if id_proof and id_proof.filename:
        extension=id_proof.filename.split('.')[-1]
        id_file = read_id_pdf(id_proof,extension)
        id_status=id_mapping(id_file,name,dob,extension)
        #result = {str(id_status)}
        os.remove(id_file)

    else:
        id_file = None
        result = {"No ID Proof uploaded"}

    cfo_location=''
    aggrement_location=''

    if user_type.strip().lower() == 'business' or user_type.strip().lower() == 'entity':
        if certification:
            if certification.filename:
                cfo_location = read_pdf(certification)

        if  aggrement:
            if aggrement.filename:
                aggrement_location = read_pdf(aggrement)




    # # Call the main logic if no errors
    if id_status:
        try:
            result = main_executor(name,dob,address, user_type, income_type, cdr_number, files_list,document_types,business_name,cfo_location,aggrement_location)
            # result={"status": "Pass"}
        except Exception as e:
            print(e)
            result = {"Error": "Error while parsing your documents"}

    else:
        result='Please check your id'



    if files_list:
        for file in files_list:
            os.remove(file)


    # Cleanup uploaded files
    # for file in files_list:
    #     os.remove(file)

    return result



# Run the FastAPI application
if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app, host="0.0.0.0", port=8000)
