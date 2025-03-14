import logging
from .player_interface import PlayerInterface
from .board_ import Board

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("__main__.py").info("Project has run")
    tabuleiro = Board()
    PlayerInterface(tabuleiro)
    
