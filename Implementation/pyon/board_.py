from .position import Position
from .player import Player
from tkinter import messagebox
import time

class Board:
    def __init__(self):
        self.match_status = 1
        self.local_player = None
        self.positions = [[None,None,None],[None,None,None],[None,None,None], [None,None,None], [None,None,None]]
        for x in range(5):
            for y in range(3):
                if(x == 0):#base branca
                    self.positions[x][y]=Position(x,y,1)
                elif(x==4):#base vermelha
                    self.positions[x][y]=Position(x,y,0)
                else:#demais posicoes
                    self.positions[x][y]=Position(x,y,None)
    def get_local_player(self):
        return self.local_player

    def local_player_team(self):
        return self.local_player.get_team()
    
    def create_player(self,team):
        self.local_player = Player(team)

    def reset (self):
        time.sleep(1)
        if(self.local_player.get_venceu()):
            self.local_player.set_vitorias()
            self.local_player.set_venceu(False)
        for x in range(5):
            for y in range(3):
                if(x == 0):#base branca
                    self.get_position(x,y).set_owner(1)
                elif(x==4):#base vermelha
                    self.get_position(x,y).set_owner(0)
                else:#demais posicoes
                    self.get_position(x,y).free()
        self.match_status = 1
        

    def get_status(self):
        return self.match_status
    
    def set_status(self,status):
        self.match_status = status

    def is_move_capture(self,old_pos, new_pos ):
        modulo_x = abs(old_pos.get_axis()[0] - new_pos.get_axis()[0])
        modulo_y = abs(old_pos.get_axis()[1] - new_pos.get_axis()[1])
        media_x = (old_pos.get_axis()[0]  + new_pos.get_axis()[0])/2
        media_y = (old_pos.get_axis()[1]  + new_pos.get_axis()[1])/2 
        if(modulo_x >1 or modulo_y >1):
            if(modulo_x >2):
                var_quatro = self.is_opponent_piece(int(((media_x*2)-1)/2),int(media_y))
                var_cinco = self.is_opponent_piece(int(((media_x*2)+1)/2),int(media_y))
                if(modulo_x >3):
                    var_um = self.is_opponent_piece(int(media_x-1),int(media_y))
                    var_dois = self.is_opponent_piece(int(media_x+1),int(media_y))
                    var_tres = self.is_opponent_piece(int(media_x),int(media_y))                              
                    if(var_um or var_dois or var_tres):
                        return True
                    else:
                        return False
                elif( var_quatro or var_cinco ):
                    return True
                else:
                    return False
            elif (self.is_opponent_piece(int(media_x),int(media_y))):
                return True
            else:
                return False
        else:
            return False

    def is_opponent_piece(self,x, y):
        position = self.get_position(int(x) , int(y))
        if (position.my_owner() != self.local_player.get_team() and position.my_owner() != None):
            position.set_captured(True)
            return True
        else:
            return False
    
    def evaluate_winner(self):
        vence_branco=0
        vence_vermelho=0
        for i in range (3):
            base_branca= self.get_position(0,i)
            base_vermelha= self.get_position(4,i)
            if(base_branca.my_owner()== 0):
                vence_vermelho+=1
            if(base_vermelha.my_owner() == 1):
                vence_branco+=1
        if(vence_vermelho == 3):
            if(self.local_player.get_team()==0):
                self.local_player.set_venceu(True)
            self.match_status = 4
            return 0
        elif(vence_branco == 3):
            if(self.local_player.get_team()==1):
                self.local_player.set_venceu(True)
            self.match_status = 4
            return 1
        return 2
    
    def get_all_owners(self):
        own=[]
        for x in range(5):
            ers=[]
            for y in range(3):
                ers.append(self.get_position(x,y).my_owner())
            own.append(ers)
        return own
    
    def set_all_owners(self,new_owners):
        for x in range(5):
            for y in range(3):
                self.get_position(x,y).set_owner(new_owners[x][y])

    def get_position(self,x,y):
        return self.positions[x][y]
        
    def proceed_move(self,x,y,new_x,new_y):
        old = self.get_position(x,y)
        new = self.get_position(new_x,new_y)
        retorno ={
                "valid_move":False,
                "troca_turno":False
                 }
        if(new.get_valid_move()):
            retorno["valid_move"]=True
         
            if(self.is_move_capture(old,new) and self.match_status == 3):
                retorno["troca_turno"]=False
                self.match_status=2
                self.valid_all_moves()
                
            else:
                self.match_status=3
                retorno["troca_turno"]=True
        else:
            self.match_status=5
        return retorno
    
    def release_positions(self,x,y):
        pos = self.get_position(x,y)
        pos.is_not_valid()
        pos.set_captured(False)

    def valid_all_moves(self):
        for x in range(5):
            for y in range(3):
                verifica=self.get_position(x,y)
                if(verifica.my_owner()==None):
                    verifica.is_valid_move()
