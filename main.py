# -*- coding: utf-8 -*-
from module import config, utils, command
import socket
import select
import threading
import time
import sys
import struct

reload(sys)
#sys.setdefaultencoding('')

WriteFile = lambda f, data : f.write(str(data))
Error = lambda data : sys.stderr.write(str(data) + '\n')

def T(S):
	sys.setdefaultencoding('utf-8')
	ret = S.encode('utf-16be')
	sys.setdefaultencoding('ascii')
	return ret

def Data(*args):
	sys.setdefaultencoding('latin1')
	ret = ''.join(args).encode('latin1')
	sys.setdefaultencoding('ascii')
	return ret

_Hex = lambda S : ' '.join(map(str,map(hex, map(ord, S))))
KickPacket = u'\xFF'

def client(sock, addr):
	global Error
	global KickPacket
	global _Hex
	addr = '%s:%d' % addr
	sock.settimeout(3)
	Error('[%s] Connected!' % addr)
	try:
		packet = sock.recv(4096)
	except socket.timeout:
		sock.close()
		return 1
	if packet[0] == '\xFE': # Server List Ping
		Error('[%s] Type:Ping' % addr)
		if len(packet) > 1 and packet[1] == '\x01': # New Response
			Error('[%s] Version: 1.4 or higher' % addr)
			datafield = [
					u'\x00\xA7\x00\x31',
					T(config.get('protocol')),
					T(utils.getVersionByProtocol(config.get('protocol'))),
					T(config.get('motd')),
					T(config.get('user')),
					T(config.get('max'))
			]
			datastr = u'\x00\x00'.join(datafield)
			Length = struct.pack('!h', len(datastr) >> 1)
			data = Data(KickPacket, Length, datastr)
			try:
				sock.sendall(data)
				while sock.recv(4096) != '':
					pass
			except:
				sock.close()
				return 1
			sock.close()
			return 0
		else: # Old Style Response
			Error('[%s] Version: 1.3 or lower' % addr)
			datafield = [
					T(config.get('motd')),
					T(config.get('user')),
					T(config.get('max')),
			]
			datastr = u'\x00\xA7'.join(datafield)
			Length = struct.pack('!h', len(datastr) >> 1)
			data = Data(KickPacket, Length, datastr)
			try:
				sock.sendall(data)
				sock.recv(4096)
			except:
				sock.close()
				return 1
			sock.close()
			return 0
	elif packet[0] == '\x02':
		Error('[%s] Type: login' % addr)
		packet = packet[1:]
		k = T(config.get('kick'))
		l = struct.pack('!h', len(k) >> 1)
		data = Data(KickPacket, l, k)
		rl = struct.unpack('!h', packet[:2])[0] << 1
		if rl != len(packet) - 2: # 1.3 or higher.
			Error('[%s] Version: 1.3 or higher' % addr)
			try:
				sock.sendall(data)
				sock.recv(4096)
			except:
				sock.close()
				return 1
			sock.close()
			return 0
		else: # 1.2 or lower
			Error('[%s] Version: 1.2 or lower' % addr)
			sock.sendall('\x02\x00\x01\x00\x2d'.encode('latin1')) # online-mode = false
			try:
				t = sock.recv(4096)
				assert len(t) > 1 and (t[0] == '\x01' or t[0] == '\xFA') # 0xFA packet is used in forge client.
				sock.sendall(data)
				sock.recv(4096)
			except AssertionError:
				print _Hex(t[0])
				err = T('Protocol ERROR!')
				L = struct.pack('!h', len(err) >> 1)
				try:
					sock.sendall(KickPacket.encode('latin1') + L.encode('latin1') + err.encode('latin1'))
					sock.recv(4096)
				except:
					pass
				sock.close()
				return 1
			except:
				sock.close()
				return 1
			sock.close()
			return 0
	else:
		Error('[%s] Unknown Protocol! Hacking attempt?' % addr)
		err = T('Protocol ERROR!')
		L = struct.pack('!h', len(err) >> 1)
		try:
			sock.sendall((KickPacket + L + err).encode('latin1'))
			sock.recv(4096)
		except:
			pass
		sock.close()
		return 1


def server(sock, pendingSock):
	global Error
	threads = []
	sid, pid = sock.fileno(), pendingSock.fileno()
	while True:
		rl, wl, xl = select.select([sid, pid], [], [])
		if rl.count(pid) :
			sock.close()
			Error('Deny further connection... Waiting for the connected clients...')
			for t in threads:
				t.join()
			Error('All clients disconnected.')
			sys.exit(0)
		for i in range(len(threads)):
			if not threads[i].isAlive:
				del threads[i]
		newThread = threading.Thread(target = client, args = sock.accept())
		newThread.start()
		threads.append(newThread)

def Exit():
	global sender
	global listenThread
	global Error
	sender.sendall('EXIT!')
	listenThread.join()
	Error('All OK, will now exit.')
	sys.exit(0)

def main():
	port = int(config.get('port'))
	try:
		bindSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		bindSocket.bind(('', port))
		bindSocket.listen(8)
	except:
		Error('Can\'t bind on port %d, will exit in 3 seconds.(The port is used by others?)' % port)
		time.sleep(3)
	Error('Bind at port %d' % port)
	global sender
	sender, receiver = utils.SocketPair()
	global listenThread
	listenThread = threading.Thread(target = server, args = (bindSocket, receiver))
	listenThread.start()
	Error('FakeOnline ready!')
	Command = command.Command()
	Command.registerCommand('reload', config.reload, 'Reload server.ini.')
	Command.registerCommand('stop', Exit, 'Peacefully exit the program.')
	Command.printHelp()
	while True:
		try:
			Command.runCommand(raw_input())
		except EOFError:
			Error('EOF Received, shutting down...')
			Exit()

if __name__ == '__main__':
	main()
