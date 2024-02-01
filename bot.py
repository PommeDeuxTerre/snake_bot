import websocket, re, json, time
from colorama import Fore, Back, Style


MOVES = ["W", "A", "S", "D"]

def check_apple(game, square):
    res = game.board[square["y"]][square["x"]]==3
    return res

def check_head_p2(game, square):
    res = square["x"]==game.p2[0]["x"] and square["y"]==game.p2[0]["y"]
    return res

def voldemor(game, square):
    if len(game.p2) >= len(game.p1):return check_apple(game, square)
    return check_head_p2(game, square) or check_apple(game, square)

def get_direction_bfs(game, check_good_target, check_target_backup = None, anti_dumb=False):
    #hashmap to check if a node's already been explored and do the backtracking
    board  = [[0 for i in range(game.width)] for i in range(game.height)]
    queue = [game.p1[0]]
    #avoid to start with dumb moves
    if anti_dumb:
        dumb_moves = get_dumb_moves(game)
        print(f"dumb moves: {dumb_moves}")
        for dumb_move in dumb_moves:
            board[dumb_move["y"]][dumb_move["x"]] = 1
    #print(f"snake: {game.p1[0]}")
    #put true where the head is, for the backtracking
    board[game.p1[0]["y"]][game.p1[0]["x"]] = True
    target = None
    #find the closest target
    while queue and not target:
        node = queue.pop(0)
        next_nodes = [
            {"x": node["x"], "y": (node["y"]-1)%game.height},#up
            {"x": (node["x"]-1)%game.width, "y": node["y"]},#left
            {"x": node["x"], "y": (node["y"]+1)%game.height},#down
            {"x": (node["x"]+1)%game.width, "y": node["y"]}#right
        ]

        for next_node in next_nodes:
            #check if already explored
            if board[next_node["y"]][next_node["x"]]:continue
            board[next_node["y"]][next_node["x"]]=node

            if check_good_target(game, next_node):
                target = next_node
                break

            if not game.board[next_node["y"]][next_node["x"]] in [1, 2]:
                queue.append({"x":next_node["x"], "y":next_node["y"]})

    print(f"target: {target}")
    if target==None and check_target_backup==None:
        moves = get_all_moves(game, game.p1)
        if not anti_dumb:return moves[0]
        for move in moves:
            found = False
            for dumb in dumb_moves:
                if dumb["x"]==move["x"] and dumb["y"]==move["y"]:found = True
            if not found:
                target = move
                break
        if not target:return None
    elif target==None:return get_direction_bfs(game, check_target_backup, anti_dumb=anti_dumb)
    print(f"target: {target}")

    #backtrack to find the next node to go
    node = target
    next_node = board[node["y"]][node["x"]]
    print(f"next_node: {next_node}")
    while board[next_node["y"]][next_node["x"]]!=True:
        node = next_node
        next_node = board[node["y"]][node["x"]]

    #get the dir to take
    #up
    if (node["x"]==game.p1[0]["x"] and node["y"]==(game.p1[0]["y"]-1)%game.height):
        move = 0
    #left
    elif (node["x"]==(game.p1[0]["x"]-1)%game.width and node["y"]==game.p1[0]["y"]):
        move = 1
    #down
    elif (node["x"]==game.p1[0]["x"] and node["y"]==(game.p1[0]["y"]+1)%game.height):
        move = 2
    #right
    elif (node["x"]==(game.p1[0]["x"]+1)%game.width and node["y"]==game.p1[0]["y"]):
        move = 3
    else:
        print(f"else: {node}")
        move = 0

    return move

def get_void_squares(game, player):
    if not player:return 0
    queue = [player[0]]
    board = [[0 for i in range(game.width)] for i in range(game.height)]
    number = 0

    while queue:
        node = queue.pop(0)
        next_nodes = [
            {"x": node["x"], "y": (node["y"]-1)%game.height},#up
            {"x": (node["x"]-1)%game.width, "y": node["y"]},#left
            {"x": node["x"], "y": (node["y"]+1)%game.height},#down
            {"x": (node["x"]+1)%game.width, "y": node["y"]}#right
        ]

        for next_node in next_nodes:
            #check if already explored
            if not board[next_node["y"]][next_node["x"]] and not game.board[next_node["y"]][next_node["x"]] in [1, 2]:
                board[next_node["y"]][next_node["x"]]=node
                queue.append({"x":next_node["x"], "y":next_node["y"]})
                number+=1

    return number

