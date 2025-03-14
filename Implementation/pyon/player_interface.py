from tkinter import *
from tkinter import messagebox
import os
from uuid import UUID
from py_netgames_client.tkinter_client.PyNetgamesServerProxy import PyNetgamesServerProxy
from py_netgames_client.tkinter_client.PyNetgamesServerListener import PyNetgamesServerListener
from py_netgames_model.messaging.message import MatchStartedMessage, MoveMessage
from .board_ import Board

class PlayerInterface(PyNetgamesServerListener):
    _match_id: UUID

    def __init__(self,board):
        self.tabuleiro = board
        self.setup_window()
        self.create_board()
        self.local_enabled = False
        self.selected = None
        self.add_listener()
        self.send_connect()
        self.match_id=None
        self.main_window.mainloop()

    def is_piece_selected(self):
        return self.selected != None
    
    def update_gui_status(self,winner):
        new_status = self.tabuleiro.get_status()
        if(new_status == 1):
            new_message ="Aguardando inicio"
        if(new_status == 3 and self.local_enabled==True):
            new_message ="Sua vez"
        elif(new_status == 3):
            new_message ="Vez do oponente"
        if(new_status == 2 and self.local_enabled==True):
            new_message ="Mova uma peça capturada!"
        elif(new_status == 2):
            new_message ="O oponente capturou sua peça!"
        if(new_status == 4 and winner == 0):
            new_message ="Vitória do Vermelho!"
        elif(new_status == 4 and winner == 1 ):
            new_message ="Vitória do Branco!"
        if(new_status == 5 and self.local_enabled==True):
            new_message ="Movimento inválido!"
        self.status_label.config(text=new_message)
        if new_status == 4:
            self.tabuleiro.reset()
            self.contador_um.config(text= "Vitorias: "+str(self.tabuleiro.get_local_player().get_vitorias()))
    
    def toggle_btn(self, name, state):
        self.menu_file.entryconfig(name, state=state)

    def setup_window(self):
        self.main_window = Tk()
        self.main_window.title("Pyon")
        self.main_window.geometry("800x600")
        self.main_window.resizable(True, True)
        self.main_window["bg"] = "white"

        for i in range(7):
            self.main_window.columnconfigure(i, weight=1)
            self.main_window.rowconfigure(i, weight=1)

        self.menu_bar = Menu(self.main_window)
        self.menu_bar.option_add("*tearOff", FALSE)
        self.main_window["menu"] = self.menu_bar
        self.menu_file = Menu(self.menu_bar)
        self.menu_bar.add_cascade(menu=self.menu_file, label="Opções")

        self.menu_file.add_command(label="Iniciar Partida", command=lambda: self.send_match(), state="disabled")
        self.menu_file.add_command(label="Desconectar", command=lambda: print("Para desconectar, feche a interface. "), state="disabled")

        self.status_label = Label(self.main_window, text="Esperando início de partida", font=("Arial", 25))
        self.status_label.grid(column=1, row=0, columnspan=5)
        self.contador_um = Label(self.main_window, text="Vitorias: " + str(0), font=("Arial", 25))
        self.contador_um.grid(column=0, row=1, columnspan=5)
       
    def create_board(self):
        self.white = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/white.png"))
        self.white_highlight = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/white_highlight.png"))
        self.red = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/red.png"))
        self.red_highlight = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/red_highlight.png"))
        self.move_circle = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/pos_option.png"))
        self.empty = PhotoImage(file=os.path.join(os.path.dirname(__file__),"images/empty.png"))
        self.board_ui = []
        for x in range(5):
            row = []
            for y in range(3):
                lbl = Label(self.main_window, bd=0, bg="#2f2f2f")
                lbl["image"] = self.empty
                lbl.bind("<Button-1>", lambda event, a = x, b = y: self.select_board_place(event, a, b))
                lbl.grid(column=x+1, row=y+2+1, sticky=W+E+N+S,padx=1,pady=1)
                row.append(lbl)

            self.board_ui.append(row)

        for i in range(3):
            self.board_ui[0][i]["bg"] = "#b7b7b7"
            self.board_ui[0][i]["image"] = self.white
            self.board_ui[4][i]["image"] = self.red
            self.board_ui[4][i]["bg"] = "#b50000"

    def do_move(self,oldx,oldy,newx,newy):
        old_pos=self.tabuleiro.get_position(oldx,oldy)
        old_pos.is_not_valid()
        new_pos=self.tabuleiro.get_position(newx,newy)
        new_pos.is_not_valid()
        new_pos.set_owner(old_pos.my_owner())
        old_pos.free()
        self.selected = None

    def select_board_place(self, event, x, y):
        lbl = self.board_ui[x][y]
        if (self.local_enabled):
            if (self.is_piece_selected()):
                axis = self.selected.get_axis()
                dict = self.tabuleiro.proceed_move(axis[0],axis[1],x,y)
                if (dict["valid_move"]):
                    self.do_move(axis[0],axis[1],x,y)
                    self.clear_possibles()
                    self.all_owners = self.tabuleiro.get_all_owners()
                    self.server_proxy.send_move(self.match_id,{"positions": self.all_owners,"turno":dict["troca_turno"]})
                    if(dict["troca_turno"]==True): 
                        self.local_enabled=False    
                    
            elif(self.tabuleiro.get_position(x,y).my_owner()==self.tabuleiro.local_player_team() and self.tabuleiro.get_status()==3):
                self.selected = self.tabuleiro.get_position(x,y)
                self.show_possible_moves(x,y) 
            
            elif(self.tabuleiro.get_position(x,y).my_owner()!=self.tabuleiro.local_player_team() and self.tabuleiro.get_position(x,y).get_captured() and self.tabuleiro.get_status()==2):
                self.selected = self.tabuleiro.get_position(x,y)
                self.tabuleiro.valid_all_moves()
        self.update_gui_status(self.tabuleiro.evaluate_winner())
        self.arruma_interface()
    
    def show_possible_moves(self,x,y):
        xm = x-1
        ym = y-1
        for i in range (3):
            for j in range (3):
                xmi = xm+i
                ymj = ym+j
                if(xmi>=0 and xmi <=4 and ymj >=0 and ymj <=2 ):
                    verifica = self.tabuleiro.get_position(xmi,ymj)
                    if(verifica.my_owner() == None and verifica != self.tabuleiro.get_position(x,y)):
                        verifica.is_valid_move()
                    elif(verifica.my_owner() != None and verifica != self.tabuleiro.get_position(x,y)):
                        self.show_possible_jumps(x,y,xmi,ymj)
                       
    def show_possible_jumps(self,atual_x,atual_y,x_ocupado,y_ocupado):
        jump_x = x_ocupado - atual_x
        jump_y = y_ocupado - atual_y
        for i in range(3):
            x_ocupado += jump_x
            y_ocupado += jump_y
            if(x_ocupado>=0 and x_ocupado <=4 and y_ocupado >=0 and y_ocupado <=2 ):    
                verifica = self.tabuleiro.get_position(x_ocupado,y_ocupado)
                if(verifica.my_owner() == None):
                    verifica.is_valid_move()
                    return
            else:
                return
    
    def clear_possibles(self):
        for x in range(5):
            for y in range(3):
                if(self.tabuleiro.get_position(x,y).get_valid_move()):
                    self.tabuleiro.release_positions(x,y)

    def arruma_interface(self):
        for x in range(5):
            for y in range(3):
                verifica=self.tabuleiro.get_position(x,y)
                if(verifica.get_valid_move()):
                    self.board_ui[x][y]["image"] = self.move_circle
                elif(verifica.my_owner()==1):
                    self.board_ui[x][y]["image"] = self.white
                    if(verifica==self.selected):
                        self.board_ui[x][y]["image"] = self.white_highlight
                elif(verifica.my_owner()==0):
                    self.board_ui[x][y]["image"] = self.red
                    if(verifica==self.selected):
                        self.board_ui[x][y]["image"] = self.red_highlight
                else:
                    self.board_ui[x][y]["image"] = self.empty

