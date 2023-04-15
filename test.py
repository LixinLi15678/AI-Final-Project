import game_manager, game_rules, signal, unittest
from player import makePlayer


class GameTest(unittest.TestCase):


	def makeGame(self, size, player1, player2, depth, script=None):
		gm = game_manager.GameManager(
		      size
		    , size
		    , makePlayer(player1, 'x', depth)
		    , makePlayer(player2, 'o', depth)
		    , script
		    , True)
		signal.signal(signal.SIGABRT, gm.interrupt)
		signal.signal(signal.SIGINT,  gm.interrupt)
		signal.signal(signal.SIGQUIT, gm.interrupt)
		signal.signal(signal.SIGALRM, gm.interrupt)
		return gm

	# Add more tests here

if __name__== "__main__":
	unittest.main()
