from pathlib import Path
import tkinter

# from numpy import imag

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./ASSETS")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

import customtkinter
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

from GUI_Assets import *

class GUI:
    def __init__(self, send, recv, state, s):
        self.window = customtkinter.CTk()
        #init the canvas here
        self.window.geometry("1200x800")
        self.window.configure(bg = "#5294D0")
        # self.Window.withdraw()
        self.canvas_width = 1200.0
        self.canvas_height = 800.0
        #init color palettes
        self.color_primary = "#57A2E8"
        self.color_secondary = "#96C3ED"
        self.color_tertiary = "#D5E9F9"
        self.color_on_primary = "#FFFFFF"
        self.color_on_secondary = "#FFFFFF"
        self.color_on_tertiary = "#000000"


        self.send = send
        self.recv = recv
        self.state = state
        self.socket = s
        self.my_msg = ''
        self.system_msg = ''

    def start_page(self):
        # create the CTKcanvas
        canvas = customtkinter.CTkCanvas(self.window,
                                        bg = "#FFFFFF",
                                        height = self.canvas_height,
                                        width = self.canvas_width,
                                        bd = 0,
                                        highlightthickness = 0,
                                        relief = "ridge")
        canvas.place(x=0,y=0)
        # create the background image
        background_image = tkinter.PhotoImage(file = relative_to_assets("start_page_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)
        

        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=282,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(relx=0.5,y=454,anchor="n")

        # create entry
        name_entry = labeled_entry(frame,"ENTER YOUR NAME",self.color_tertiary,self.color_on_tertiary)
        

        # create new room button
        new_room_button = slim_button(frame, self.color_secondary, "New Room", self.color_on_secondary)
        new_room_button.config(command = lambda: print(name_entry.get()))
        

        # create join room button
        join_room_button = slim_button(frame, self.color_primary,"Join Room", self.color_on_primary)
        join_room_button.config(command = lambda: print(name_entry.get()))
          
        self.window.mainloop()

    
    def run(self):
        self.start_page()    

if __name__ == "__main__":
    g = GUI('','','','')
    g.start_page()