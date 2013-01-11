# -*- coding: utf-8 -*-
import ConfigParser
import sys

__config = None

WriteFile = lambda f, data : f.write(unicode(data))
Error = lambda data : sys.stderr.write(unicode(data) + '\n')

def getInstance():
	global __config
	if __config == None:
		__config = ConfigParser.RawConfigParser(allow_no_value = True)
		if os.path.exists('server.ini'):
			__config.read(['server.ini', ])
		else:
			Error(u'没有找到配置文件!')
			__config.set('FakeOnline', 'motd', 'NOT a Minecraft Server')
			__config.set('FakeOnline', 'kick', 'This is not a minecraft server. Do not login!')
			__config.set('FakeOnline', 'user', 42)
			__config.set('FakeOnline', 'max', 100)
			__config.set('FakeOnline', 'protocol', 51)
			Error(u'Minecraft协议版本号可以在http://wiki.vg/Protocol_History处找到')
			try:
				confFile = open('./server.ini', 'wb')
			except IOError:
				Error(u'不能写入server.ini, 默认配置将被输出到控制台.')
				WriteFile(sys.stdout, '------------ Begin server.ini ------------')
				__config.write(sys.stdout)
				WriteFile(sys.stdout, '------------- End server.ini -------------')
				Error(u'按回车退出程序...')
				try:
					raw_input()
				except EOFError:
					pass
				sys.exit(0)
			__config.write(confFile)
			confFile.close()
			Error(u'请在修改server.ini后重新运行本程序')
			Error(u'按回车退出程序...')
			try:
				raw_input()
			except EOFError:
				pass
			sys.exit(0)
	return __config

def save():
	try:
		confFile = open('./server.ini', 'wb')
	except IOError:
		Error(u'保存配置失败: 不能写入server.ini')
		return False
	global __config
	__config.write(confFile)
	confFile.close()
	return True
