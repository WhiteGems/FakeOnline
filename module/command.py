import sys

Error = lambda s : sys.stderr.write(str(s) + '\n')

class Command:
	def __init__(self):
		self.command = {}
		self.registerCommand('help', self.printHelp, 'Print Help Message')

	def registerCommand(self, command, func, Help):
		if self.command.has_key(command):
			return False
		if not callable(func):
			return False
		self.command[command] = (func, Help)

	def runCommand(self, command):
		try:
			command, args = command.strip().split(None, 1)
			args = args.split()
		except ValueError:
			command = command.strip()
			args = ()
		if not self.command.has_key(command):
			self.commandNotFound(command, *args)
			return False
		else:
			self.command[command][0](*args)

	def commandNotFound(self, command, *args):
		Error('Command %s not found!' % command)
		self.printHelp()

	def printHelp(self):
		Error('Registered command:')
		for k in self.command:
			Error('%s\t\t%s' % (k, self.command[k][1]))
		
