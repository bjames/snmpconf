from pysnmp.hlapi import *
import tftpy
import ipaddress
import Queue
import socket
import threading
import os

# TODO implement SNMPv3
# TODO implement configuration functions
# TODO check for root at program start (root required to bind TFTP server to TCP 69)
# TODO we are doing to much in main() most of this should be moved to other functions


def tftp_server(computer_address, queue):

    print "Creating TFTP server and binding to " + str(computer_address) + ":69"

    # Have the TFTP send the dynamic file for any download requests
    server = tftpy.TftpServer('')
    queue.put(server)
    server.listen(computer_address, 69)


    return


def send_legacy_snmp(target_address, computer_address, community):

    # HostConfigSet OID + IP Address
    oid = '1.3.6.1.4.1.9.2.1.53.' + str(computer_address)

    # Sends an SNMP set request
    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(SnmpEngine(),

            CommunityData(community),
            UdpTransportTarget((str(target_address), 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid),
                       OctetString('config_file.conf')))
    )

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            print(' = '.join([x.prettyPrint() for x in varBind]))

    return


def send_v3_snmp(target_address, computer_address, username, password):

    pass


def get_ip_address():

    # gets the IP address that is active on the network by opening a socket
    # solution not mine see: http://stackoverflow.com/a/30990617
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))

    return ipaddress.ip_address(unicode(s.getsockname()[0]))


def configure(config_file):

    user_input = ""

    print "Input configuration, one line at a time. Type 'end' to end"
    while user_input != "end":

        user_input = raw_input()
        config_file.write(user_input + "\n")

    return


def test_main():

    """
    try:
        computer_address = get_ip_address()
    except socket.error:
        print "Failed to get current IP address are you connected to the network?"
        exit()
    """

    computer_address=ipaddress.ip_address(unicode("192.168.192.1"))
    target_address = ipaddress.ip_address(unicode("192.168.192.10"))
    snmp_string = "private"
    snmp_ver = 2

    print "=================================="
    print "Test Parameters"
    print "=================================="
    print "target ip address = " + str(target_address)
    print "source ip address = " + str(computer_address)
    print "SNMP RW String = " + snmp_string
    print "SNMP version = " + str(snmp_ver)
    print "==================================\n"
    print "starting the tftp server in a separate thread"

    config_file = open('config_file.conf', 'w+b')

    configure(config_file)

    # This queue will be used to get our server object back from the initialization function
    queue = Queue.Queue()

    config_file.close()

    # create a new thread containing our TFTP server. Pass it our file object
    tftp_thread = threading.Thread(target=tftp_server, args=[str(computer_address), queue])
    tftp_thread.start()

    server = queue.get()

    send_legacy_snmp(target_address, computer_address, snmp_string)

    user_input = ""

    while user_input != "done":
        user_input = raw_input("enter done when finished")

    server.stop()
    os.remove('config_file.conf')
    exit()


test_main()
