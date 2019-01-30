import base64

with open("b64_img.txt", 'r') as f:
    imgstring = f.read()
    
imgdata = base64.b64decode(imgstring[68:])
filename = "captcha.jpg"
with open(filename, 'wb') as f:
    f.write(imgdata)