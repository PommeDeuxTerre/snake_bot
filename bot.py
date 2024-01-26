import websocket, re, json
from colorama import Fore, Back, Style


class Game:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.p1 = []
        self.p2 = []
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

    def update_board(self):
        self.board  = [[0 for i in range(self.width)] for i in range(self.height)]
        for el in self.p1:
            try:self.board[el["y"]][el["x"]]=1
            except:print(f"error: {el}")
        for el in self.p2:
            try:self.board[el["y"]][el["x"]]=2
            except:print(f"error: {el}")
        apples_eaten = []
        for el in self.apples:
            if self.board[el["y"]][el["x"]]!=0:apples_eaten.append(el)
            else: self.board[el["y"]][el["x"]]=3
        for apple in apples_eaten:
            self.apples.remove(apple)

    def update_snakes(self, snakes):
        self.p1 = []
        self.p2 = []
        snakes = json.loads(snakes[2:])[1]
        #player 1
        for square in snakes[0]:
            new_square = {"x":square["x"]//40, "y":square["y"]//40}
            self.p1.append(new_square)

        #player 2
        for square in snakes[1]:
            new_square = {"x":square["x"]//40, "y":square["y"]//40}
            self.p2.append(new_square)
    
    def update_apples(self, apples):
        apple = json.loads(apples[2:])[2]
        apple["x"]//=40
        apple["y"]//=40
        self.apples.append(apple)
    
    def set_apples(self, apples):
        self.apples = []
        apples = json.loads(apples[2:])[1]
        for square in apples:
            new_square = {"x":square["x"]//40, "y":square["y"]//40}
            self.apples.append(new_square)

def play(ws):
    game = Game()
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
            game.update_snakes(res)
        elif (re.search('addSnake', res)):
            print("add snake")
        elif (re.search('updateApple', res)):
            print("apple update")
            game.update_apples(res)
        elif (re.search('setApples', res)):
            print("set apples")
            game.set_apples(res)
        elif (re.search('makeGames', res)):
            print("make game")
        else:
            print(f"undefined res: {res}")

        game.update_board()
        game.print()