import math

import game_manager, game_rules, signal, unittest
from player import makePlayer
import json

class GameTest(unittest.TestCase):
	def makeGame(self, size, player1, player2, depth=5, timeLimit=2.0, simulation_type='random', c_value=1.414, script=None, pt=False):
		gm = game_manager.GameManager(
		      size
		    , size
		    , makePlayer(player1, 'x', depth, timeLimit, c_value, simulation_type, pt)
		    , makePlayer(player2, 'o', depth, timeLimit, c_value, simulation_type, pt)
		    , script
		    , True)
		signal.signal(signal.SIGABRT, gm.interrupt)
		signal.signal(signal.SIGINT,  gm.interrupt)
		signal.signal(signal.SIGQUIT, gm.interrupt)
		signal.signal(signal.SIGALRM, gm.interrupt)
		return gm

	def test1(self):
		"""
        Test if MCPlayer implement successfully
        """
		# X Always win
		# gm = self.makeGame(3, 'd', 'c', timeLimit=1.0, simulation_type='random', c_value=1.414)
		# gm.play()
		# self.assertEqual(gm.GetWinner(), 'X')
		#
		# # MC should do better
		# gm = self.makeGame(5, 'c', 'd', timeLimit=1.0, simulation_type='random', c_value=1.414)
		# gm.play()
		# self.assertEqual(gm.GetWinner(), 'X')

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

		cList = [1.414, 1.732, 2, 2.236, 2.449, 2.646, math.e, 2.828, 3]
		numGame = 10
		size = 8
		type = 'alphabeta'
		time = 5.0
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
				gm = self.makeGame(size, player1, player2, timeLimit=time, depth=depth, simulation_type=type, c_value=c, pt=True)
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
		write['time'] = time
		write['depth'] = depth
		write['simulation'] = type
		write['result'] = result

		with open('history.json', 'a') as f:
			# write to new line
			f.write('\n')
			json.dump(write, f)

		print("Done!")
		print(result)

	# Add more tests here

if __name__== "__main__":
	unittest.main()
