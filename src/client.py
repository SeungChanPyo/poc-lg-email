import requests
import os
import base64

URL1 = "http://192.168.14.141:8000/document/general"
URL2 = "http://192.168.14.141:8000/document/general/file"
HEADERS = {"Content-type" : "application/json"}


def base64_encode(filePath):
    with open(filePath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string



if __name__ == "__main__":
    img = "/mnt/hdd/eden/aicenter-engine/src/img_with_box6.jpg"
    base64_img = base64_encode(img)
    
    request1 = {
        "version": "string",
        "requestId": "string",
        "timestamp": 0,
        "images": [
            {
                "format": "jpg",
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
    
    response1 = requests.post(URL1, headers=HEADERS, json=request1)
    print(response1)