from pathlib import Path
from turtle import bgcolor
from xml.etree.ElementTree import TreeBuilder
from game_utils import *
from GUI_Assets import *
import tkinter
import json
# what is threading??? select???
import threading
import select
# from numpy import imag

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./ASSETS")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

import customtkinter
customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")



class GUI:
    def __init__(self, send, recv, state, s):
        self.window = customtkinter.CTk()
        # init the canvas here
        self.window.geometry("1200x800")
        self.window.configure(bg = "#5294D0")
        # self.Window.withdraw()
        self.canvas_width = 1200.0
        self.canvas_height = 800.0
        # init color palettes
        self.color_primary = "#57A2E8"
        self.color_secondary = "#96C3ED"
        self.color_tertiary = "#D5E9F9"
        self.color_on_primary = "#FFFFFF"
        self.color_on_secondary = "#FFFFFF"
        self.color_on_tertiary = "#000000"
        self.color_background = "#5293CF"


        self.send = send
        self.recv = recv
        self.state = state
        self.socket = s
        # change the original my_msg here
        self.my_action = ''
        self.server_action = ''

        # init the member_lst of the room
        self.members_lst = []

    def start_page(self,notification="Enter Your Name"):
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
        name_entry = labeled_entry(frame,notification,self.color_tertiary,self.color_on_tertiary)
        

        # create new room button
        new_room_button = slim_button(frame, self.color_secondary, "New Room", self.color_on_secondary)
        new_room_button.config(command = lambda: self.register_name(name_entry.get(),"create"))
        

        # create join room button
        join_room_button = slim_button(frame, self.color_primary,"Join Room", self.color_on_primary)
        join_room_button.config(command = lambda: self.register_name(name_entry.get(),"join"))
          
        self.window.mainloop()

    def register_name(self, player_name, action):
        if len(player_name) > 0:
            msg = json.dumps({"action": "login", "name": player_name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == "ok":
                self.state.set_state(S_LOGGEDIN)
                self.state.set_myname(player_name)
                if action == "create":
                    self.create_page(player_name)
                elif action == "join":
                    self.join_page(player_name)
            elif response["status"] == "duplicate":
                self.start_page(notification="This name has been registered. Please enter another")
            # figure out why later
            # # treading means running another function at the same time
            # process = threading.Thread(target=self.proc)
            # process.daemon = True
            # process.start()



    def create_page(self, player_name="empty", notification="Enter Room Name:"):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("create_page_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(x=932.5,y=280,anchor="n")

        # create entry
        room_name_entry = labeled_entry(frame,notification,self.color_tertiary,self.color_on_tertiary)
        

        # create continue button
        new_room_button = slim_button(frame, self.color_secondary, "CONTINUE", self.color_on_secondary)
        new_room_button.config(command = lambda: self.register_room(player_name,room_name_entry.get(),"create"))
        
        # create back button
        back= slim_button(frame,self.color_primary,"BACK",self.color_on_primary)
        back.config(command = lambda: self.start_page())

          
        self.window.mainloop()


    def join_page(self, player_name="empty", notification="Enter room name:"):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("join_page_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(x=932.5,y=280,anchor="n")

        # create entry
        room_name_entry = labeled_entry(frame,notification,self.color_tertiary,self.color_on_tertiary)
        

        # create continue button
        continue_button = slim_button(frame, self.color_secondary, "CONTINUE", self.color_on_secondary)
        continue_button.config(command = lambda: self.register_room(player_name,room_name_entry.get(),"join"))
        
        # create back button
        back= slim_button(frame,self.color_primary,"BACK",self.color_on_primary)
        back.config(command = lambda: self.start_page())


        self.window.mainloop()

    def register_room(self, player_name, room_name, action):
        if len(room_name) > 0:
            if action == "create":
                msg = json.dumps({"action": action, "name": room_name})
            elif action == "join":
                msg = json.dumps({"action": action, "name": room_name})
            self.send(msg)
            response = json.loads(self.recv())
            # create&join share the same
            if response["status"] == "success":
                self.members_lst = response["members"]
                self.state.set_state(S_PAIRING)
                self.pairing_page(room_name)
                # for debugging
                # self.pairing_page(room_name)
                print("Here is fine")

            # create only
            elif response["status"] == "duplicate":
                self.create_page(player_name, notification="This room has been registered. Please enter another:")
            # join only
            elif response["status"] == "no such room":
                self.join_page(player_name, notification="No such room. Please enter another:")
            elif response["status"] == "waiting":
                self.members_lst.append(response["from"])
            else:
                print("Wrong!!!")




    def pairing_page(self,room_name="init"):
        self.room_name = room_name


        background_left = customtkinter.CTkFrame(
            master = self.window,
            width=425,
            height=800,
            fg_color=self.color_primary,
            corner_radius=0
            )
        background_left.place(x=0,y=0)
        self.window.config(bg="#FFFFFF")
        room = customtkinter.CTkLabel(
            master = background_left,
            text_color = self.color_on_primary,
            text = "Room:\n" + room_name,
            text_font= ("Montserrat Alternates SemiBold", 40 * -1),
            justify = tkinter.LEFT
            )
        room.place(relx=0.1,rely=0.2)

        divider = customtkinter.CTkFrame(
            master = background_left,
            width = 220,
            height = 10,
            fg_color = self.color_on_primary,
            )
        divider.place(relx=0.12, y =279)

        guide = customtkinter.CTkLabel(
            master = background_left,
            text_color = self.color_on_primary,
            text = "Use your knowledge\nto compete with\nyour friends.\nLearn for fun!",
            text_font= ("Geo", 28 * -1),
            justify = tkinter.LEFT
            )
        guide.place(relx=0.1, rely=0.4)

        background_right = customtkinter.CTkFrame(
            master = self.window,
            width=775,
            height=800,
            fg_color="#FFFFFF",
            corner_radius=0
            )
        background_right.place(x=425,y=0)
        

        title = customtkinter.CTkLabel(
            master = background_right,
            text_color = self.color_on_tertiary,
            text = "Waiting For Players...",
            text_font= ("Montserrat Alternates SemiBold", 60 * -1),
            justify = tkinter.LEFT
            )
        title.place(relx=0.5,y=157,anchor="center")

        self.member_frame = customtkinter.CTkFrame(
            master = background_right,
            bg_color="#FFFFFF",
            fg_color="#FFFFFF"
            )
        self.member_frame.place(relx=0.1,y=220)


        # show who are in the room
        for player in self.members_lst:
            customtkinter.CTkLabel(
                master = self.member_frame,
                text = player,
                text_color = self.color_on_secondary,
                text_font = ("Montserrat Alternates SemiBold", 24 * -1),
                corner_radius=5,
                bg_color=self.color_on_primary,
                fg_color=self.color_secondary
                ).pack(side=tkinter.LEFT,padx=10)
                
        # maybe bug here
        # update when some one enters
        # response = json.loads(self.recv())
        # if len(response) > 0:
        #     if response["action"] == "pairing":
        #         members_lst.append(response["from"])
        #         customtkinter.CTkLabel(
        #             master = member_frame,
        #             text = player,
        #             text_color = self.color_on_secondary,
        #             text_font = ("Montserrat Alternates SemiBold", 24 * -1),
        #             bg_color=self.color_primary,
        #             fg_color=self.color_secondary
        #             ).pack()

        
        # update_process = threading.Thread(target=self.update_member)
        # update_process.daemon = True
        # update_process.start()

        join_button = bold_button(
            master=background_right,
            button_color=self.color_primary,
            text="Join Game",
            text_color=self.color_on_primary
            )
        join_button.config(bg_color = "#FFFFFF")
        join_button.place(relx=0.1,rely=0.75)


        self.update = True
        self.response = {}

        get_response = threading.Thread(target=self.get_response)
        get_response.daemon = True
        get_response.start()

        self.member_frame.after(1000,lambda:self.update_member())


        # try:
        #     response = json.loads(self.recv())
        #     print(response)
        #     if response["action"] == "pairing":
        #         self.members_lst.append(response["from"])
        #         self.pairing_page(room_name)
                
        # except:
        #     print("except")
        #     pass

        self.window.mainloop()

    def get_response(self):
        while self.update:
            self.response = json.loads(self.recv())

    def update_member(self):
        if self.update == True:
            if len(self.response) > 0:
                if self.response["action"] == "pairing":
                    player = self.response["from"]
                    if player not in self.members_lst:
                        self.members_lst.append(player)
                        customtkinter.CTkLabel(
                            master = self.member_frame,
                            text = player,
                            text_color = self.color_on_secondary,
                            text_font = ("Montserrat Alternates SemiBold", 24 * -1),
                            corner_radius=5,
                            bg_color=self.color_on_primary,
                            fg_color=self.color_secondary
                            ).pack(side=tkinter.LEFT,padx=10)
            self.member_frame.after(1000,lambda:self.update_member())                   

    
            
            




    
    def choose_identity_page(self):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("choose_identity_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(relx=0.5,y=410,anchor="n")
 

        # create question_setter button
        question_setter_button = bold_button(frame, self.color_secondary, "Question setter", self.color_on_secondary)
        question_setter_button.config(command = lambda: print(room_name_entry.get()))


        # create respondent button
        respondent_button = bold_button(frame, self.color_primary,"Respondent", self.color_on_primary)
        respondent_button.config(command = lambda: print(name_entry.get()))

          
        self.window.mainloop()


    def confirm_respondent_page(self):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("confirm_respondent_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(relx=0.5,y=550,anchor="n")
 

         # create continue button
        continue_button = bold_button(frame, self.color_secondary, "CONTINUE", self.color_on_secondary)
        continue_button.config(command = lambda: print(room_name_entry.get()))

          
        self.window.mainloop()


    def confirm_question_setter_page(self):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("confirm_question_setter_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#000000",
            fg_color="#000000",
            )
        frame.place(relx=0.5,y=550,anchor="n")
 

         # create continue button
        continue_button = bold_button(frame, self.color_secondary, "CONTINUE", self.color_on_secondary)
        continue_button.config(command = lambda: print(room_name_entry.get()))

          
        self.window.mainloop()
    

    def game_rules_page(self):
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
        background_image = tkinter.PhotoImage(file = relative_to_assets("GameRules_page_background.png"))
        canvas.create_image(0,
                            0,
                            anchor = 'nw',
                            image = background_image)


        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=417,
            height=431,
            bg_color="#5293CF",
            fg_color="#5293CF",
            )
        frame.place(relx=0.83,y=650,anchor="n")
 

        # create next button
        next_button = bold_button(frame, self.color_secondary, "NEXT", self.color_on_secondary)
        next_button.config(command = lambda: print(room_name_entry.get()))
        next_button.config(bg_color = "#5293CF")
        next_button.pack(padx=0,pady=0)


        self.window.mainloop()


    # def wait_question_page(self):
    #     # create the CTKcanvas
    #     canvas = customtkinter.CTkCanvas(self.window,
    #                                     bg = "#000000",
    #                                     height = self.canvas_height,
    #                                     width = self.canvas_width,
    #                                     bd = 0,
    #                                     highlightthickness = 0,
    #                                     relief = "ridge")
    #     canvas.place(x=0,y=0)


    #     # make the frame for contents
    #     frame = customtkinter.CTkFrame(
    #         master = canvas,
    #         width=1200,
    #         height=800,
    #         bg_color="#000000",
    #         fg_color="#000000",
    #         )
    #     frame.place(x=300,y=100,anchor="n")


    #     # create "LOADING..."
    #     reminder = customtkinter.CTkLabel(
    #         master = frame,
    #         text_color = self.color_primary,
    #         text = "LOADING...",
    #         text_font= ("Montserrat Alternates SemiBold", 96 * -1),
    #         )
    #     reminder.place(relx=0.5,rely=0.2)


    #     #create "Wait until all the questions have been settled."
    #     reminder = customtkinter.CTkLabel(
    #         master = frame,
    #         text_color = self.color_primary,
    #         text = "Wait until all the questions\nhave been settled.\nThe game will begin at any time.",
    #         text_font= ("Geo", 40 * -1),
    #         )
    #     reminder.place(relx=0.55,rely=0.35)

    #     self.window.mainloop()

    # create 5 playing pages
    def loop(i):
        for i in range(1,6):
            play_game_page()
            i+=1
    def play_game_page(self,i):
        # make the frame for contents
        frame = customtkinter.CTkFrame(
            master = self.window,
            width=1200,
            height=800,
            bg_color = "#FFFFFF",
            fg_color = "#FFFFFF",
            )
        frame.place(x=0,y=0,anchor="nw")

        
        # create title
        title = customtkinter.CTkLabel(
            master = frame,
            text_color = "#5293CF",
            text = "Question("+str(i)+"/5)",
            text_font= ("Montserrat Alternates SemiBold", 40 * -1)
            )
        title.place(relx=0.05,rely=0.05)

        # create frame for questions & answers
        frame_question = customtkinter.CTkFrame(
            master = self.window,
            width=1200,
            height=800,
            bg_color = self.color_background,
            fg_color = self.color_background,
            )
        frame_question.place(relx=0.5,rely=0.5,anchor='n')

        # set the question
        question = question_label(
            master = frame_question, 
            text = "yeahyeahyeahyeahyeahyeahyeah"
            )
        frame_question.place(relx=0.5,rely=0.25)
        

        frame_answers = customtkinter.CTkFrame(
            master = self.window,
            width=1200,
            height=800,
            bg_color = "#FFFFFF",
            fg_color = "#FFFFFF",
            )
        frame_answers.place(relx=0.5,rely=0.4,anchor='n')
        
        # create "options" label
        options = customtkinter.CTkLabel(
            master = frame,
            text_color = "#FFFFFF",
            text = "Options",
            text_font= ("Geo", 40 * -1),
            )
        options.place(relx=0.08,rely=0.333)


        answer1 = thick_button(
            master = frame_answers,
            button_color = "#456765",
            text = "234567",
            text_color = "#456788",
            )
        answer1.pack(padx=10,pady=10)


        answer2 = thick_button(
            master = frame_answers,
            button_color = "#456765",
            text = "234567",
            text_color = "#456788",
            )
        answer2.pack(padx=10,pady=10)

        answer3 = thick_button(
            master = frame_answers,
            button_color = "#456765",
            text = "234567",
            text_color = "#456788",
            )
        answer3.pack(padx=10,pady=10)

        answer4 = thick_button(
            master = frame_answers,
            button_color = "#456765",
            text = "234567",
            text_color = "#456788",
            )
        answer4.pack(padx=10,pady=10)


        self.window.mainloop()



    # copy that in chat GUI here, change later
    # def proc(self):
    #     # print(self.msg)
    #     while True:
    #         read, write, error = select.select([self.socket], [], [], 0)
    #         peer_msg = []
    #         # print(self.msg)
    #         if self.socket in read:
    #             peer_msg = self.recv()
            # # figure it out later, what is textCons???
            # if len(self.my_msg) > 0 or len(peer_msg) > 0:
            #     # print(self.system_msg)
            #     self.system_msg = self.sm.proc(self.my_msg, peer_msg)
            #     self.my_msg = ""
            #     self.textCons.config(state=NORMAL)
            #     self.textCons.insert(END, self.system_msg + "\n\n")
            #     self.textCons.config(state=DISABLED)
            #     self.textCons.see(END)

    def run(self):
        self.start_page()    
        # self.join_page()
        # self.create_page()
        # self.choose_identity_page()
        # self.confirm_respondent_page()
        # self.confirm_question_setter_page()

if __name__ == "__main__":
    g = GUI('','','','')
    # g.start_page()
    # g.create_page()
    # g.join_page()
    # g.pairing_page()
    # g.choose_identity_page()
    # g.confirm_respondent_page()
    # g.confirm_question_setter_page()
    # g.game_rules_page()
    # g.wait_question_page()
    g.play_game_page()