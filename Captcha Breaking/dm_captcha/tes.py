from PIL import Image
import pytesseract

# Simple image to string
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
print(pytesseract.image_to_string(Image.open('cap_0.png')))

