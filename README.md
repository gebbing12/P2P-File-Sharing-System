# P2P File Sharing System
Implemented a hybrid P2P file-sharing system with a central server using the Python socket library.

## introduction
In this program, I design a simple peer-to-peer file sharing system. And in this network we have one central server, three peers, and three files.
At the begin, peer1 and peer2 are already register in the network and the central server has their file list of them. About peer3, it will try to register in the network and share its file list in the future. Figure1 is network’s structure.

## Protocol
To make the system more practicable, here are some protocol about the message and file transmission:
1. Every time a new peer wants to connect with the p2p file system, it should send its peer name first, so the server can check whether the peer have already in the network. And the server will use different processing in different situation.
2. Each peer can directly request the file list from the server, or ask the server for the IP endpoints of the peers containing the requested file.
3. When a peer update it's chunk of file, it must tell central server to update file list.
