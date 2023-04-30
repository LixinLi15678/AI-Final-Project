from typing import Optional
import game_rules
import random
import time
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

class Node:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0

    def add_child(self, child):
        self.children.append(child)

class MonteCarloPlayer(Player):
    def __init__(self, symbol: str, time_limit: float, c: float, simulation_type: str, print_count: bool, depth: int):
        super(MonteCarloPlayer, self).__init__(symbol)
        self.time_limit = time_limit
        self.c = c
        self.depth = depth
        self.simulation_type = simulation_type
        self.simulation_count = 0
        self.print_count = print_count

    def selectInitialX(self, board: list) -> tuple:
        return (0, 0)
    def selectInitialO(self, board: list) -> tuple:
        validMoves = game_rules.getFirstMovesForO(board)
        return list(validMoves)[0]

    def getMove(self, board: list) -> tuple:
        """This function is to get the next move of the player.

        Args:
            board (list): The current state of the board.

        Returns:
            tuple: The next move of the player.
        """
        start_time = time.time()
        root = Node(board)

        self.simulation_count = 0
        while time.time() - start_time < self.time_limit:
            node = self.select_node(root)
            if node:
                result = self.run_simulation(node)
                self.backpropagate(node, result)
            else:
                break
        if self.print_count:
            print(f"Simulation count: {self.simulation_count}")

        best_move = max(root.children, key=lambda c: c.wins / c.visits if c.visits != 0 else 0).move
        return best_move

    def select_node(self, node: Node) -> Optional[Node]:
        """Selects the most promising node from the given node's children based on
            (W / N) + c * sqrt(ln(N_parent) / N).
            W is the total number of wins for the node
            N is the total number of visits for the node
            N_parent is the total number of visits for the parent node
            c is a constant determining the exploration-exploitation trade-off (higher values encourage exploration)

        Args:
            node (Node): The node to select the child from.

        Returns:
            Node: The most promising child node.
            None: If the node has no children.
        """
        if game_rules.getLegalMoves(node.state, self.symbol):
            if not node.children:
                for move in game_rules.getLegalMoves(node.state, self.symbol):
                    child_state = game_rules.makeMove(node.state, move)
                    child = Node(child_state, parent=node, move=move)
                    node.add_child(child)
            return max(node.children, key=lambda c: c.wins / c.visits + self.c * (c.parent.visits ** 0.5) / (1 + c.visits) if c.visits != 0 else 0)
        else:
            return None

    def run_simulation(self, node: Node) -> int:
        """ Runs a simulation from the given node and returns the result.

        Args:
            node (Node): The node to start the simulation from.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost,
                 and 0.5 if the game was a draw.
        """
        self.simulation_count += 1
        state = node.state
        player = self.symbol
        return self.simulate(state, player)

    def simulate(self, board: list, symbol: str) -> int:
        """ Calls the appropriate simulation function based on the simulation type.

        Args:
            board (list): The board to simulate on.
            symbol (str): The symbol to simulate with.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost,
                    and 0.5 if the game was a draw.
        """
        if self.simulation_type == "random":
            return self.random_simulation(board, symbol)
        elif self.simulation_type == "alphabeta":
            return self.alphabeta_simulation(board, symbol)
        # elif self.simulation_type == "heuristic":
        #     return self.heuristic_simulation(board, symbol)
        else:
            raise ValueError(f"Invalid simulation type: {self.simulation_type}")

    def random_simulation(self, board: list, symbol: str) -> int:
        """Simulates a game using random moves and returns the result.

        Args:
            board (list): The board to simulate on.
            symbol (str): The symbol to simulate with.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost.
        """
        state = board
        player = symbol
        depth = self.depth

        # Keep playing random moves until there are no legal moves left
        while game_rules.getLegalMoves(state, player):
            move = random.choice(game_rules.getLegalMoves(state, player))
            state = game_rules.makeMove(state, move)
            if player == 'x':
                player = 'o'
            else:
                player = 'x'

        if player == self.symbol:
            return 0
        else:
            return 1

    def alphabeta_simulation(self, board: list, symbol: str) -> int:
        """Simulates a game using the alpha-beta pruning algorithm and returns the result.

        Args:
            board (list): The board to simulate on.
            symbol (str): The symbol to simulate with.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost.
        """
        state = board
        player = symbol
        depth = self.depth
        while game_rules.getLegalMoves(state, player):
            move = random.choice(game_rules.getLegalMoves(state, player))
            state = game_rules.makeMove(state, move)
            if player == 'x':
                player = 'o'
            else:
                player = 'x'
        return 0

    def backpropagate(self, node: Node, result: int) -> None:
        while node:
            node.visits += 1
            node.wins += result
            result = -result
            node = node.parent


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


class NotImplementedException:
    def __init__(self, message): self.message = message
    def __str__(self): return self.message

def makePlayer(playerType, symbol, depth, timeLimit, cValue, sType, pt):
    player = playerType[0].lower()
    if player   == 'h': return HumanPlayer(symbol)
    elif player == 'r': return RandomPlayer(symbol)
    elif player == 'a': return AlphaBetaPlayer(symbol, depth)
    elif player == 'd': return DeterministicPlayer(symbol)
    elif player == 'c': return MonteCarloPlayer(symbol, timeLimit, cValue, sType, pt, depth)
    else: raise NotImplementedException('Unrecognized player type {}'.format(playerType))

def callMoveFunction(player, board):
    if game_rules.isInitialMove(board): return player.selectInitialX(board) if player.symbol == 'x' else player.selectInitialO(board)
    else: return player.getMove(board)
