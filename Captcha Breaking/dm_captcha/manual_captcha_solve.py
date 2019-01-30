# import tkinter as tk
# from PIL import ImageTk, Image
# import os

# root = tk.Tk()

# # Function to load the next image into the Label
# def next_img(answer):
    # print(answer)
    # entryText.set("")
    # img_label.img = ImageTk.PhotoImage(file=next(imgs))
    # img_label.config(image=img_label.img)



# # Choose multiple images
# img_dir = r"X:\ORS\Surveillance Unit\Surveys\NPS Online Survey\Full Implementation\NRC collaboration\scraping\dm_captcha\captchas"
# os.chdir(img_dir)
# imgs = iter(os.listdir(img_dir))

# img_label = tk.Label(root)
# img_label.pack()

# entryText = tk.StringVar()
# e = tk.Entry(root, textvariable=entryText)
# entryText.set("")
# e.pack()


# btn = tk.Button(root, text='Next image', command=next_img(e.get()))
# btn.pack()

# next_img("") # load first image
# e.bind("<Return>", (lambda event: next_img(e.get())))

# root.mainloop()

from tkinter import *
import os 
from PIL import ImageTk
import csv

class Application(Frame):

    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.img_dir = r"X:\ORS\Surveillance Unit\Surveys\NPS Online Survey\Full Implementation\NRC collaboration\scraping\dm_captcha\captchas"
        os.chdir(self.img_dir)
        self.imgs = iter(os.listdir(self.img_dir))
        self.first_img = next(self.imgs)
        self.cap_num = ""
        self.create_img()
        self.input_text = StringVar()
        self.input_text.set("")
        self.create_text_field()
        self.create_button()
        
    def create_button(self):
        self.bttn = Button(self)
        self.bttn['text'] = "Next Captcha"
        self.bttn['command'] = self.prcess_input
        self.bttn.grid()

    def prcess_input(self):
        self.record_input()
        self.input_text.set("")
        self.next_img()
        
    def create_img(self):
        self.img_label = Label(self)
        self.img_label.grid()
        self.img_label.img = ImageTk.PhotoImage(file=self.first_img)
        self.img_label.config(image=self.img_label.img)
        
    def next_img(self):
        filename = next(self.imgs)
        self.img_label.img = ImageTk.PhotoImage(file=filename)
        self.img_label.config(image=self.img_label.img)
        self.cap_num = filename[4:-4]
        os.rename(os.path.join(self.img_dir,filename), os.path.join(self.img_dir,"solved",filename))
        
    def create_text_field(self):
        self.text_field = Entry(self, textvariable=self.input_text)
        self.text_field.grid()
        self.text_field.bind("<Return>", (lambda event: self.prcess_input()))
        
    def record_input(self):
        data = [self.cap_num, self.text_field.get()]
        with open("cap_solutions.csv", "a+") as f:
            writer = csv.writer(f, lineterminator = "\n")
            writer.writerow(data)


root = Tk()
root.title("Captcha Solving")
root.geometry('300x300')

app = Application(root)

root.mainloop() 