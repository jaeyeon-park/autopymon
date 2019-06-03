import sys,os
from autopymon import Autopymon
import traceback as tb
class pymonRunner():
	def __init__(self):
		self.programName = Autopymon.__name__
		self.ver = Autopymon.__ver__
		self.quitcmd = 'Ctrl+C'

	def loadView(self):
		os.system('clear')
		print('{} version {}'.format(self.programName,self.ver))
		print("{} : quit {}".format(self.quitcmd,self.programName))
		print("-"*os.get_terminal_size().columns)
		
	def mainViewloop(self):
		isfile = os.path.isfile
		isdir = os.path.isdir
		islink = os.path.islink
		exists = os.path.exists
		isSeries = [(isfile,'file'),(isdir,'dir'),(islink,'link')]
		while True:
			try:
				print("\ncurdir : {}".format(os.path.abspath('./')))
				f = input("support both abspath and relative-path to curdir\nfilepath : ")
				f = os.path.expanduser(f)
				if isfile(f):
					pymon = Autopymon(f)
					runcode = pymon.run()
					if runcode == 0:
						print("BYE!")
						return 0
					else:
						print("ERROR!")
						return -1
				else:
					for isfunc,f_kind in isSeries:
						if isfunc(f):print("{} is {}".format(f,f_kind))
					if not exists(f):print("{} does not exist".format(f))
					dirname = os.path.dirname(f)
					if not isdir(f):continue
					for node in os.listdir(dirname):
						node_kind = [node_kind for isfunc,node_kind in isSeries if isfunc(node)]
						if len(node_kind) : node_kind = node_kind[0]
						else:node_kind = ""
						print("L {}\t {}".format(node_kind, node))	
			except KeyboardInterrupt:
				print("\rQuit Autopymon")
				return 0
			except:
				tb.print_exc()
				return -1


if __name__ == "__main__":
	pymon = pymonRunner()
	pymon.loadView()
	pymon.mainViewloop()
	
