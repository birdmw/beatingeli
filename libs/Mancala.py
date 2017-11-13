import keras
from csv import DictWriter
from multiprocessing import Pool, cpu_count
from os import sep
from random import random, choice
from time import time


class Board:
    def __init__(self, pos=None, record_history=True):
        """
        self.pos (board position) is all of the information available to an otherwise human player
        """
        self.record_history = record_history
        if pos:
            self.pos = dict(pos)
        else:
            # position 0 and 7 are the mancalas for player 2 and player 1
            # player_1 starts
            self.pos = {0: 0, 7: 0, "turn": 'player_1', 'move_number': 0}

            # start with holes 1-7 and holes 8-14 having 4 stones each
            for i in range(1, 7) + range(8, 14):
                self.pos[i] = 4

        if self.record_history:
            # Each board has an associated history of positions
            self.history = [dict(self.pos)]

        # Record the winner
        self.winner = None

    def play(self, hole):
        """
        Play takes in a chosen hole, and updates self.pos (board position) as per the rules of the game
        Player 1 can play holes 1 to 6. Player 2 can play holes 8 to 13. A chosen hole should not be empty.
        :param hole: int
        :return:
        """

        self.pos['move_number'] += 1

        # Set your mancala hole based on who's turn it is
        mancala = 7 if "1" in self.pos["turn"] else 0
        # As well set your opponents
        opp_mancala = 0 if "1" in self.pos["turn"] else 7

        # Declare which holes are the current players
        if mancala:  # mancala == 7
            my_holes, opp_holes = range(1, 7), range(8, 14)
        else:  # mancala == 0
            my_holes, opp_holes = range(8, 14), range(1, 6)

        if not self.pos['turn']:
            print("Game Over.")
            return

        if self.pos[hole] == 0 or hole not in my_holes:
            print("invalid move")
            return

        # Sweep checks if one side is completely empty
        # self.sweep()

        # If it is someones turn to play
        if self.pos['turn']:
            # Count stones from chosen hole
            stones = self.pos[hole]
            # Empty hole from which stones are taken
            self.pos[hole] = 0
            # Go around the board placing stones one at a time
            for s in range(stones):
                hole += 1
                # Loop around at hole 13
                if hole == 14:
                    hole = 0
                # Skip opponents mancala
                if hole == opp_mancala:
                    hole += 1
                # Add stone to hole
                self.pos[hole] += 1

            # If your turn ends in one of your own holes,
            # and it was previously empty,
            # and there are opponent stones on the opposite side
            if self.pos[hole] == 1 and hole in my_holes and self.pos[14 - hole]:
                # Place the one stone from your own hole into your mancala
                self.pos[mancala] += self.pos[hole]
                self.pos[hole] = 0
                # As well as the stones from the opposing hole
                self.pos[mancala] += self.pos[14 - hole]
                self.pos[14 - hole] = 0

            # Change players if final stone was not in the players own mancala
            if hole != mancala:
                if self.pos["turn"] == 'player_1':
                    self.pos["turn"] = "player_2"
                else:  # mancala == 0
                    self.pos["turn"] = "player_1"
                    # Sweep checks if one side is completely empty
                    # We have to do this check again since
        self.sweep()

        if not self.winner:
            if self.record_history:
                self.history.append(dict(self.pos))

        # A player wins when they have over 24 stones in their mancala
        if self.pos[0] > 24:
            self.winner = 'player_2'
            self.pos['turn'] = None
        elif self.pos[7] > 24:
            self.winner = 'player_1'
            self.pos['turn'] = None
        elif self.pos[0] == 24 == self.pos[7]:
            self.winner = 'tie'
            self.pos['turn'] = None

    def sweep(self):
        # If holes 1-7 have no stones, holes 8-14 pour into player 2's mancala
        if sum([self.pos[i] for i in range(1, 7)]) == 0:
            # Count up the stones
            stones = sum([self.pos[i] for i in range(8, 14)])
            # Empty the holes
            for i in range(8, 14):
                self.pos[i] = 0
            # Add the stones to the mancala
            self.pos[0] += stones
            # The board is empty, so it is nobodies turn
            self.pos['turn'] = None

        # If holes 8-14 have no stones, holes 1-7 pour into player 1's mancala
        elif sum([self.pos[i] for i in range(8, 14)]) == 0:
            # Count up the stones
            stones = sum([self.pos[i] for i in range(1, 7)])
            # Empty the holes
            for i in range(1, 7):
                self.pos[i] = 0
            # Add the stones to the mancala
            self.pos[7] += stones
            # The board is empty, so it is nobodies turn
            self.pos['turn'] = None

    def print_(self):
        print("======BOARD========")
        print("Left Mancala:", self.pos[0])
        print([str(self.pos[i]) for i in range(8, 14)[::-1]])
        print([str(self.pos[i]) for i in range(1, 7)])
        print("Right Mancala:", self.pos[7])
        print("===================")

    def reset(self):
        self.__init__()


def play_one_game(params):
    player_tuple, snapshot, v, board, first_move = params
    f_move = first_move
    p1, p2 = player_tuple[0], player_tuple[1]
    if snapshot:
        history = []
    board = Board() if not board else board
    while board.pos['turn']:
        if v:
            board.print_()
            print(board.pos['turn'] + "'s turn")
        if snapshot:
            history.append(dict(board.pos))
        if board.pos['turn'] == 'player_1':
            move = p1(board.pos)
        else:  # self.board.pos['turn'] == 'player_2'
            move = p2(board.pos)
        if v:
            print("**************************" + board.pos['turn'], "plays", move)
        if first_move:
            board.play(first_move)
            first_move = None
        else:
            board.play(move)

    if v:
        board.print_()
        print("winner is " + board.winner)
    if snapshot:
        history.append(dict(board.pos))
        game_record = {'history': history, 'winner': board.winner}
        snapshot = choice(game_record['history'])
        snapshot['winner'] = game_record['winner']
        return snapshot
    if f_move:
        return board.winner, f_move
    return board.winner


