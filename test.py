import math

import game_manager, game_rules, signal, unittest
from player import makePlayer
import json

class GameTest(unittest.TestCase):
	def makeGame(self, size, player1, player2, depth=5, number_of_simulations=50, simulation_type='random', c_value=1.414, script=None, pt=False):
		gm = game_manager.GameManager(
		      size
		    , size
		    , makePlayer(player1, 'x', depth, number_of_simulations, c_value, simulation_type, pt)
		    , makePlayer(player2, 'o', depth, number_of_simulations, c_value, simulation_type, pt)
		    , script
		    , True)
		signal.signal(signal.SIGABRT, gm.interrupt)
		signal.signal(signal.SIGINT,  gm.interrupt)
		signal.signal(signal.SIGQUIT, gm.interrupt)
		signal.signal(signal.SIGALRM, gm.interrupt)
		return gm

	def test1(self):
		total = 0
		for i in range(10):
			gm = self.makeGame(8, 'c', 'r', number_of_simulations=50, depth=3, simulation_type="alphabeta", c_value=2, pt=True)
			gm.play(PB=False)
			if gm.GetWinner() == "X" or "x":
				total += 1
		print(total, "WINS")
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

		cList = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
		numGame = 10
		size = 8
		type = 'random'
		simulatins = 50
		player1 = 'c'
		player2 = 'r'
		result = {}
		write = {}
		depth = 3

		for c in cList:
			# Count the number of X win
			print(f"Testing c_value = {c} ...")
			numX = 0
			for numG in range(numGame):
				print(f"Game {numG + 1} ...")
				gm = self.makeGame(size, player1, player2, number_of_simulations=100, depth=depth, simulation_type=type, c_value=c, pt=True)
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
		write['depth'] = depth
		write['simulation'] = type
		write['result'] = result

		with open('history.json', 'a') as f:
			# write to new line
			f.write('\n')
			json.dump(write, f)

		print("Done!")
		print(result)
		self.assertTrue(True)

	# Add more tests here

	# def test4(self):
	# 	# alphabeta vs mc
	# 	p1 = 'c'
	# 	p2 = 'a'
	# 	depth = 3
	# 	total = 0
	# 	for i in range(10):
	# 		print(f"Game {i+1}:")
	# 		gm = self.makeGame(8, p1, p2, depth, timeLimit=15.0, simulation_type='alphabeta', c_value=math.sqrt(5))
	# 		gm.play(PB=False)
	# 		if gm.GetWinner() == "X" or "x":
	# 			total += 1
	# 		print(f"{gm.GetWinner()} wins")
	# 	print(total, "WINS")
	# 	self.assertTrue(True)
	#
	# def test5(self):
	# 	# alphabeta vs mc
	# 	p1 = 'c'
	# 	p2 = 'a'
	# 	depth = 3
	# 	total = 0
	# 	for i in range(10):
	# 		print(f"Game {i+1}:")
	# 		gm = self.makeGame(8, p1, p2, depth, timeLimit=15.0, simulation_type='random', c_value=math.sqrt(5))
	# 		gm.play(PB=False)
	# 		if gm.GetWinner() == "X" or "x":
	# 			total += 1
	# 		print(f"{gm.GetWinner()} wins")
	# 	print(total, "WINS")
	# 	self.assertTrue(True)

if __name__ == "__main__":
	unittest.main()
