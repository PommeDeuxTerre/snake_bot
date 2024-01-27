import websocket, re, json
from colorama import Fore, Back, Style
import time


MOVES = ["W", "A", "S", "D"]

class Game:
    def __init__(self):
        self.width = 20
        self.height = 20
        self.p1 = []
        self.p2 = []
        self.apples = []
        self.board  = [[0 for i in range(self.width)] for i in range(self.height)]
        self.dir = 1
    
    def print(self):
        texts = [
            Back.WHITE + "  "+Style.RESET_ALL,
            Back.GREEN + "  "+Style.RESET_ALL,
            Back.BLUE + "  "+Style.RESET_ALL,
            Back.RED + "  "+Style.RESET_ALL
        ]

        for i in range(self.height):
            text = ""
            for j in range(self.width):
                text+=texts[self.board[i][j]]
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

    def get_move(self):
        if (len(self.p1)%2==0):
            self.dir+=1
            self.dir%=4
            return MOVES[self.dir]
        #find the best path to get an apple by bfs
        else:
            #hashmap to check if a node's already been explored and do the backtracking
            board  = [[0 for i in range(self.width)] for i in range(self.height)]
            queue = [self.p1[0]]
            #print(f"snake: {self.p1[0]}")
            #put true where the head is, for the backtracking
            board[self.p1[0]["y"]][self.p1[0]["x"]] = True
            apple = None
            #find the closest apple
            while queue and not apple:
                node = queue.pop(0)
                next_nodes = [
                    #up
                    {"x": node["x"], "y": (node["y"]-1)%self.height},
                    #left
                    {"x": (node["x"]-1)%self.width, "y": node["y"]},
                    #down
                    {"x": node["x"], "y": (node["y"]+1)%self.height},
                    #right
                    {"x": (node["x"]+1)%self.width, "y": node["y"]}
                ]
                for next_node in next_nodes:
                    if not board[next_node["y"]][next_node["x"]]:
                        board[next_node["y"]][next_node["x"]]=node
                        if self.board[next_node["y"]][next_node["x"]]==3:
                            apple = {"x":next_node["x"], "y":next_node["y"]}
                            break
                        queue.append({"x":next_node["x"], "y":next_node["y"]})
            #print(f"apple: {apple}")

            #backtrack to find the next node to go
            node = apple
            next_node = board[node["y"]][node["x"]]
            while board[next_node["y"]][next_node["x"]]!=True:
                node = next_node
                next_node = board[node["y"]][node["x"]]

            #get the dir to take
            #up
            if (node["x"]==self.p1[0]["x"] and node["y"]==(self.p1[0]["y"]-1)%self.height):
                move = 0
            #left
            elif (node["x"]==(self.p1[0]["x"]-1)%self.width and node["y"]==self.p1[0]["y"]):
                move = 1
            #down
            elif (node["x"]==self.p1[0]["x"] and node["y"]==(self.p1[0]["y"]+1)%self.height):
                move = 2
            #right
            elif (node["x"]==(self.p1[0]["x"]+1)%self.width and node["y"]==self.p1[0]["y"]):
                move = 3
            else:
                print(f"node : {node}")
                print(f"p1 : {self.p1[0]}")
            
            #print(move, self.dir)
            if (move!=self.dir):
                self.dir = move
                return MOVES[move]

def play(ws):
    game = Game()
    while True:
        res = ws.recv()
        if (res=="2"):
            #print("check ping")
            ws.send("3")
        elif (re.search('onEnd', res)):
            game = Game()
            time.sleep(0.5)
            ws.send('42["playRoom"]')
            #print("game finished")
        elif (re.search("removeClientRoom", res)):
            return
        elif (re.search('updateSnakes', res)):
            #print("snake update")
            game.update_snakes(res)
            move = game.get_move()
            #print(move)
            if move!=None:ws.send(f'42["move","{move}"]')
        elif (re.search('addSnake', res)):
            #print("add snake")
            pass
        elif (re.search('updateApple', res)):
            #print("apple update")
            game.update_apples(res)
        elif (re.search('setApples', res)):
            #print("set apples")
            game.set_apples(res)
        elif (re.search('makeGames', res)):
            #print("make game")
            pass
        else:
            #print(f"undefined res: {res}")
            pass

        game.update_board()
        #game.print()
