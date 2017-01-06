import re
import subprocess
import time
import socket

from semantic_version import Spec, Version

class VaultServerManager(object):
    def __init__(self, config_path, client):
        self.config_path = config_path
        self.client = client

        self.keys = None
        self.root_token = None

        self._process = None

    def start(self):
        command = ['vault', 'server', '-config=' + self.config_path]

        self._process = subprocess.Popen(command,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

        attempts_left = 20
        last_exception = None
        while attempts_left > 0:
            try:
                self.client.is_initialized()
                return
            except Exception as ex:
                print('Waiting for Vault to start')

                time.sleep(0.5)

                attempts_left -= 1
                last_exception = ex

        raise Exception('Unable to start Vault in background: {0}'.format(last_exception))

    def stop(self):
        self._process.kill()

    def initialize(self):
        assert not self.client.is_initialized()

        result = self.client.initialize()

        self.root_token = result['root_token']
        self.keys = result['keys']

    def unseal(self):
        self.client.unseal_multi(self.keys)


class MotoServerManager(object):
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 5009  # picked at random

    def start(self):
        command = ['moto_server', 'ec2', '-H', self.host, '-p' + str(self.port)]
        self._process = subprocess.Popen(command,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)

        attempts_left = 20
        while attempts_left > 0:
            sock = socket.socket()
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            if result == 0:
                break
            else:
                print('Waiting for moto_server to start')
                time.sleep(0.5)
                attempts_left -= 1

    def stop(self):
        self._process.kill()

    @property
    def url(self):
        return 'http://{}:{}'.format(self.host, self.port)


VERSION_REGEX = re.compile('Vault v([\d\.]+)')

def match_version(spec):
    output = subprocess.check_output(['vault', 'version']).decode('ascii')
    version = Version(VERSION_REGEX.match(output).group(1))

    return Spec(spec).match(version)
