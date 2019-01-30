import cv2
from crop_box import crop_box
from PIL import Image
import pytesseract
import csv

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

total_tested = 0
total_matches = 0

class CaptchaSolver():
    def __init__(self, captcha_dir):
        self.captcha_dir = captcha_dir
        self.captcha_interior = self.get_interior()
        self.solution = self.solve()
            
    def save_captcha_interior(self, path):
        cv2.imwrite(path, self.captcha_interior)
    
    def get_interior(self):
        try:
            return crop_box(self.captcha_dir)
        except ValueError as e:
            print(self.captcha_dir + " - " + str(e))
            return None
    
    def solve(self):
        try:
            return pytesseract.image_to_string(
            Image.fromarray(self.captcha_interior), 
            config='--psm 8')
        except:
            return None
            
            
with open("cap_solutions.csv") as f:
    reader = csv.reader(f)
    for row in reader:
        captcha_dir = "solved/"+row[0]
        
        cs = CaptchaSolver(captcha_dir=captcha_dir)
        
        
        # save_path = "cropped/"+row[0]
        # cs.save_captcha_interior(save_path)
        
        
        tes_answer = CaptchaSolver(captcha_dir=captcha_dir).solution
        manual_answer = row[1]
        total_tested += 1
        if manual_answer == tes_answer:
            total_matches += 1
        # print("{}: {} - {}".format(manual_answer == tes_answer,
                                   # manual_answer, tes_answer))
                                   
print("Overall, {}% success({}/{})".format(total_matches/total_tested,
                                       total_matches, total_tested))