def play_many_games(params, count, multi=True):
    player_tuple, snapshot, v, board, first_move = params
    snapshot_collection = []
    if multi:
        pool = Pool(processes=cpu_count())
        sequence = [params] * count
        snapshot_collection = pool.map(play_one_game, sequence)
        pool.close()
        pool.join()

    else:  # not multiprocessed
        t = time()
        board = Board()
        for c in range(count):
            snapshot = play_one_game(params)
            snapshot_collection.append(snapshot)
            board.reset()
            if time() > t + 3:
                print(c)
                t += 3
    return snapshot_collection


def random_bot(pos):
    if pos['turn'] == 'player_1':
        return choice(filter(lambda x: pos[x] > 0, range(1, 7)))
    elif pos['turn'] == 'player_2':
        return choice(filter(lambda x: pos[x] > 0, range(8, 14)))

def nnet(pos):
    global nnet_model
    try:
        nnet_model
    except:
        filepath = 'nnet.pkl'
        keras.models.load_model(filepath)
    #TODO: make a board with pos
    #TODO: make a function that converts a pos to an array for the nnet
    #TODO: make a list of possible_moves (use randombots logic without the choice piece)
    #TODO: for each possible move, make a copy of the board and play that one move,
    #           then predict the winner making tuples along the way 
    #TODO: rectify predictions to 1-prediction if global board.pos is player_1
    #TODO: make a weighted_choice and return it


def monte_carlo(pos, seconds=20, bot=None, multi=True, v=1):
    if not bot:
        bot = random_bot
    start = time()
    stop = start + seconds
    if pos['turn'] == 'player_1':
        legal_plays = set(filter(lambda x: pos[x] > 0, range(1, 7)))
    elif pos['turn'] == 'player_2':
        legal_plays = set(filter(lambda x: pos[x] > 0, range(8, 14)))
    else:
        return None
    if not legal_plays:
        return None
    elif len(legal_plays) == 1:
        return legal_plays.pop()
    else:
        player = pos['turn']
        enemy = 'player_2' if player == 'player_1' else 'player_1'
        move_scores = {k: {'player_1': 1, 'player_2': 1, 'tie': 0} for k in legal_plays}
        board = Board(pos=dict(pos), record_history=False)
        if v:
            trials = 0
        legal_list = list(legal_plays)
        while time() <= stop:
            if multi:
                pool = Pool(processes=cpu_count())
                count = 10000 * int(seconds) * int(cpu_count() / 16.)
                seq = [((bot, bot), False, 0, Board(dict(pos)), choice(legal_list),) for _ in range(count)]
                winner_collection = pool.map(play_one_game, seq)
                pool.close()
                pool.join()
                for (winner, chosen) in winner_collection:
                    move_scores[chosen][winner] += 1
                trials += count
            else:  # not multi
                pos_copy = dict(pos)
                board.pos = pos_copy
                chosen = choice(legal_list)  # for multiprocessing this will need to be a comprehension
                winner, chosen = play_one_game(((bot, bot), False, 0, board, chosen))
                # print "12341234"
                # print winner, chosen
                # print move_scores.keys()
                # print "asdfasdfs"
                move_scores[chosen][winner] += 1
                trials += 1
        if v > 1:
            print(str(trials) + " trials")

        move_percents = []
        for move in move_scores.keys():
            move_percents.append((move, move_scores[move][player] / float(move_scores[move][enemy])))

        move = weighted_choice(move_percents, power=1)
        return move


class Human:
    def __init__(self):
        pass

    def __call__(self, pos):
        board = Board(dict(pos))
        # board.print_()
        bin = input("Enter Bin: ")
        print(int(bin))
        return int(bin)


def weighted_choice(my_list, power=1):
    my_list = [(a, b ** power) for (a, b) in my_list]
    max_ = sum([m[1] for m in my_list])
    threshold = random() * max_
    sum_ = 0
    for (item, value) in my_list:
        sum_ += value
        if threshold <= sum_:
            return item


def data_to_csv(data, file_path):
    keys = data[0].keys()
    with open(file_path, 'wb') as output_file:
        dict_writer = DictWriter(output_file, keys, lineterminator='\n')
        dict_writer.writeheader()
        dict_writer.writerows(data)


if __name__ == "__main__":
    # players = (random_bot, random_bot)
    # records = play_many_games(player_tuple=players, count=100000, multi=True)
    # data_to_csv(records, sep.join(['..', 'data', 'games.csv']))

    p1, p2 = 0, 0
    H = Human()
    for i in range(1):
        players = (monte_carlo, monte_carlo)
        # # player_tuple, snapshot, v, board, first_move
        # params = players, False, 0, None, None
        # winner = play_one_game(params=params)
        params = players, True, 0, None, None
        for j in range(5)[1:]:
            print(j)
            snapshot_collection = play_many_games(params=params, count=j, multi=False)
            data_to_csv(snapshot_collection, sep.join(['..', 'data', str(time()) + '.csv']))

            # if '1' in winner:
            #     p1 += 1
            # if '2' in winner:
            #     p2 += 1
            # print "p1=", p1, " p2=", p2
