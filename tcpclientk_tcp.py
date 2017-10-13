import logging
import socket
import threading
import time

DEFAULT_CONNECT_TIMEOUT = 10.0  # seconds
DEFAULT_RECV_TIMEOUT = 1.0
DEFAULT_RECV_BUFLEN = 1024

logger = logging.getLogger(__name__)

class TcpClientSock(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.connected = False
        self.disconnected = False
        self.sock = None
        self.last_error = None

    def connect(self):
        logger.debug("connect")
        if self.disconnected:
            return
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(DEFAULT_CONNECT_TIMEOUT)
            self.sock.connect((self.ip, self.port))
        except Exception as e:
            if self.sock:
                self.sock.close()
                self.sock = None
            self.connected = False
            self.last_error = str(e)
            logger.debug(e)
        else:
            self.connected = True
            self.last_error = None

    def disconnect(self):
        logger.debug("disconnect")
        if self.sock:
            self.sock.close()
        self.sock = None
        self.connected = False
        self.disconnected = True


class TcpClientThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name,
                         daemon=daemon)
        self.args = args
        self.kwargs = kwargs
        self._do_exit = False
        self.tcp_client = None
        self._queue = None
        self.autoconnect = False

        self.ip = self.kwargs['ip']
        self.port = self.kwargs['port']
        if 'tcp_client' not in self.kwargs:
            self.tcp_client = TcpClientSock(self.ip, self.port)
        else:
            self.tcp_client = self.kwargs['tcp_client']

        if 'msg_queue' in self.kwargs:
            self._queue = self.kwargs['msg_queue']

    def run(self):
        logger.debug('%s: running with %s and %s', self.__class__.__name__, self.args, self.kwargs)

        while not self._do_exit:

            while (not self._do_exit) and (not self.tcp_client.connected) and self.autoconnect:
                self.tcp_client.connect()
                time.sleep(0.5)

            if not self._run():
                time.sleep(0.5)

        logger.debug('%s: NOT running' % self.__class__.__name__)

    def _run(self):
        raise NotImplementedError


class TcpClientTxThread(TcpClientThread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoconnect = True

    def _run(self):
        time.sleep(1)
        return True

    def send(self, data):
        if (not isinstance(data, str)) and (not isinstance(data, bytes)):
            raise Exception("You must pass a str or bytes to send() not a %s" % type(data))

        if isinstance(data, str):
            data_ascii_encoded = data.encode('ascii')
        elif isinstance(data, bytes):
            data_ascii_encoded = data

        if not self.tcp_client.connected:
            logger.debug('Could not send data: %s' % data_ascii_encoded)
            return False
        logger.debug('Sending data: %s' % data_ascii_encoded)

        try:
            self.tcp_client.sock.send(data_ascii_encoded)
        except BrokenPipeError as e:
            self.tcp_client.connected = False
            return False
        return True


class TcpClientRxThread(TcpClientThread):

    def _run(self):
        if not self.tcp_client.connected:
            logger.debug('Could not rcv data (not connected)')
            return False

        logger.debug('In rcv blocking call...')

        try:
            self.tcp_client.sock.settimeout(DEFAULT_RECV_TIMEOUT)
            data = self.tcp_client.sock.recv(DEFAULT_RECV_BUFLEN)
        except BrokenPipeError as e:
            self.tcp_client.connected = False
            return False
        except socket.timeout as e:
            # Ignore timeouts, no error
            return True
        except OSError as e:
            self.tcp_client.connected = False
            return False

        if (data is not None) and (len(data) == 0):
            logger.debug("%s: Received = 0 bytes" % (self.__class__.__name__))
            self.tcp_client.connected = False
            return False

        if (data is None):
            return True

        logger.debug("%s: Received: %s" % (self.__class__.__name__, data))

        if self._queue is not None:
            self._queue.put(data)

        return True

