#!/usr/bin/env python

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from pathlib import Path

rpc_connection = 0

try:
    file = open(str(Path.home())+'/.bitcoin/.cookie')
    user, password = file.read().split(':')
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332" % (user, password))
    print('Using cookie auth, user:{} - password:{}'.format(user, password))
    print('blockheight: {}'.format(rpc_connection.getblockcount()))
except FileNotFoundError:
    print("Couldn't not find cookie file, is bitcoind running?")


mempool = rpc_connection.getrawmempool(True)
print('mempool size:{}'.format(len(mempool)))

for tx in mempool:
    print(mempool[tx])

    for i in mempool[tx]['fees']:
        print(i)
        # print('tx: {}, param:{}:{}'.format(tx, i, mempool[tx][i]))
    break
print('Out of loops')