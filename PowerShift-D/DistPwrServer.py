import select
import socket
import sys,os
import Queue
import math
total_extra_power=0
urgent_count=0
take_power_unit=2
break_signal = 0


def take_power_func(TOTAL_extra_power):
    power = 0
    if TOTAL_extra_power > 10:
        power = math.floor(TOTAL_extra_power/10)
    else:
        power = 1     
    return power
# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('ubuntu-3.cs.uchicago.edu', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
server.bind(server_address)

# Listen for incoming connections
server.listen(50)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets to which we expect to write
outputs = [ ]
# Outgoing message queues (socket:Queue)
message_queues = {}

while inputs and break_signal != 1:
    if os.path.isfile('/home/huazhe/signal/END_runtime'):
        break_signal = 1

    # Wait for at least one of the sockets to be ready for processing
    print >>sys.stderr, '\nwaiting for the next event'
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # Handle inputs
    for s in readable:

        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print >>sys.stderr, 'new connection from', client_address
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data we want to send
            message_queues[connection] = Queue.Queue()
        else:
            data = s.recv(1024)
            if data:
                # A readable client socket has data
                receive_list = data.split(',')
                add_power =float(receive_list[0])
                urgent_flag = int(receive_list[1])
                urgent_change = int(receive_list[2])
                necessary_power =float(receive_list[3])
                take_power_unit = take_power_func(total_extra_power)
                actual_get_power = 0
                release_power = 0
                if add_power != 0:
                    total_extra_power +=add_power
                #elif urgent_flag == 0 and urgent_change== 0 and necessary_power == 0:
                #    total_extra_power = total_extra_power
                else:
                    if urgent_flag ==1:
                        #urgent case
                        actual_get_power = min(total_extra_power, necessary_power)
                        if total_extra_power >= necessary_power:
                            urgent_change -= 1
                            
                        total_extra_power = total_extra_power - actual_get_power
                    elif urgent_flag == 2:
                        actual_get_power = 0
                    else:
                        if urgent_count ==0:
                            actual_get_power = min(take_power_unit, total_extra_power)
                            total_extra_power -= actual_get_power
                urgent_count += urgent_change
                if urgent_count !=0:
                    release_power = 1
                print 'received_data=',data
                print 'urgent_count=',urgent_count,'total_extra_power=',total_extra_power
                output_data= str(actual_get_power) +','+str(release_power)
                #print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
                message_queues[s].put(output_data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
            else:
                # Interpret empty result as closed connection
                print >>sys.stderr, 'closing', client_address, 'after reading no data'
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                # Remove message queue
                del message_queues[s]
    # Handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except Queue.Empty:
            # No messages waiting so stop checking for writability.
            print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
            outputs.remove(s)
        else:
            print >>sys.stderr, 'sending "%s" to %s' % (next_msg, s.getpeername())
            s.send(next_msg)
    # Handle "exceptional conditions"
    for s in exceptional:
        print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]

server.close()
