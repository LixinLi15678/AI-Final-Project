import math

import game_manager, game_rules, signal, unittest
from player import makePlayer
import json
import numpy as np

class GameTest(unittest.TestCase):
	def makeGame(self, size, player1, player2, depth=5, number_of_simulations=50, simulation_type='random', c_value=2.5, script=None, sdepth=5, make_graph = False) -> game_manager.GameManager:
		"""Make a game with the given parameters.

		Args:
			size (int): The size of the board.
			player1 (str): The type of player 1.
			player2 (str): The type of player 2.
			depth (int, optional): The depth of the tree, used in AB. Defaults to 5.
			number_of_simulations (int, optional): The number of simulations. Defaults to 50.
			simulation_type (str, optional): The type of simulation in MC. Defaults to 'random'.
			c_value (float, optional): The c value in MC. Defaults is 2.5 based on our tests.
			script (str, optional): The script to run. Defaults to None.
			sdepth (int, optional): The depth of the simulation. Defaults to 5.

		Returns:
			game_manager.GameManager: The game manager.
		"""
		gm = game_manager.GameManager(
		      size
		    , size
		    , makePlayer(player1, 'x', depth, number_of_simulations, c_value, simulation_type, sdepth, make_graph)
		    , makePlayer(player2, 'o', depth, number_of_simulations, c_value, simulation_type, sdepth, make_graph)
		    , script
		    , True)
		signal.signal(signal.SIGABRT, gm.interrupt)
		signal.signal(signal.SIGINT,  gm.interrupt)
		signal.signal(signal.SIGQUIT, gm.interrupt)
		signal.signal(signal.SIGALRM, gm.interrupt)
		return gm


	def test1(self):
		total = 0
		print("Testing ...")
		for i in range(100):
			gm = self.makeGame(8, 'c', 'r', number_of_simulations=100, depth=3, simulation_type="random", c_value=0, sdepth=3, make_graph=False)
			gm.play(PB=False)
			if gm.GetWinner() == "X":
				total += 1
			# print(gm.GetWinner())
			print("total: " + str(i+1) + " " + str(total) + "WINS")
		print("total: " + str(total) + " " + str(total) + "WINS")
		self.assertTrue(True)

	def test2(self):
		"""
		Test different c_value
		"""

		print("Loading history ...")
		with open('history.json', 'r') as f:
			# read the last line
			lines = f.readlines()
			temp = json.loads(lines[-1])
			num = temp['num']
		print("History loaded")

		cList = [round(x, 2) for x in list(np.arange(0, 0.401, 0.05))]
		numGame = 100
		size = 8
		type = 'random'
		simulatins = 100
		player1 = 'c'
		player2 = 'a'
		result = {}
		write = {}
		depth = 3
		sdepth = 3

		for c in cList:
			# Count the number of X win
			print(f"Testing c_value = {c} ...")
			numX = 0
			for numG in range(numGame):
				print(f"Game {numG + 1} ...")
				gm = self.makeGame(size, player1, player2, number_of_simulations=simulatins, depth=depth, simulation_type=type, c_value=c, sdepth=sdepth)
				gm.play(PB=False)
				if gm.GetWinner() == 'X':
					numX += 1
				print(f"X win {numX} times")
			result[round(c, 3)] = numX

		print("writing to json ...")
		write['num'] = num + 1
		write['size'] = size
		write['player1'] = player1
		write['player2'] = player2
		write['game'] = numGame
		write['simulations'] = simulatins
		write['ab depth'] = depth
		write['simulation'] = type
		write['simulation depth'] = sdepth
		write['result'] = result

		with open('history.json', 'a') as f:
			# write to new line
			f.write('\n')
			json.dump(write, f)

		print("Done!")
		print(result)
		self.assertTrue(True)

	def test3(self):
		print("Testing ...")
		gm = self.makeGame(8, 'c', 'r', number_of_simulations=20, depth=3, simulation_type="random", c_value=2.5, sdepth=3, make_graph=True)
		gm.play(PB=False)
		print(gm.GetWinner())
		self.assertTrue(True)


if __name__ == "__main__":
	unittest.main()
