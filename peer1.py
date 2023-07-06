#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 22:09:14 2021

@author: gebingbing
"""


import socket
import select
import json


CLIENT_PORT = 7771
SERVER_ADDR = '127.0.0.1'
SERVER_PORT = 6666


with open('FILE_LIST_peer1.json','r') as f:
    FILE_LIST= json.load(f)

with open('REGISTER_LIST_peer1.json','r') as f:
    REGISTER_LIST= json.load(f)

#update the chunck list to server
def update():
     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((SERVER_ADDR,SERVER_PORT))
                sock.sendall(b'PEER1')
                sock.recv(1024)
                sock.send(b'update') 
                sock.recv(1024)
                sock.send(json.dumps(REGISTER_LIST).encode())
                data = sock.recv(1024)
                print(int(data))
                sock.close()
            except:
                print('update fail')
  
# ask server for the file's location              
def request(file):
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((SERVER_ADDR,SERVER_PORT))
                sock.sendall(b'PEER1')
                sock.recv(1024)
                sock.send(b'request') 
                sock.recv(1024)
                sock.send(file.encode())
                port_list = sock.recv(1024)
                port_list_dict = json.loads(str(port_list,'utf-8')) 
                print(port_list_dict)
                sock.close()
                return port_list_dict
            except:
                print('can not find the file location')
   
# ask the server for the file list             
def list_request():
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((SERVER_ADDR,SERVER_PORT))
                sock.sendall(b'PEER1')
                sock.recv(1024)
                sock.send(b'listrequest') 
                file_list = sock.recv(1024)
                file_list_dict = json.loads(str(file_list,'utf-8')) 
                print('file list in server are', file_list_dict)
                sock.close()
            except:
                print('can not find the file list')
        
# send the file to other peer            
def send(conn,addr):
        with conn:
            print('connected by:',addr)
            while True:
                file = conn.recv(1024)
                #find the file
                if not file:
                    break
                file_str =  str(file,'utf-8')
                file_data = {file_str:FILE_LIST[file_str]}
                print(file_data, type(file_data))
                try:
                    conn.sendall(json.dumps(file_data).encode())
                except:
                    print('file send fail')

#download the file from other peer
def download(chunkdict):
        for peer in chunkdict.keys():
            # ignore the chunk the peer already have
            if peer == 'PEER1':
                continue
            else:
                ip = chunkdict[peer]['IP']
                port = chunkdict[peer]['PORT']
                file = chunkdict[peer]['file']
                if len(file) == 0:
                    continue
                else:
                    print(port)
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        try:
                            sock.connect((ip,port))
                            print('1')
                            for chunk in file:
                                print(chunk)
                                sock.send(chunk.encode())
                                new_file = sock.recv(1024)
                                file_dict = json.loads(str(new_file,'utf-8')) 
                                    # #change REGISTER_LIST and FILE_LIST
                                for file_name in file_dict.keys():
                                    file_dict[file_name]['port'] = 7771
                                    REGISTER_LIST['file'][file_name] = file_dict[file_name]['len']
                                    FILE_LIST.update(file_dict)
                                    REGISTER_LIST['FILE_NUM'] = len(FILE_LIST)
                            sock.close()
                        except:
                            print('the fail download fail')
        print(REGISTER_LIST,FILE_LIST)
        with open('FILE_LIST_peer1.json','w') as f:
            json.dump(FILE_LIST,f)
        with open('REGISTER_LIST_peer1.json','w') as f:
            json.dump(REGISTER_LIST,f)
        print ('the fail download successfully')

                
def login(SERVER_ADDR, SERVER_PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((SERVER_ADDR,SERVER_PORT))
            sock.sendall(b'PEER1')
            sock.recv(1024) #make sure the server receive the peer name
            sock.sendall(json.dumps(REGISTER_LIST).encode())
            data = sock.recv(1024)
            print(int(data))
            sock.close()
        except:
                print('the login fail')
            
         
if __name__ == '__main__':
        #want to get file1's chunk
        file = 'file1'
        chunkdict = request(file)
        print(chunkdict)
        download(chunkdict)
        update()
        inputs = []
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_socket:
            peer_socket.setblocking(False)
            peer_socket.bind(('127.0.0.1', 7771))
            peer_socket.listen(5)
            # Sockets from which we expect to read
            inputs.append(peer_socket) 
            while inputs:
                readable, writable, exceptional = select.select(inputs, [],[])   
                for s in readable:
                    if s == peer_socket:
                        send_conn, send_addr = s.accept()
                        with send_conn:
                            print('connected by', send_addr)
                            send(send_conn, send_addr)
#                inputs.remove(s)
#            peer_socket.close()
