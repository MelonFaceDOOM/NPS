import cv2
from crop_box import crop_box
import csv

def save_interior(file_name):
    captcha_dir = "captchas/"+file_name
    try:
        cropped = crop_box(captcha_dir)
    except ValueError as e:
        print(captcha_dir + " - " + str(e))
        cropped = None

    if cropped is not None:
        save_path = "crop_testing/"+file_name
        cv2.imwrite(save_path, cropped)


with open("cap_solutions.csv") as f:
    reader = csv.reader(f)
    
    for i in range(0,10):
        file_name = next(reader)[0]
        save_interior(file_name)