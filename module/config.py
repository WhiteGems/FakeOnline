# -*- coding: utf-8 -*-
import os
import ConfigParser
import sys

__config = None

WriteFile = lambda f, data : f.write(str(data))
Error = lambda data : sys.stderr.write(str(data) + '\n')

def getInstance():
	global __config
	if __config == None:
		__config = ConfigParser.RawConfigParser(allow_no_value = True)
		if os.path.exists('./server.ini'):
			__config.read(['./server.ini', ])
		else:
			Error('No config file found. (first running?)')
			__config.add_section('FakeOnline')
			__config.set('FakeOnline', 'motd', 'NOT a Minecraft Server')
			__config.set('FakeOnline', 'kick', 'This is not a minecraft server. Do not login!')
			__config.set('FakeOnline', 'port', 25565)
			__config.set('FakeOnline', 'user', 42)
			__config.set('FakeOnline', 'max', 100)
			__config.set('FakeOnline', 'protocol', 51)
			Error(u'Protocol field is only valid if client use "new style" 0xFE0x01 ping request (in 1.4+).')
			Error(u'You can find protocol number at http://wiki.vg/Protocol_History')
			try:
				confFile = open('./server.ini', 'wb')
			except IOError:
				Error(u'Unable to open server.ini for writing, default config will be written on the screen.')
				WriteFile(sys.stdout, '------------ Begin server.ini ------------')
				__config.write(sys.stdout)
				WriteFile(sys.stdout, '------------- End server.ini -------------')
				Error(u'Press enter to exit.')
				try:
					raw_input()
				except EOFError:
					pass
				sys.exit(0)
			__config.write(confFile)
			confFile.close()
			Error(u'server.ini generated successfully. You can change the value, and run again!')
			Error(u'Press enter to exit...')
			try:
				raw_input()
			except EOFError:
				pass
			sys.exit(0)
	return __config

def reload():
	global __config
	return __config.read(['./server.ini']).count('./server.ini') != 0

def get(key):
	conf = getInstance()
	try:
		return conf.get('FakeOnline', key)
	except:
		pass

def set(key, value):
	conf = getInstance()
	try:
		return conf.set('FakeOnline', key, value)
	except:
		pass

def save():
	try:
		confFile = open('./server.ini', 'wb')
	except IOError:
		Error(u'Unable to save config: can\'t open server.ini for writing!')
		return False
	global __config
	__config.write(confFile)
	confFile.close()
	return True
