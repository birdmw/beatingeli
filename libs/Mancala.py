from pathos.multiprocessing import ProcessingPool
import random
from time import time


class Board:
    def __init__(self):
        """
        self.pos (board position) is all of the information available to an otherwise human player
        """

        # position 0 and 7 are the mancalas for player 2 and player 1
        # player_1 starts
        self.pos = {0: 0, 7: 0, "turn": 'player_1'}

        # start with holes 1-7 and holes 8-14 having 4 stones each
        for i in range(1, 7) + range(8, 14):
            self.pos[i] = 4

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
            raise ValueError('Invalid Move')

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


class Dojo:
    def __init__(self, p1, p2, board):
        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.history = []

    def play_one_game(self, rand_sample=False, v=0):
        while self.board.pos['turn']:
            if v:
                self.board.print_()
                print(self.board.pos['turn'] + "'s turn")
            if self.board.pos['turn'] == 'player_1':
                move = self.p1(self.board.pos)
            else:  # self.board.pos['turn'] == 'player_2'
                move = self.p2(self.board.pos)
            if v:
                print(self.board.pos['turn'], "plays", move)
            self.board.play(move)
        if v:
            self.board.print_()
            print("winner is " + self.board.winner)
        if rand_sample:
            sample = dict(random.choice(self.board.history))
            sample['winner'] = self.board.winner
            # self.history.append(sample)
            return sample
        return

    def play_many_games(self, count, v=0, multi=False):
        if multi:
            data = [(True, 0,)] * count
            results = ProcessingPool().map(self.play_one_game, data)
            print len(results)

        if not multi:
            t = time()
            for c in range(count):
                self.play_one_game(rand_sample=True)
                self.board.reset()
                if v:
                    if time() > t + 3:
                        print(c)
                        t += 3


def random_bot(pos):
    if pos['turn'] == 'player_1':
        return random.choice(filter(lambda x: pos[x] > 0, range(1, 7)))
    elif pos['turn'] == 'player_2':
        return random.choice(filter(lambda x: pos[x] > 0, range(8, 14)))


if __name__ == "__main__":
    p1 = random_bot
    p2 = p1
    b = Board()
    d = Dojo(p1, p2, b)
    # d.play_one_game(rand_sample=True, v=0)
    # print d.history
    d.play_many_games(1000, v=1, multi=True)
    # print len(d.history)
