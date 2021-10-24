import cv2
import imutils
import numpy as np
import argparse
from urllib.request import urlopen

#https://data-flair.training/blogs/python-project-real-time-human-detection-counting/
HOGCV = cv2.HOGDescriptor()
HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
    resp = urlopen(url) #https://newbedev.com/how-can-i-read-an-image-from-an-internet-url-in-python-cv2-scikit-image-and-mahotas
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, readFlag)
    return image

def detect(frame):
    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(frame, winStride = (4, 4), padding = (8, 8), scale = 1.03)
    person = 0
    
    for x,y,w,h in bounding_box_cordinates:
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(frame, f'person {person}', (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
        person += 1

    
    cv2.putText(frame, 'Status : Detecting ', (40,40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
    cv2.putText(frame, f'Total Persons : {person}', (40,70), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255,0,0), 2)
    cv2.imshow('output', frame)
    return person

def humanDetector(args):
    return detectByPathImage(args, None)




def detectByPathImage(path, output_path):
    image = imutils.url_to_image(path)
    image = imutils.resize(image, width = min(800, image.shape[1])) 
    result_image = detect(image)
    if output_path is not None:
        cv2.imwrite(output_path, result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return result_image



if __name__ == "__main__":
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    count = humanDetector("https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fstatic.onecms.io%2Fwp-content%2Fuploads%2Fsites%2F38%2F2014%2F11%2F12220214%2Fshutterstock_159281780.jpg")
    print(count)