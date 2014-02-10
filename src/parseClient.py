import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 5000))
data1 = client_socket.recv(4096)
if data1 == "Connection established\n":
    client_socket.send("Load Parser" + '\n')
    data2 = client_socket.recv(4096)
    if data2 == "Parser Loaded...Ready to accept sentences...\n":
        for sent in ['The sun goes over the moon every hour.',
                     'It is not acceptable to be hiding from bats.',
                     'Samantha killed the dog in the park. Everyone saw her.']:
            client_socket.send(sent + '\n')
            parse = client_socket.recv(4096)
            print parse
    else:
        print "Something Wrong!"
        print data2
        client_socket.send('q\n')
else:
    print "Something Wrong!"
    print data1
    client_socket.send('q\n')
#while 1:
#    data = client_socket.recv(4096)
#    if (data == 'q\n' or data == 'Q\n'):
#        client_socket.close()
#        break
#    else:
#        print "RECIEVED:", data
#        data = raw_input("SEND( TYPE q or Q to Quit):")
#        if (data != 'Q' and data != 'q'):
#            client_socket.send(data + '\n')
#        else:
#            client_socket.send(data)
#            client_socket.close()
#            break
