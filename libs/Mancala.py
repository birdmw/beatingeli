class Board:
    def __init__(self):
        """
        self.pos (board position) is all of the information available to an otherwise human player
        """

        # position 0 and 7 are the mancalas for player 2 and player 1
        # player_1 starts
        self.pos = {0: 0, 7: 0, "turn": 'player_1'}

        # start with bins 1-7 and bins 8-14 having 4 stones each
        for i in range(1, 7) + range(8, 14):
            self.pos[i] = 4

        # Each board has an associated history of positions
        self.history = [dict(self.pos)]

        # Record the winner
        self.winner = None

    def play(self, bin):
        """
        Play takes in a chosen bin, and updates self.pos (board position) as per the rules of the game
        Player 1 can play bins 1 to 6. Player 2 can play bins 8 to 13. A chosen bin should not be empty.
        :param bin: int
        :return:
        """

        # Set your mancala bin based on who's turn it is
        mancala = 7 if "1" in self.pos["turn"] else 0
        # As well set your opponents
        opp_mancala = 0 if "1" in self.pos["turn"] else 7

        # Declare which bins are the current players
        if mancala:  # mancala == 7
            my_bins, opp_bins = range(1, 7), range(8, 14)
        else:  # mancala == 0
            my_bins, opp_bins = range(8, 14), range(1, 6)

        if not self.pos['turn']:
            print("Game Over.")
            return

        if self.pos[bin] == 0 or bin not in my_bins:
            raise ValueError('Invalid Move')

        # If bins 1-7 have no stones, bins 8-14 pour into player 2's mancala
        if sum([self.pos[i] for i in range(1, 7)]) == 0:
            # Count up the stones
            stones = sum([self.pos[i] for i in range(8, 14)])
            # Empty the bins
            for i in range(8, 14):
                self.pos[i] = 0
            # Add the stones to the mancala
            self.pos[0] += stones
            # The board is empty, so it is nobodies turn
            self.pos['turn'] = None

        # If bins 8-14 have no stones, bins 1-7 pour into player 1's mancala
        elif sum([self.pos[i] for i in range(8, 14)]) == 0:
            # Count up the stones
            stones = sum([self.pos[i] for i in range(1, 7)])
            # Empty the bins
            for i in range(1, 7):
                self.pos[i] = 0
            # Add the stones to the mancala
            self.pos[7] += stones
            # The board is empty, so it is nobodies turn
            self.pos['turn'] = None

        # If it is someones turn to play
        if self.pos['turn']:
            # Count stones from chosen bin
            stones = self.pos[bin]
            # Empty bin from which stones are taken
            self.pos[bin] = 0
            # Go around the board placing stones one at a time
            for s in range(stones):
                bin += 1
                # Loop around at bin 13
                if bin == 14:
                    bin = 0
                # Skip opponents mancala
                if bin == opp_mancala:
                    bin += 1
                # Add stone to bin
                self.pos[bin] += 1

            # If your turn ends in one of your own bins,
            # and it was previously empty,
            # and there are opponent stones on the opposite side
            if self.pos[bin] == 1 and bin in my_bins and self.pos[14 - bin]:
                # Place the one stone from your own bin into your mancala
                self.pos[mancala] += self.pos[bin]
                self.pos[bin] = 0
                # As well as the stones from the opposing bin
                self.pos[mancala] += self.pos[14 - bin]
                self.pos[14 - bin] = 0

            # Change players if final stone was not in the players own mancala
            if bin != mancala:
                if self.pos["turn"] == 'player_1':
                    self.pos["turn"] = "player_2"
                else:  # mancala == 0
                    self.pos["turn"] = "player_1"

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

    def print_(self):
        print("======BOARD========")
        print("Left Mancala:", self.pos[0])
        print([str(self.pos[i]) for i in range(8, 14)[::-1]])
        print([str(self.pos[i]) for i in range(1, 7)])
        print("Right Mancala:", self.pos[7])
        print("===================")
