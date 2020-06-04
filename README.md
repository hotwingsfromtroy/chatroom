# chatroom
A chatroom implemented in python using sockets. Might need some kinks to be ironed out. Stress testing incomplete.

To use it:
- run the server file first. It prints out the server address on the terminal.
- run a client window from one terminal, using the server address. Type the username and hit enter to enter the chatroom.
- run another client by following the above step.
- as long as clients are on the same network, i.e, the routes b/w the various machines are well-defined, then they should be able to enter the chatroom. Theoretically, at least. I wouldn't exactly guarantee it though since stress testing hasn't been performed properly.
