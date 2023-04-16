import game_manager, game_rules, signal, unittest
from player import makePlayer

class GameTest(unittest.TestCase):


	def makeGame(self, size, player1, player2, depth=3, timeLimit=2.0, simulation_type='random', c_value=1.414, script=None):
		gm = game_manager.GameManager(
		      size
		    , size
		    , makePlayer(player1, 'x', depth, timeLimit, c_value, simulation_type)
		    , makePlayer(player2, 'o', depth, timeLimit, c_value, simulation_type)
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
		gm = self.makeGame(3, 'd', 'c', timeLimit=1.0, simulation_type='random', c_value=1.414)
		gm.play()
		self.assertEqual(gm.GetWinner(), 'X')

		# MC should do better
		gm = self.makeGame(5, 'c', 'd', timeLimit=1.0, simulation_type='random', c_value=1.414)
		gm.play()
		self.assertEqual(gm.GetWinner(), 'X')

	def test2(self):
		"""
		Test different c_value
		"""

		result = {}
		cList = [1.414, 1.732, 2, 2.236, 2.449, 2.646, 2.828, 3]
		numGame = 20

		for c in cList:
			# Count the number of X win
			print(f"Testing c_value = {c} ...")
			numX = 0
			for numG in range(numGame):
				print(f"Game {numG + 1} ...")
				gm = self.makeGame(8, 'c', 'r', timeLimit=2, simulation_type='random', c_value=c)
				gm.play(PB=False)
				if gm.GetWinner() == 'X':
					numX += 1
				print(f"X win {numX} times")
			result[c] = numX

		print(result)


	# Add more tests here

if __name__== "__main__":
	unittest.main()