def get_all_moves(game, player):
    moves = []
    node = player[0]
    next_nodes = [
        {"x": node["x"], "y": (node["y"]-1)%game.height},#up
        {"x": (node["x"]-1)%game.width, "y": node["y"]},#left
        {"x": node["x"], "y": (node["y"]+1)%game.height},#down
        {"x": (node["x"]+1)%game.width, "y": node["y"]}#right
    ]

    for next_node in next_nodes:
        if game.board[next_node["y"]][next_node["x"]] in [0,3]:
            moves.append(next_node)
    return moves

def make_move(game, player, player_number, move):
    player.insert(0, move)
    value = game.board[move["y"]][move["x"]]
    game.board[move["y"]][move["x"]] = player_number
    return value

def cancel_move(game, player, move, value):
    player.remove(move)
    game.board[move["y"]][move["x"]] = value

def get_dumb_moves(game, deep=0, deepmax=1):
    if deep==deepmax:return get_void_squares(game, game.p1)-get_void_squares(game, game.p2)

    #get all the moves that are not part of a snake already
    p1_moves = get_all_moves(game, game.p1)

    #if same strength or less, avoid head contact
    to_remove = []
    if (len(game.p2) >= len(game.p1)):
        p2_moves = get_all_moves(game, game.p2)
        for move2 in p2_moves:
            for move1 in p1_moves:
                if move2["x"]==move1["x"] and move2["y"]==move1["y"]:
                    to_remove.append(move1)
        for remove in to_remove:
            p1_moves.remove(remove)
                    

    #get a score for each move
    best_scores = []
    for p1_move in p1_moves:
        worst_score = 400
        value1 = make_move(game, game.p1, 1, p1_move)
        for p2_move in get_all_moves(game, game.p2):
            value2 = make_move(game, game.p2, 2, p2_move)
            score = get_dumb_moves(game, deep+1)
            if score<worst_score:
                worst_score = score
            cancel_move(game, game.p2, p2_move, value2)
        cancel_move(game, game.p1, p1_move, value1)
        best_scores.append(worst_score)
    
    #return the best score if no need of the move
    best_score = -400
    for score in best_scores:
        if score>best_score:best_score=score
    if deep!=0:return best_score

    for i in range(len(p1_moves)):
        if best_scores[i]<best_score:
            to_remove.append(p1_moves[i])
    
    return to_remove

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

    def get_move(self, check_good_target, get_direction, square=False, check_target_backup = None, anti_dumb=False):
        if square and len(self.p1)==4:
            self.dir+=1
            self.dir%=4
            return MOVES[self.dir]

        move = get_direction(self, check_good_target, check_target_backup, anti_dumb)
        print(move)
        #print(move, self.dir)
        if move==None:return None
        if (move!=self.dir):
            self.dir = move
            return MOVES[move]

def play(ws, bot):
    game = Game()
    bots = [[check_apple, get_direction_bfs, True, None], [check_apple, get_direction_bfs, False, None, True], [voldemor, get_direction_bfs, False, check_apple, True]]
    while True:
        res = ws.recv()
        if (res=="2"):
            #print("check ping")
            ws.send("3")
        elif (re.search('onEnd', res)):
            game = Game()
            time.sleep(1)
            ws.send('42["playRoom"]')
            #print("game finished")
        elif (re.search("removeClientRoom", res)):
            return
        elif (re.search('updateSnakes', res)):
            #print("snake update")
            game.update_snakes(res)
            game.update_board()
            move = game.get_move(*bots[bot])
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
        print("\n\n\n\n")
        #game.print()
        #print(get_void_squares(game, game.p2))
