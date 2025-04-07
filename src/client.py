import requests
import os
import base64

GENERAL_OCR = "http://192.168.14.141:8000/document/general"
DOCUMENT_OCR = "http://192.168.14.141:8000/domain-document"
DOMAIN_OCR = "https://ocr.edentns.ai/document/general"
HEADERS = {"Content-type" : "application/json"}


def base64_encode(filePath):
    with open(filePath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def general_ocr(img, URL):
    # img = "/mnt/hdd1/seungchan/aicenter-api/계약서 샘플 (1).pdf"
    base64_img = base64_encode(img)
    
    request = {
        "version": "string",
        "requestId": "string",
        "timestamp": 0,
        "images": [
            {
                "format": "png",
                "data": base64_img,
                "name" : "1.png",
                "option": {
                    "pageRange": []
                }
            }
        ],
        "details": "",
        "modelType": "UNIVERSAL"
    }
    
    response= requests.post(URL, headers=HEADERS, json=request)
    print(response.json())
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
    img = "/mnt/hdd/eden/aicenter-engine/src/merge_4.png"
    URL = DOMAIN_OCR
    general_ocr_result = general_ocr(img, URL)
    # document_ocr_result = document_ocr(img, URL)
    # response1 = requests.post(URL1, headers=HEADERS, json=request1)
    # print(response1)