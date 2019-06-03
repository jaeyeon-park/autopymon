import time,fcntl,os,signal
import traceback as tb
import collections
__VERSION = 0.1
__PRINT_BUF_LEN = 20
def standprintQ(maxlen):
	stdout = collections.deque(maxlen=maxlen)
	def connectQ():return stdout.appendleft
	def printQ():
		if len(stdout):print(stdout.pop())
	def printQall():
		while len(stdout):print(stdout.pop())
	return (printQall, printQ, connectQ)

printQall, printQ, connectQ = standprintQ(__PRINT_BUF_LEN)

class DNotify():
	def __init__(self,dirpath):
		dirpath = os.path.expanduser(dirpath)
		dirpath = os.path.abspath(dirpath)
		if not os.path.isdir(dirpath):
			print('SHOULD BE DIR PATH')
			raise Excepton
		self.dirpath = dirpath
		self.dirfd = os.open(self.dirpath,os.O_RDONLY)
		self.setSIGIO = False
	
	def addWatch(self,event,handler):
		eventmask = 0x0
		if isinstance(event,int):event = [event]
		for e in event: eventmask |= e
		def wrap(handler):
			def wrapped(signum,frame):
				handler(signum,frame)
				fcntl.fcntl(self.dirfd,fcntl.F_NOTIFY,eventmask)
			return wrapped
		if not self.setSIGIO:
			signal.signal(signal.SIGIO,wrap(handler))
			self.setSIGIOSET = True
		else:
			print("ALREADY HANDLER IS SET")
			return
		fcntl.fcntl(self.dirfd,fcntl.F_SETSIG,0)
		fcntl.fcntl(self.dirfd,fcntl.F_NOTIFY,eventmask)
		
	def rmWatch(self):
		fcntl.fcntl(self.dirfd,fcntl.F_NOTIFY,0)
		
class Autopymon():
	__ver__ = 0.1

	class Log():
		def __init__(self,msgtype='',lines=[],indent=0):
			if isinstance(lines,str): self.data = [lines]
			else: self.data = lines
			if msgtype != '' : msgtype = '({})'.format(msgtype)
			self.msgtype = msgtype
			self.indent = indent
		def append(self,data):self.data.append(data)
		def extend(self,data):self.data.extend(data)
		def __str__(self):
			msg = 'Autopymon {}:\n'.format(self.msgtype)
			for data in self.data : msg += (" "*self.indent + "{}\n".format(data))
			return msg
		
	def __new__(cls,filepath):
		obj = super(Autopymon,cls).__new__(cls)
		obj.pushprint = connectQ()
		obj.__ver = cls.__ver__
		obj.__name = cls.__name__
		return obj
	def __init__(self,filepath):
		filepath = os.path.expanduser(filepath)
		if not os.path.isfile(filepath):
			print("NOT FILE")
			raise Exception
		self.fpath = os.path.abspath(filepath)
		self.dirpath = os.path.dirname(self.fpath)
		self.dnotify = DNotify(self.dirpath)
		self.modified = os.path.getmtime(self.fpath)
		
	@property
	def name(self):return self.__name
	@property
	def ver(self):return self.__ver
	def __runCodeInSandbox(self):
		os.system('clear')
		f = open(self.fpath)
		code = f.read()
		f.close()
		try:
			log = Autopymon.Log(msgtype='Start')
			log.append('time : {}'.format(time.ctime()))
			log.append('file : {}'.format(self.fpath))
			self.pushprint(log)
		
			log = Autopymon.Log(msgtype='Inside-Sandbox',indent=1)
			sandbox = {'print':lambda msg:log.append(msg)}
			exec(code,sandbox,{}) #여기가 좀 다른 분
			self.pushprint(log)
		except:
			log = Autopymon.Log(msgtype='Code-Exception',indent=1)
			exclog = tb.format_exc().splitlines()[3:]
			exclog[0] = exclog[0].replace('<string>',self.fpath.split('/')[-1])
			log.extend(exclog)
			self.pushprint(log)
		finally:
			log = Autopymon.Log(msgtype='Check-done')
			log.append('time : {}'.format(time.ctime()))
			log.append('Ctrl+C : quit {}'.format(self.name))
			self.pushprint(log)
			self.pushprint("-"*os.get_terminal_size().columns)
	
	def __ioEventHandler(self,signum,frame):
		if not os.path.isfile(self.fpath): return
		newmodified = os.path.getmtime(self.fpath)
		if not (newmodified-self.modified) : return
		self.__runCodeInSandbox()
		self.modified = newmodified
	
	def register(self):
		self.dnotify.addWatch(fcntl.DN_MODIFY,self.__ioEventHandler)
		
	def run(self):
		self.register()
		self.__runCodeInSandbox()
		while True:
			try:
				printQall()
			except KeyboardInterrupt:
				self.pushprint("\rQuit Autopymon")
				printQall()
				return 0
			except:
				tb.print_exc()
				return -1
		


	
	
	
	
	
	