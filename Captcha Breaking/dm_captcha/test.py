import os
img_dir = r"X:\ORS\Surveillance Unit\Surveys\NPS Online Survey\Full Implementation\NRC collaboration\scraping\dm_captcha\captchas"
os.chdir(img_dir)
imgs = iter(os.listdir(img_dir))

file = next(imgs)


os.rename(os.path.join(img_dir,file), os.path.join(img_dir,"solved",file))