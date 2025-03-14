class Player:
    def __init__(self,team):
        self.teamenum =team
        self.vitorias = 0
        self.venceu = False
      
    def get_team(self):
        return self.teamenum
    
    def get_vitorias(self):
        return self.vitorias
    
    def set_vitorias(self):
        self.vitorias +=1

    def get_venceu(self):
        return self.venceu
    
    def set_venceu(self,var):
        self.venceu = var
        