import os
import shlex
import time
import json
from subprocess import check_output

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.util import dumpNodeConnections

from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, RemoteController
    

def mapNetworkScenarios(net: Mininet, host_pairs: list = [["h1","h3"],["h2","h4"],["h1","h4"],["h2","h3"]]):


    # Execute iperf on each pair
    network_map = {"network": [], "scenario": "default"}

    for pair in host_pairs:

        hosts = []

        for host in net.hosts:
            if host.name in pair:
                hosts.append(host)
        
        if len(hosts) != 2:
            continue

        h1, h2 = hosts

        # Check if hosts are connected
        result = net.ping([h1,h2],timeout="0.5")

        if result < 100:
            host1_speed, host2_speed = net.iperf(hosts=[h1, h2], seconds=5) # Host connected, testing bandwidth

        else:
            host1_speed = "-"
            host2_speed = "-"
        
        # Add results to the network map
        network_map["network"].append({
            "host1": {
                "name": h1.name,
                "speed": host1_speed
            },

            "host2": {
                "name": h2.name,
                "speed": host2_speed
            }
        })
    
    return network_map

class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        # two templates for links creation
        host_config = {}
        switch_config_video = {} #dict(bw=10)
        switch_config_non_video = {}# dict(bw=8)



        switches = {}
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)
        
        self.addHost("h1",ip="10.0.0.1/24",mac="00:00:00:00:00:01")
        self.addHost("h2",ip="10.0.0.2/24",mac="00:00:00:00:00:02")
        self.addHost("h3",ip="10.0.0.3/24",mac="00:00:00:00:00:03")
        self.addHost("h4",ip="10.0.0.4/24",mac="00:00:00:00:00:04")
        self.addHost("h5",ip="10.0.0.5/24",mac="00:00:00:00:00:05")
        self.addHost("h6",ip="10.0.0.6/24",mac="00:00:00:00:00:06")
        self.addHost("h7",ip="10.0.0.7/24",mac="00:00:00:00:00:07")
        self.addHost("h8",ip="10.0.0.8/24",mac="00:00:00:00:00:08")

        

        self.addLink("s1", "s2", **switch_config_video)
        self.addLink("s2", "s4", **switch_config_video)
        self.addLink("s1", "s3", **switch_config_non_video)
        self.addLink("s3", "s4", **switch_config_non_video)

        self.addLink("h1", "s1", **host_config)
        self.addLink("h2", "s1", **host_config)
        self.addLink("h6", "s1", **host_config)
        self.addLink("h7", "s2", **host_config)
        self.addLink("h5", "s3", **host_config)
        self.addLink("h3", "s4", **host_config)
        self.addLink("h4", "s4", **host_config)
        self.addLink("h8", "s4", **host_config)





# topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}


try:
    if __name__ == "__main__":
        
        setLogLevel("info")
 
        topo = NetworkSlicingTopo()
        net = Mininet(
            topo=topo,
            link=TCLink,
            controller=RemoteController("c0", ip="127.0.0.1"),
            switch=OVSKernelSwitch,
            build=False,
            autoSetMacs=True,
            autoStaticArp=True,
        )

        # Build
        print("[INFO] Building")
        net.build()

        # Start
        print("[INFO] Starting")
        net.start()

        dumpNodeConnections(net.hosts)

        inMenu = True
        while inMenu:
            choice = input("\n*** MENU:\n1) Open CLI\n2) iperf \n3) Stop network simulation\nACTION: ")
            if choice=="1":
                #1 = Mininet CLI
                CLI(net)
            elif choice=="2":
                    network_map = mapNetworkScenarios(net)
                    network_map = json.dumps(network_map)
                    print(network_map)
            elif choice=="3":
                inMenu = False




        net.stop()
        os.system("sudo mn -c && clear")

except Exception as e: 
    info("\n*** Osti errore popo!\n")
    print(e)
    net.stop()

    