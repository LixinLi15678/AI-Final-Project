import game_rules, random
###########################################################################
# Explanation of the types:
# The board is represented by a row-major 2D list of characters, 0 indexed
# A point is a tuple of (int, int) representing (row, column)
# A move is a tuple of (point, point) representing (origin, destination)
# A jump is a move of length 2
###########################################################################

# I will treat these like constants even though they aren't
# Also, these values obviously are not real infinity, but close enough for this purpose
NEG_INF = -1000000000
POS_INF = 1000000000

class Player(object):
    """ This is the player interface that is consumed by the GameManager. """
    def __init__(self, symbol): self.symbol = symbol # 'x' or 'o'

    def __str__(self): return str(type(self))

    def selectInitialX(self, board): return (0, 0)
    def selectInitialO(self, board): pass

    def getMove(self, board): pass

    def h1(self, board, symbol):
        return -len(game_rules.getLegalMoves(board, 'o' if self.symbol == 'x' else 'x'))

# This class has been replaced with the code for a deterministic player.
class AlphaBetaPlayer(Player):
    def __init__(self, symbol, depth):
        super(AlphaBetaPlayer, self).__init__(symbol)
        self.depth = depth

    # Leave these two functions alone.
    def selectInitialX(self, board): return (0,0)
    def selectInitialO(self, board):
        validMoves = game_rules.getFirstMovesForO(board)
        return list(validMoves)[0]

    # Edit this one here. :)
    def getMove(self, board) -> tuple:
        return self.AlphaBetaSearch(board)[1]

    def AlphaBetaSearch(self, board, a=NEG_INF, b=POS_INF, depth=None, symbol=None, maximizing_player=True) -> tuple:
        """
        Returns the maximum/minimum value of the board, depending on isMaximizing.
        args:
            board: the board to evaluate
            a: the alpha value
            b: the beta value
            depth: the depth of the search
            symbol: the symbol to evaluate
            maximizing_player: a boolean value indicating whether to perform a max or min operation
        returns:
            a tuple of (value, move)
        """
        # set default values
        if depth is None:
            depth = self.depth
        if symbol is None:
            symbol = self.symbol
        # set best value
        if maximizing_player:
            bestMove = (NEG_INF, None)
        else:
            bestMove = (POS_INF, None)
        legalMoves = game_rules.getLegalMoves(board, symbol)
        # If no legal moves or end of tree, return
        if len(legalMoves) == 0 or depth == 0:
            return (self.h1(board, symbol), None)
        # loop through all legal moves
        for i in range(len(legalMoves)):
            nextMove = game_rules.makeMove(board, legalMoves[i])
            val = self.AlphaBetaSearch(nextMove, a, b, depth - 1, 'o' if symbol == 'x' else 'x', not maximizing_player)[0]
            # get max/min value
            if maximizing_player:
                if bestMove[0] < val:
                    bestMove = (val, legalMoves[i])
                if bestMove[0] >= b:
                    return bestMove
                a = max(a, bestMove[0])
            else:
                if bestMove[0] > val:
                    bestMove = (val, legalMoves[i])
                if bestMove[0] <= a:
                    return bestMove
                b = min(b, bestMove[0])
        return bestMove

class MonteCarloPlayer(Player):
    def __init__(self, symbol, num_trials):
        super(MonteCarloPlayer, self).__init__(symbol)
        self.num_trials = num_trials

    def selectInitialX(self, board): return (0, 0)
    def selectInitialO(self, board):
        validMoves = game_rules.getFirstMovesForO(board)
        return list(validMoves)[0]

    def getMove(self, board) -> tuple:
        pass

class RandomPlayer(Player):
    def __init__(self, symbol):
        super(RandomPlayer, self).__init__(symbol)

    def selectInitialX(self, board):
        validMoves = game_rules.getFirstMovesForX(board)
        return random.choice(list(validMoves))

    def selectInitialO(self, board):
        validMoves = game_rules.getFirstMovesForO(board)
        return random.choice(list(validMoves))

    def getMove(self, board):
        legalMoves = game_rules.getLegalMoves(board, self.symbol)
        if len(legalMoves) > 0: return random.choice(legalMoves)
        else: return None


class DeterministicPlayer(Player):
    def __init__(self, symbol): super(DeterministicPlayer, self).__init__(symbol)

    def selectInitialX(self, board): return (0,0)
    def selectInitialO(self, board):
        validMoves = game_rules.getFirstMovesForO(board)
        return list(validMoves)[0]

    def getMove(self, board):
        legalMoves = game_rules.getLegalMoves(board, self.symbol)
        if len(legalMoves) > 0: return legalMoves[0]
        else: return None


class HumanPlayer(Player):
    def __init__(self, symbol): super(HumanPlayer, self).__init__(symbol)
    def selectInitialX(self, board): raise NotImplementedException('HumanPlayer functionality is handled externally.')
    def selectInitialO(self, board): raise NotImplementedException('HumanPlayer functionality is handled externally.')
    def getMove(self, board): raise NotImplementedException('HumanPlayer functionality is handled externally.')


def makePlayer(playerType, symbol, depth=1):
    player = playerType[0].lower()
    if player   == 'h': return HumanPlayer(symbol)
    elif player == 'r': return RandomPlayer(symbol)
    elif player == 'a': return AlphaBetaPlayer(symbol, depth)
    elif player == 'd': return DeterministicPlayer(symbol)
    elif player == 'c': return MonteCarloPlayer(symbol, depth)
    else: raise NotImplementedException('Unrecognized player type {}'.format(playerType))

def callMoveFunction(player, board):
    if game_rules.isInitialMove(board): return player.selectInitialX(board) if player.symbol == 'x' else player.selectInitialO(board)
    else: return player.getMove(board)
