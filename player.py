import math
import signal
from typing import Optional
from tqdm import tqdm
import game_manager
import game_rules
import random
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import textwrap

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
    def __init__(self, state, c, player, parent=None, move=None):
        self.c_param = c
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0
        self.player = player

    def __str__(self):
        return "{Board = " + str(self.state) + ", C: " + str(self.c_param) + ", Player = " + str(self.player) + ", Parent = " + str(self.parent) + ", Move: " + str(self.move) + ", Children: " + str(len(self.children)) + "}"

    def __repr__(self):
        return self.__str__()

    def add_child(self, child):
        self.children.append(child)

    def update(self, loser):
        self.visits += 1
        # 1 point earned if the loser = node.player, node.player is used for getLegalMove
        # so, you can think in the way that 1 point eared if loser != node.parent.player
        if loser == self.player:
            self.value += 1
        else:
            self.value -= 1

    def ucb1(self):
        if self.visits == 0 or self.parent is None or self.parent.visits == 0:
            return POS_INF
        return self.value / self.visits + self.c_param * math.sqrt(math.log(self.parent.visits) / self.visits)


class MonteCarloPlayer(Player):
    def __init__(self, symbol: str, number_of_simulations: int, c: float, simulation_type: str, sdepth: int, make_graph:bool):
        super(MonteCarloPlayer, self).__init__(symbol)
        self.number_of_simulations = number_of_simulations
        self.c = c
        self.simulation_type = simulation_type
        self.simulation_count = 0
        self.sdepth = sdepth
        self.make_graph = make_graph
        self.index = 0
        self.tree = None
        self.edges = []
        self.actions = []
        self.labels = {}
        self.fig = None
        self.ax = None

    def selectInitialX(self, board: list) -> tuple:
        return (0, 0)
    def selectInitialO(self, board: list) -> tuple:
        validMoves = game_rules.getFirstMovesForO(board)
        return list(validMoves)[0]

    # convert board to string displayed in the graph
    def board_to_graph_string(self, board):
        a = ""
        for row in board:
            for c in row:
                if c == ' ':
                    a += "   "
                else:
                    a += c + " "
            a = a[:-1] + "\n"
        a = a[:-1]
        return a

    def add_graph_node(self, node):
        # add labels for new node and append actions
        self.labels[node] = [self.board_to_graph_string(node.state), "Val: " + str(node.value), "Visits: " + str(node.visits), "Ucb: " + str(round(node.ucb1(), 2)), "Player: " + str(node.player)]
        self.actions.append(("add_node", node))

    def add_graph_nodes_with_edges(self, node):
        # add edges for each child for the parent node
        for child in node.children:
            self.add_graph_node(child)
            self.actions.append(("add_edge", (node, child)))

    def update_graph_nodes(self, node):
        # update node in labels
        self.actions.append(("update", (node, [self.board_to_graph_string(node.state), "Val: " + str(node.value), "Visits: " + str(node.visits), "Ucb: " + str(round(node.ucb1(), 2)), "Player: " + str(node.player)])))

    def delete_graph_node(self, node):
        self.actions.append(("del", node))


    def update(self, move):
        action, item = self.actions[move]
        self.ax.clear()

        if action == "add_node":
            self.tree.add_node(item)
        elif action == "add_edge":
            self.tree.add_edge(*item)
        elif action == "del":
            self.tree.remove_node(item)
        elif action == "update":
            node, new_labels = item
            self.labels[node] = new_labels


        pos = nx.drawing.nx_agraph.graphviz_layout(self.tree, prog='dot')
        nx.draw(self.tree, pos, with_labels=False, node_color='lightblue', node_size=2000, arrowsize=20, ax=self.ax)


        for node, (x, y) in pos.items():
            if node in self.labels:
                for i, label in enumerate(self.labels[node]):
                    # when i==0, the board size is very big, so adjust offset
                    if i > 1:
                        offset = 30 + i * 20
                    else:
                        offset = -40 + i * 90

                    self.ax.annotate(label, xy=(x, y), xytext=(5, offset), textcoords='offset points', fontweight='bold',
                                fontsize=10)

    def draw_graph(self):
        print("Starting draw graph")
        self.tree = nx.DiGraph()
        file_name = "process/MCTS Process " + str(self.index) + ".gif"
        self.fig, self.ax = plt.subplots(figsize=(40, 20))
        plt.close()
        ani = animation.FuncAnimation(self.fig, self.update, frames=len(self.actions), interval=1000, repeat=False)
        ani.save(file_name, writer='pillow', fps=1)
        print("end draw")
        self.fig = None
        self.ax = None

    def forward_propagation_update_graph(self, root:Node):
        queue = [root]

        while queue:
            cur_node = queue.pop(0)
            for child in cur_node.children:
                self.update_graph_nodes(child)
                queue.append(child)

    def getMove(self, board: list) -> tuple:
        """This function is to get the next move of the player.

        Args:
            board (list): The current state of the board.

        Returns:
            tuple: The next move of the player.
        """

        # get root node and expand it first
        root_node = Node(state=board.copy(), c=self.c, player=self.symbol)

        self.edges = []
        self.actions = []
        self.labels = {}

        # add root node in the graph
        if self.make_graph:
            self.add_graph_node(root_node)
            self.index += 1

        root_moves = game_rules.getLegalMoves(board, self.symbol)
        self.expand(root_node, root_moves)

        if len(root_moves) == 1:
            if self.make_graph:
                self.add_graph_nodes_with_edges(root_node)
                self.draw_graph()
            return root_moves[0]

        # add edges in the graph for root node
        if self.make_graph:
            self.add_graph_nodes_with_edges(root_node)

        for i in range(self.number_of_simulations):
            node = root_node

            # keep finding the optimal child until we find a leaf
            while node.children:
                node = self.select(node)

            # if this leaf have already been visited, then we expand it and choose the first child
            # if this leaf is the end of the game, which means it has no child, then we just choose this node
            if node.visits != 0:
                self.expand(node, game_rules.getLegalMoves(node.state, node.player))

                if self.make_graph:
                    self.add_graph_nodes_with_edges(node)

                node = node.children[0] if len(node.children) != 0 else node

            simulation_state, simulation_loser = self.run_simulation(node)

            temp_node = None
            if self.make_graph:
                # append a temp simulation node in the graph
                temp_node = Node(simulation_state, self.c, player = simulation_loser)
                self.add_graph_node(temp_node)
                self.actions.append(("add_edge", (node, temp_node)))


            # backpropagation
            while node is not None:
                node.update(simulation_loser)
                if self.make_graph:
                    self.update_graph_nodes(node)
                node = node.parent

            # delete the temp simulation node after update
            if self.make_graph:
                self.delete_graph_node(temp_node)
                self.forward_propagation_update_graph(root_node)

        if self.make_graph:
            self.draw_graph()
        return self.select(root_node).move

    def select(self, node):
        """This function is to get the optimal child of the node

        Args:
            node: current node.

        Returns:
            node: The best child
        """
        best_score = NEG_INF
        best_child = None
        for child in node.children:
            score = child.ucb1()
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self, node, legal_moves):
        """This function is to expand current node, get its children

        Args:
            node: current node.
            legal_moves(list): returns from game_rule.getLeagalmove

        """
        for move in legal_moves:
            new_board = game_rules.makeMove(node.state.copy(), move)
            expansion_node = Node(new_board, self.c, player='o' if node.player == 'x' else 'x', parent=node, move=move)
            node.add_child(expansion_node)

    def run_simulation(self, node: Node) -> list:
        """ Runs a simulation from the given node and returns the result.

        Args:
            node (Node): The node to start the simulation from.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost,
        """
        self.simulation_count += 1
        state = node.state
        player = node.player
        return self.simulate(state, player)

    def simulate(self, board: list, symbol: str) -> list:
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


    def random_simulation(self, board: list, symbol: str) -> list:
        """Simulates a game using random moves and returns the result.

        Args:
            board (list): The board to simulate on.
            symbol (str): The symbol to simulate with.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost.
        """
        state = board
        player = symbol
        moves = game_rules.getLegalMoves(state, player)

        # Keep playing random moves until there are no legal moves left
        while moves:
            move = random.choice(moves)
            state = game_rules.makeMove(state, move)
            player = 'o' if player == 'x' else 'x'
            moves = game_rules.getLegalMoves(state, player)

        # if we lose, value = -1, otherwise 1
        return [state, player]

    def alphabeta_simulation(self, board: list, symbol: str) -> list:
        """Simulates a game using the alpha-beta pruning algorithm and returns the result.

        Args:
            board (list): The board to simulate on.
            symbol (str): The symbol to simulate with.

        Returns:
            int: The result of the simulation. 1 if the player won, 0 if the player lost.
        """
        state = board
        player = symbol
        depth = self.sdepth
        moves = game_rules.getLegalMoves(state, player)
        while moves:
            move = self.alphabeta_getmove(state, player, depth)
            state = game_rules.makeMove(state, move)
            new_player = 'o' if player == 'x' else 'x'
            player = new_player
            moves = game_rules.getLegalMoves(state, player)

        # if we lose, value = -1, otherwise 1
        return [state, player]

    def alphabeta_getmove(self, board, player, depth) -> tuple:
        if depth == 0:
            legalMoves = game_rules.getLegalMoves(board, player)
            if len(legalMoves) > 0:
                return legalMoves[0]
            else:
                return None

        return self.alpha_beta_max_value(board, NEG_INF, POS_INF, 0, player, depth)[0]

    def alpha_beta_max_value(self, board, alpha, beta, d, player, depth):
        if d == depth:
            return None

        legalMoves = game_rules.getLegalMoves(board, player)
        if len(legalMoves) > 0:
            max_v = NEG_INF
            ans = None
            for move in legalMoves:
                new_board = game_rules.makeMove(board, move)
                tmp = self.alpha_beta_min_value(new_board, alpha, beta, d+1, player, depth)
                v = tmp if tmp is not None else self.h1(new_board, player)
                if v > max_v:
                    max_v = v
                    ans = move
                alpha = max(max_v, alpha)
                if beta <= alpha:
                    return ans if d == 0 else max_v
            return [ans, max_v] if d == 0 else max_v
        else:
            return None

    def alpha_beta_min_value(self, board, alpha, beta, d, player, depth):
        if d == depth:
            return None

        legalMoves = game_rules.getLegalMoves(board, 'o' if player == 'x' else 'x')
        if len(legalMoves) > 0:
            min_v = POS_INF
            for move in legalMoves:
                new_board = game_rules.makeMove(board, move)
                tmp = self.alpha_beta_max_value(new_board, alpha, beta, d+1, player, depth)
                v = tmp if tmp is not None else self.h1(new_board, player)
                min_v = min(min_v, v)
                beta = min(min_v, beta)
                if beta <= alpha:
                    return min_v
            return min_v
        else:
            return None


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

def makePlayer(playerType, symbol, depth, numSimulate, cValue, sType, sdepth, make_graph):
    player = playerType[0].lower()
    if player   == 'h': return HumanPlayer(symbol)
    elif player == 'r': return RandomPlayer(symbol)
    elif player == 'a': return AlphaBetaPlayer(symbol, depth)
    elif player == 'd': return DeterministicPlayer(symbol)
    elif player == 'c': return MonteCarloPlayer(symbol, numSimulate, cValue, sType, sdepth, make_graph)
    else: raise NotImplementedException('Unrecognized player type {}'.format(playerType))

def callMoveFunction(player, board):
    if game_rules.isInitialMove(board): return player.selectInitialX(board) if player.symbol == 'x' else player.selectInitialO(board)
    else: return player.getMove(board)
