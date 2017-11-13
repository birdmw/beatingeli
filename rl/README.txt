This is for a special module where I will be creating a genetically evolving keras neural network to play Mancala.

In my recent research I have discovered some fun methodologies. 

PREVIOUS APPROACH:

   previous to this, I have been building a network with a single output. That one output predicts a game winner. 
   The bot look at each possible next move, and then chooses the outcome which looks most like a winning game.
   About 2,000 games are were used as examples - but the quality of those games has always been limited to Monte-Carlos inspection.

NEXT APPROACH:

   Next, instead of having a single output, the network will have multiple outputs. One output for each possible action or move.
   In Mancala, each possible action is a subset of the 12 playable bins for any given move. The network will have 12 outputs and 
   the chosen move will be a chosen from the distribution of floats sitting on those output nodes - subsected by the selection of
   possible moves. 

   The CREATURE class will house a single network initialized by weights & anatomy (shape of network) exernally. 
   Each creature will have an ELO score, a mutate function, and a play function. 
   The play function will take in parameter: position (a list of bins + player whos turn it is), and will return a single
   bin which is the move it chose to play.

   The POPULATION class will house a collection of creatures. 