import tkinter
import PIL.Image, PIL.ImageTk
from manager import Manager

class MammothMap(tkinter.Tk):


    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.canvas = tkinter.Canvas(self, width = screen_width, height = screen_height)
        self.canvas.pack()
        self.manager = Manager()
        self.place_image()
    
    def place_image(self):
        self.image = self.manager.refresh_map()
        self.photo = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(self.image))
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.after(2000, self.place_image) 

if __name__== "__main__":
    app = MammothMap()
    app.mainloop()

