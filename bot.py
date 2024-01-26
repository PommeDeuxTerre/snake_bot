import websocket, re
from colorama import Fore, Back, Style

class Game:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.p1 = None
        self.p2 = None
        self.apples = []
        self.board  = [[0 for i in range(self.width)] for i in range(self.height)]
    
    def print(self):
        for i in range(self.height):
            text = ""
            for j in range(self.width):
                match self.board[i][j]:
                    case 0:
                        text+=Back.WHITE + "  "+Style.RESET_ALL
                    case 1:
                        text+=Back.GREEN + "  "+Style.RESET_ALL
                    case 2:
                        text+=Back.BLUE + "  "+Style.RESET_ALL
                    case 3:
                        text+=Back.RED + "  "+Style.RESET_ALL
            print(text)
        return

def play(ws):
    while True:
        res = ws.recv()
        if (res=="2"):
            print("check ping")
            ws.send("3")
        elif (re.search('onEnd', res)):
            print("game finished")
            return
        elif (re.search('updateSnakes', res)):
            print("snake update")
            print(res)
        elif (re.search('addSnake', res)):
            print("add snake")
        elif (re.search('updateApple', res)):
            print("apple update")
        elif (re.search('setApples', res)):
            print("set apples")
        elif (re.search('makeGames', res)):
            print("make game")
        else:
            print(f"undefined res: {res}")

test = Game()
test.print()