#---------------- PYNG------------
    def add_listener(self):
        self.server_proxy = PyNetgamesServerProxy()
        self.server_proxy.add_listener(self)

    def receive_connection_success(self):
        self.toggle_btn("Iniciar Partida", "active")
        self.toggle_btn("Desconectar", "active")
        messagebox.showinfo(message="Conectado ao servidor")

    def send_connect(self):
        self.server_proxy.send_connect(address="wss://py-netgames-server.fly.dev")

    def send_match(self):
        self.server_proxy.send_match(2)
        
    def receive_match(self, match):
        messagebox.showinfo(message="Partida iniciada. " + str(match.position))
        self.tabuleiro.set_status(3)
        self.match_id=match.match_id
        self.tabuleiro.create_player(match.position)
        if(match.position==0):
            self.local_enabled=True
        self.update_gui_status(self.tabuleiro.evaluate_winner())

    def receive_disconnect(self):
        messagebox.showinfo(message="O oponente desconectou")

    def receive_error(self, error):
        self.tabuleiro.reset()
        messagebox.showinfo(message="receive_error")

    def receive_move(self, move):
        new_move=move.payload
        if(new_move["turno"]):
            self.tabuleiro.set_status(3)
            self.local_enabled=True
        else:
            self.tabuleiro.set_status(2)
        self.tabuleiro.set_all_owners(new_move["positions"])
        self.update_gui_status(self.tabuleiro.evaluate_winner())
        self.arruma_interface()
