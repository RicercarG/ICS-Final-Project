import time
import socket
import select
import sys
import string
# import indexer
import json
import pickle as pkl
from game_utils import *
import game_room as room

class Server:
    def __init__(self):
        self.new_players = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.room = room.Room()
        self.loser_lst = []
        self.winner = ""
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)

        # set the color dictionary
        self.color_dict = {"red":"#C03221","orange":"#ED7D3A","yellow":"#F0D719","green":"#4A8259","cyan":"#4AC3D3","blue":"#2F4E89","purple":"#521C5E"}
        self.total_answers_recv = 0
        self.right_choice_made = 0

    def new_player(self, sock):
        # add to all sockets and to new players
        print('new player...')
        sock.setblocking(0)
        self.new_players.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        try:
            msg = json.loads(myrecv(sock))
            print("login:", msg)
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]

                    if self.room.is_member(name) != True:
                        # move socket from new clients list to logged clients
                        self.new_players.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        print(name + ' logged in')
                        self.room.enter_game(name)
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "ok"}))

                    else: # a player under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.room.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
# ==============================================================================
# handle create/join room request
# ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "create":
                room_name = msg["name"]
                from_name = self.logged_sock2name[from_sock]
                print(room_name, from_name)
                # check whether the room has already existed
                if self.room.find_room(room_name) == False:
                    print("start creating the room")
                    # create the room
                    self.room.create_room(from_name, room_name)
                    msg = json.dumps(
                        {"action": "create", "status": "success","members":[from_name]})
                elif self.room.find_room(room_name) == True:
                    print("room has been created")
                    # "duplicate" means the room name has already been taken by others
                    msg = json.dumps(
                        {"action": "create", "status": "duplicate"})

                mysend(from_sock, msg)
            elif msg["action"] == "join":
                room_name = msg["name"]
                from_name = self.logged_sock2name[from_sock]
                # check whether the room exists
                if self.room.find_room(room_name) == True:
                    # join the room
                    self.room.join_room(from_name, room_name)
                    other_players = self.room.room_others(from_name, room_name)
                    all_players = self.room.room_members(room_name)
                    msg = json.dumps(
                        {"action": "join", "status": "success","members":all_players})
                    for player in other_players:
                        to_sock = self.logged_name2sock[player]
                        mysend(to_sock, json.dumps(
                            {"action": "pairing", "status": "waiting", "from": from_name}))
                elif self.room.find_room(room_name) == False:
                    msg = json.dumps(
                        {"action": "join", "status": "no such room"})

                else:
                    print("something goes wrong with join function")
                mysend(from_sock, msg)

# ==============================================================================
# the game finally starts
# ==============================================================================

            elif msg["action"] == "game start":
                room_name = msg["from room"]
                if len(self.room.room_members(room_name)) > 1:
                    question, answers_name, answers_hex = generate_question_and_answers(self.color_dict)
                    for player in self.room.room_members(room_name):
                        msg = json.dumps({"action":"game start", "status":"success"})
                        to_sock = self.logged_name2sock[player]
                        mysend(to_sock, msg)
                    time.sleep(5)
                    print("now sending the question")
                    for player in self.room.room_members(room_name):
                        msg = json.dumps({"action":"receive question","question":question,"answers_name":answers_name,"answers_hex":answers_hex})
                        to_sock = self.logged_name2sock[player]
                        mysend(to_sock, msg)
    
                else:
                    msg = json.dumps({"action":"game start","status":"denied"})
                    mysend(from_sock, msg)

            elif msg["action"] == "choice made":
                self.total_answers_recv += 1
                from_name = self.logged_sock2name[from_sock]
                room_name = msg["from room"]
                if msg["status"] == "right":
                    self.right_choice_made += 1
                    if self.right_choice_made == 1: # make sure this is the first player to answer
                        # add one score to the player
                        self.room.right_answer(from_name)
                        # make this guy the winner
                        self.winner = from_name
                    else:
                        self.loser_lst.append(from_name)
                else:
                    self.loser_lst.append(from_name)
                
                # after all players have made the choice:
                if self.total_answers_recv == len(self.room.room_members(room_name)):
                    # label this guy as the last one who make the choice
                    last_player = from_name
                    # get the highest_score
                    highest_score = 0
                    for player in self.room.room_members(room_name):
                        player_score = self.room.members[player]
                        if player_score > highest_score:
                            highest_score = player_score
                    # get the list of players who have the highest score
                    top_player_lst = []
                    for player in self.room.room_members(room_name):
                        player_score = self.room.members[player]
                        if player_score == highest_score:
                            top_player_lst.append(player)
                    
                    # get the top three players for the last page
                    sorted_player_lst = []
                    sorted_values = sorted(self.room.members.values())
                    sorted_values.reverse()
                    for i in sorted_values:
                        for k in self.room.members.keys():
                            if self.room.members[k] == i:
                                if k not in sorted_player_lst:
                                    sorted_player_lst.append(k)
                                    break
                    if len(sorted_player_lst) == 2:
                        top_three_lst = sorted_player_lst + [""]
                    else:
                        top_three_lst = sorted_player_lst[:3]

                    # send the msg to the winner, if there's any
                    if len(self.winner) > 0: 
                        if self.winner == last_player:
                            winner_msg = json.dumps(
                                {"action": "able to start next round", "status": "win", "top players":top_player_lst, "top score": highest_score, "player score":self.room.members[self.winner], "top three":top_three_lst})
                        else:
                            winner_msg = json.dumps(
                                {"action": "round end", "status": "win", "top players":top_player_lst, "top score": highest_score, "player score":self.room.members[self.winner], "top three":top_three_lst})

                        winner_sock = self.logged_name2sock[self.winner]
                        mysend(winner_sock,winner_msg)

                    # send the msg to other players
                    for player in self.loser_lst:
                        to_sock = self.logged_name2sock[player]
                        if player == last_player:
                            msg = json.dumps(
                                {"action": "able to start next round", "status": "lose", "top players":top_player_lst, "top score": highest_score, "player score":self.room.members[player], "top three":top_three_lst})

                        else:
                            msg = json.dumps(
                                {"action": "round end", "status": "lose", "top players":top_player_lst, "top score": highest_score, "player score":self.room.members[player], "top three":top_three_lst})
                        mysend(to_sock,msg)
                    # prepare for the next round
                    self.winner = ""
                    self.loser_lst = []
                    self.total_answers_recv=0
                    self.right_choice_made=0
    
        else:
            # client died unexpectedly
            self.logout(from_sock)

    def run(self):
        print('starting game server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged players..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new players..')
            for newc in self.new_players[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new player request
                sock, address = self.server.accept()
                self.new_player(sock)

def main():
    server = Server()
    server.run()

if __name__ == "__main__":
    main()



                        
                        






