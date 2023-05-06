# AI-Final-Project
### By Zining(Kimi) Liu & Lixin(Leo) Li

In this project, we use tree graph visualization, which requires pygraphviz. For installing, you can read [here](https://pygraphviz.github.io/documentation/stable/install.html). 



## Introduction Monte Carlo Tree Search

### Background ###

[Monte Carlo Tree Search (MCTS)](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search) is a widely-used algorithm for decision-making in artificial intelligence and game playing. 
Combining Monte Carlo simulation with tree search, MCTS efficiently explores large state spaces to find optimal solutions. 
It has been notably successful in games like Go and Chess, enabling groundbreaking achievements in AI systems. MCTS is ideal 
for problems with vast search spaces and expensive state evaluations, where traditional search methods fall short.

![MCTS Board](pictures/MCTS_intro.jpg)


The game we choose is [konane](https://en.wikipedia.org/wiki/Konane) which is a strategy game played between two players.


![Konane Board](pictures/board.jpg "Board")

## PyGraphviz ##
We use PyGraphviz to draw a tree graph in each Game for testing our algorithm Manually. This visualization shows all actions of MCTS. Each `.gif` files
is one move in one game. For example, `MCTS Process 1.gif` means the first move. 

Because the time cost of MCTS itself and drawing each graph with PyGraphviz is quite high. Moreover, if you want to increase 
the number of simulations for each move in MCTS, the time it takes to run an entire game can even reach 8 hours or more as 
the number of simulations increases. For this reason, we have already run an entire game for you, which you can check in 
the process folder. All the `.gif` files comes from test3 in `test.py`, you can check all the parameters(ex. c value, simulation type ...) in test3.

You can read `Implementation` section to help you understand each graph in the .gif file.


If you want to try this feature yourself, you can read `test.py` section. 

## implementation ##
We learn the specific algorithm by watching this [video](https://www.youtube.com/watch?v=UXW2yZndl7U) on YouTube and playing this [project](https://vgarciasc.github.io/mcts-viz/),
and our general idea is basically the same as these. So, we highly recommend that you watch this video and try out the program.

### Explanation ###
Next we will explain MCTS to you in detail containing information for all functions and variables. We also have comments for each function, you can go to `player.py` to get more information：

1.This is a root node. MCTS will determine the next move.(this example comes from test3 in `test.py`: ` number_of_simulations=20`, `simulation_type="random"`, `c_value=2.5`, you can check the whole game in process folders)
![MCTS Board](pictures/root.jpg)

2.Next, MCTS will expand the root node and get all the children of the node. Just for root node, If there is only one child of the root node, then our MCTS will not do any simulation, just choose this move.
![MCTS Board](pictures/expand1.jpg)

3.Each new node's `ucbi` value is positive infinite, and after expand, the program will choose one path with highest `ucbi` value until reaching a leaf node. MCTS will check if this leaf node has already been visited. If we haven't visited this node, then we will do a simulation for this leaf node, otherwise, we will expand it and choose the left most child to be the leaf node. The leftmost new Node of the root node is chosen first. And program will do a simulation for it. If the simulation type is `random`,then two random players will move by turn until the end. Similarly, if the simulation type is `alphabeta`,then two alphabeta players will move by turn until the end.
![MCTS Board](pictures/simulation1.jpg)
![MCTS Board](pictures/addsimulation.jpg)

4.After the simulation is completed, the simulation returns a loser(the player of the simulation node is the loser) and MCTS will do the backpropagation which will update each node's value. 1 means wins and 0 means lose. 1 and 0 also depends on the layer of each node which is similar to minimax. More explanation is in `Class Node` section, especially `self.value`. Process: backpropagation -> remove simulation root node -> forward propagation(which is just for drawing graph and help debugging, and it is not a normal step for MCTS, you can read `forward_propagation_update_graph()` in `PyGraphviz Drawing Graph Functions` section)
![MCTS Board](pictures/backpropagation.jpg)
![MCTS Board](pictures/remove%20simulatin.jpg)
![MCTS Board](pictures/forward1.jpg)

5.After doing the same things for all the children of the root node, we will get:
![MCTS Board](pictures/first_layer.png)

6.Then, MCTS calls `select()` function and choose one path with the most optimal `ucbi` from the root node to a leaf node. It will choose the Leftmost path and we have already visited the leftmost node. So, the program will expand the left most leaf node and choose the left most child to be the leaf node.
![MCTS Board](pictures/leftmost.png)

7.Do the simulation for this node.
![MCTS Board](pictures/simulation2.png)
![MCTS Board](pictures/simulation2.5.png)

8.Next, backpropagate the result. You can see that, `o` lose and the value of the leftmost node in the third layer is not added by 1 although the player of this node is `x`. This is because the actual player of this node is `o`, `x` is used for `rule.getLeagalMove` for the children of this node.
![MCTS Board](pictures/back1.png)
![MCTS Board](pictures/back1.5.png)
![MCTS Board](pictures/back1.6.png)

9.Because ![](pictures/math.jpg) depends on parent's visits. we will remove the simulation root node first and do a forward propagation for each node just for debugging. 
![MCTS Board](pictures/remove3.png)
![MCTS Board](pictures/forward3.png)
![MCTS Board](pictures/forward3_1.png)
![MCTS Board](pictures/forward3_2.png)
![MCTS Board](pictures/forward3_3.png)
![MCTS Board](pictures/forward3_4.png)

10.Next, MCTS kept doing samethings until the number of simulations becomes 20. We will omit the remaining steps and just give you the end of this move. You can check all `.gif` files in `process` folders.
![MCTS Board](pictures/end.png)

#### Class Node ####
- `self.c_param`(int) - C value of MCTS
- `self.state`(2d array) - The board of game represented by a node
- `self.move`(tuple) - One move of game. After `self.move`, the board of the game becomes `self.state`
- `self.children`(list of Node) - List of Node. Children of this node
- `self.visits`(int) - The number of times we visit this point
- `self.player`(char) - This is used for `game_rules.getmove`, which means the next player of `self.state`
- `self.value`(int) - The score of this point. If the loser of this node's simulation or this node's children's simulations is self.player, `self.value` += 1. That is because `self.player` is the next play of `self.state`.
- `add_child()` -  Function. Add children for this node.
- `update()` - Function. Updating `self.visit` and `self.value`.
- `ucb1()` - Function. Get the ![](pictures/math.jpg) of one node.

#### class MonteCarloPlayer(Player) ####
- `self.number_of_simulations`(int) - determine how many simulations of one move will be
- `self.c`(int) - C value of MCTS.
- `self.simulation_type`(string) - `random` means MCTS uses random simulation, `alphabeta` means MCTS uses alphabeta simulation.
- `self.simulation_count`(int) - record how many simulations have already completed of one move
- `self.sdepth`(int) - Depth of alphabeta simulation.
- `self.make_graph`(bool) - decide whether MCTS will draw `.gif` graphs
- `self.index `(int) - record the index of each move, used for determining the name of each `.gif` file in `process` folders
- `self.tree` - used for drawing graph
- `self.edges`(list) - All edges of MCTS used for drawing graph
- `self.actions`(list) - All the actions of MCTS used for drawing graph
- `self.labels`(Dict) - All nodes' information used for drawing graph
- `self.fig` - used for drawing graph
- `self.ax` - used for drawing graph

1.**PyGraphviz Drawing Graph Functions**
- `board_to_graph_string()` -  Convert A game board to string which will be used for node's name when drawing graph.
- `add_graph_node()` - Add a node in `self.labels` and `self.actions`
- `add_graph_nodes_with_edges()` - given a node, add all its children in `self.labels` and `self.actions`, and create edges with this node and its children is `self.children`
- `update_graph_nodes()` - updating a node's information by add actions in `self.actions`
- `delete_graph_node()` - add actions for deleting one node in`self.actions`
- `update()` -  Used for drawing graph.
- `draw_graph()` -  used for drawinng graph.
- `forward_propagation_update_graph()` - updating each node's information forwardly from root node. This function is just for drawing graph and will not be called if `self.makegraph = false`. Because each node's information is realtime, you can just get a node's variable at any time, but you cannot do this when drawing graph. A node's `ucbi` is decided by its parent, after normal backpropagation, we need forwardpropagation to update each node's information for drawing graph.

2.**MCTS Functions**
- `getMove()` - Get one move from MCTS.
- `select()` - Select the optimal path and choose a leaf node with highest `ucbi`
- `expand()` - expand one node, use `game_rules.getLegalMove` to get this node's move. Set each move to a node and add them to this node's children.
- `run_simulation()` -run one simuation
- `simulate()` - choose `random` simulation or `alphabeta` simulation.
- `random_simulation()` - execute a `random` simulation. Given the board and first player, two players do random choice by turn.
- `alphabeta_simulation()` - execute an `alphabeta` simulation. Given the board, first player, and depth, two players do random choice by turn.
- `alphabeta_getmove()` - which is the implementation of HW4
- `alpha_beta_max_value()` - which is the implementation of HW4
- `alpha_beta_min_value()` - which is the implementation of HW4


## Testing MCTS ###
We evaluate our MCTS algorithm by just examining the PyGraphviz Graph manually. Writing tests for MCTS is challenging because 
all variables are determined by the outcomes of simulations, and it is impossible to predict the results of random simulations 
beforehand. Similarly, if we use alpha-beta simulations, we would need to anticipate all outcomes of the alpha-beta algorithm 
first, which is undoubtedly a difficult and time-consuming task. All random and alpha-beta simulations have already been 
implemented and thoroughly tested in Homework 4. As a result, utilizing PyGraphviz to draw graphs and debug step by step 
has become a relatively simple and highly convenient approach for us.

### test.py ###


**gm = self.makeGame**

In test.py, you can use `gm = self.makeGame` to create one game. Here is all the parameters:

-`size`(int) - Size of the game board
-`player1`(char) - The first player
-`player2`(char) - The second player
-`depth`)(int) - The depth for `Alphabeta`
-`number_of_simulations`(int) - how many simulations of one MCTS move will be
-`simulation_type` - choose `random` simulation or `alphabeta` simulation of MCTS
-`c_value` - Value of c for MCTS
-`sdepth` - depth for MCTS's `alphabeta simulation`
-`make_graph` - `make_graph = true` means MCTS will draw `.gif` files, `make_graph = false` means MCTS will not draw `.gif` files

`test1`
This test is used for run a single game

`test2`
This test is used for exploring `c` and write the result into `history.json`. 

`test3`
This test is used for Drawing graph. We just the number of simulations in each move to 20, because this is just used for
testing the algorthm Manually






