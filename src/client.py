import requests
import os
import base64

GENERAL_OCR = "http://192.168.14.141:8000/document/general"
DOCUMENT_OCR = "http://192.168.14.141:8000/domain-document"
TABLE_OCR = "http://192.168.14.141:8000/document/table"
BIZ_CARD_OCR = "http://192.168.14.141:8000/document/biz-card"
BIZ_LICENSE_OCR = "http://192.168.14.141:8000/document/biz-license"
ID_CARD_OCR = "http://192.168.14.141:8000/document/id-card"

DOMAIN_OCR = "https://ocr.edentns.ai/document/general"
DOMAIN_TABLE_OCR = "https://ocr.edentns.ai/document/table"
DOMAIN_DOCUMENT_OCR = "https://ocr.edentns.ai/domain-document"
DOMAIN_BIZ_CARD_OCR = "https://ocr.edentns.ai/document/biz-card"
DOMAIN_BIZ_LICENSE_OCR = "https://ocr.edentns.ai/document/biz-license"
DOMAIN_ID_CARD_OCR = "https://ocr.edentns.ai/document/id-card"

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
                "format": "pdf",
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

def table_ocr(img, URL):
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
                "tableOption": [
                    {
                    "pageRange": [
                    ],
                    "tableClue": [
                    ]
                }
                ]
            }
        ],
        "details": "linemode=true",
    }
    response = requests.post(URL, headers=HEADERS, json=request)
    print(response.json())
    return response

def document_ocr(img, URL):
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
    response = requests.post(URL, headers=HEADERS, params=PARAMS, json=request)
    print(response.json())
    return response

def biz_license_ocr(img, URL):
    base64_img = base64_encode(img)
    request = {
        "version": "v2",
        "requestId": "string",
        "timestamp": 0,
        "images": [
            {
                "format": "png",
                "data": base64_img,
                "name" : "1.png",
            }
        ],
        "ocrType" : "EDEN",
        "details": "",
        "recognitionId" : 0,
        "templateName" : "string",
        "modelType": "UNIVERSAL"
    }
    response = requests.post(URL, headers=HEADERS, json=request)
    print(response.json())
    return response

def biz_card_ocr(img, URL):
    base64_img = base64_encode(img)
    request = {
        "version": "v2",
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
    response = requests.post(URL, headers=HEADERS, json=request)
    print(response.json())
    return response

def id_card_ocr(img, URL):
    base64_img = base64_encode(img)
    request = {
        "version": "v2",
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
    response = requests.post(URL, headers=HEADERS, json=request)
    print(response.json())
    return response
    

if __name__ == "__main__":
    # img = "/mnt/hdd1/seungchan/aicenter-api/계약서 샘플 (1).pdf"
    img = "/mnt/hdd1/seungchan/aicenter-api/(조앤컴퍼니스)사업자등록증.png"
    URL1 = DOMAIN_OCR
    URL2 = TABLE_OCR
    URL3 = DOMAIN_DOCUMENT_OCR
    # general_ocr_result = general_ocr(img, URL1)
    # table_ocr_result = table_ocr(img, URL2)
    # document_ocr_result = document_ocr(img, URL3)
    biz_license_ocr_result = biz_license_ocr(img, BIZ_LICENSE_OCR)
    # response1 = requests.post(URL1, headers=HEADERS, json=request1)
    # print(response1)