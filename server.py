#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 21:34:05 2021

@author: gebingbing
"""

import socket
import json
import select

SERVER_IP = '127.0.0.1'
SERVER_PORT = 6666

with open('CHUNK_LIST.json','r') as f:
       CHUNK_LIST = json.load(f)

# socket list
inputs = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setblocking(False)
            server_socket.bind((SERVER_IP, SERVER_PORT))
            server_socket.listen(5)
            inputs.append(server_socket) 
            while inputs:
                #use the select to monitor server's socket
                readable, writable, exceptional = select.select(inputs, [], []) 
                for s in readable:
                    if s == server_socket:
                        connection, client_address = s.accept()
                        with connection:
                            # get peer' name
                            print ('connection from', client_address)
                            peer_name = connection.recv(1024)
                            peer_name_str = str(peer_name,'utf-8')
                            connection.send(b'1') 
                            print (peer_name_str)
                            # peer have already in the network
                            if peer_name_str in CHUNK_LIST.keys():
                                reqest_kind = connection.recv(1024)
                                print(str(reqest_kind,'utf-8'))
                                # peer request is update
                                if str(reqest_kind,'utf-8') == 'update':
                                    connection.send(b'1') 
                                    new_peer_chunk = connection.recv(1024)
                                    new_chunk = {peer_name_str:json.loads(str(new_peer_chunk,'utf-8'))}
                                    CHUNK_LIST.update(new_chunk)
                                    with open('CHUNK_LIST.json','w') as f:
                                        json.dump(CHUNK_LIST,f)
                                    connection.send(b'1')
                                    print('%s update successfully' %(peer_name_str))
                                # peer request is listrequest
                                if str(reqest_kind,'utf-8') == 'listrequest':
                                     connection.sendall(json.dumps(CHUNK_LIST).encode())
                                     print('send file list to %s' %(peer_name_str))
                                # peer request is request
                                if str(reqest_kind,'utf-8') == 'request':
                                    connection.send(b'1') 
                                    port_dict = {}
                                    file_need = connection.recv(1024)
                                    file_need_str = str(file_need,'utf-8')
                                    for peer in CHUNK_LIST.keys():
                                        chunk_list = []
                                        for chunk in CHUNK_LIST[peer]['file'].keys():
                                            if file_need_str in chunk:
                                                chunk_list.append(chunk)
                                        port_dict[peer] = {"file":chunk_list,"IP":CHUNK_LIST[peer]["IP"],"PORT":CHUNK_LIST[peer]["PORT"]}
                                        print(port_dict)
                                    connection.sendall(json.dumps(port_dict).encode())
                                    print('send file port to %s' %(peer_name_str))
                            # peer is not int the network and want to register
                            else:
                                #new peer share its file list to server
                                new_peer_register = connection.recv(1024)
                                new_chunk = {peer_name_str:json.loads(str(new_peer_register,'utf-8'))}
                                CHUNK_LIST.update(new_chunk)
                                connection.sendall(b'1')
                                with open('CHUNK_LIST.json','w') as f:
                                    json.dump(CHUNK_LIST,f)
                                print('%s register successfully' %(peer_name_str))
#                inputs.remove(s)
#            server_socket.close()