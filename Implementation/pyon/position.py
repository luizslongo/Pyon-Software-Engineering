class Position:
    def __init__(self, x, y, owner):
        self.owner = owner
        self.x = x
        self.y = y
        self.valid_move = False
        self.captured = False

    def free(self):
        self.owner = None

    def my_owner(self):
        return self.owner
    
    def set_owner(self,new_owner):
        self.owner=new_owner
        
    def get_axis(self):
        axis=[self.x,self.y]
        return axis
        
    def is_valid_move(self):
        self.valid_move = True
        
    def get_valid_move(self):
        return self.valid_move
        
    def is_not_valid(self):
        self.valid_move = False

    def get_captured(self):
        return self.captured 
    
    def set_captured(self,iscap):
        self.captured = iscap