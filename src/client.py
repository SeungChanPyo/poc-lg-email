import requests
import os
import base64

GENERAL_OCR = "http://192.168.14.141:8000/document/general"
DOCUMENT_OCR = "http://192.168.14.141:8000/domain-document"
URL2 = "http://192.168.14.141:8000/document/general/file"
HEADERS = {"Content-type" : "application/json"}


def base64_encode(filePath):
    with open(filePath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def general_ocr(img):
    img = "/mnt/hdd1/seungchan/aicenter-api/계약서 샘플 (1).pdf"
    base64_img = base64_encode(img)
    
    request = {
        "version": "string",
        "requestId": "string",
        "timestamp": 0,
        "images": [
            {
                "format": "pdf",
                "data": base64_img,
                "name" : "1.png",
                "option": {
                    "pageRange": [3]
                }
            }
        ],
        "details": "",
        "modelType": "UNIVERSAL"
    }
    
    response= requests.post(GENERAL_OCR, headers=HEADERS, json=request)
    return response

def document_ocr(img):
    base64_img = base64_encode(img)
    request = {
        "version": "v4",
        "requestId": "string",
        "timestamp": 0,
        "images": [
            {
                "format": "pdf",
                "data": base64_img,
                "name" : "1.png",
            }
        ],
        "ocrType" : "string",
        "details": "",
        "recognitionId" : 0,
        "templateName" : "string",
        "modelType": "UNIVERSAL"
    }
    PARAMS = {
        "domainId": 1131,
        "templateId": 60000549,
        "ocrType": "EDEN"
    }
    response = requests.post(DOCUMENT_OCR, headers=HEADERS, params=PARAMS, json=request)
    return response

if __name__ == "__main__":
    img = "/mnt/hdd1/seungchan/aicenter-api/extracted_page.pdf"

    # general_ocr_result = general_ocr(img)
    document_ocr_result = document_ocr(img)
    # response1 = requests.post(URL1, headers=HEADERS, json=request1)
    # print(response1)