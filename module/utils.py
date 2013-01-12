import socket
import threading

try:
    pairfamily = socket.AF_UNIX
except:
    pairfamily = socket.AF_INET

def SocketPair(family = pairfamily, type_=socket.SOCK_STREAM, proto=socket.IPPROTO_IP):
    try:
        sock1, sock2 = socket.socketpair(family, type_, proto)
        return (sock1, sock2)
    except:
        listensock = socket.socket(family, type_, proto)
        listensock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listensock.bind( ('127.0.0.1', 0) )
        iface, ephport = listensock.getsockname()
        listensock.listen(1)

        sock1 = socket.socket(family, type_, proto)
        connthread = threading.Thread(target=pairConnect, args=[sock1, ephport])
        connthread.setDaemon(1)
        connthread.start()
        sock2, sock2addr = listensock.accept()
        listensock.close()
        return (sock1, sock2)

def pairConnect(sock, port):
    sock.connect( ('127.0.0.1', port) )

def getVersionByProtocol(protocol):
	mapping = {
			8	: '1.2 Beta',
			9	: '1.3 Beta',
			10	: '1.4 Beta',
			11	: '1.5 Beta',
			13	: '1.6 Beta',
			14	: '1.7 Beta',
			15	: '1.8 Beta Pre-release',
			16	: '1.8 Beta Pre2-release',
			17	: '1.8 Beta',
			18	: '1.9 Beta Pre1',
			19	: '1.9 Beta Pre2',
			20	: '1.9 Beta Pre4',
			21	: '1.9 Beta Pre5',
			22	: '1.0',
			23	: '1.1',
			28	: '1.2.2',
			29	: '1.2.4',
			39	: '1.3.1',
			47	: '1.4.1',
			49	: '1.4.4',
			51	: '1.4.6',
	}
	try:
		return mapping[protocol]
	except KeyError:
		return '1.4.6' # Return the Newest.

