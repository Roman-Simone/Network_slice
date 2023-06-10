import os
import shlex
import time

from subprocess import check_output

from comnetsemu.cli import CLI
from comnetsemu.net import Containernet, VNFManager
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.util import dumpNodeConnections

from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, RemoteController
    
class NetworkSlicingTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        # two templates for links creation
        host_config = {}
        switch_config = {}

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

        

        self.addLink("s1", "s2", **switch_config)
        self.addLink("s2", "s4", **switch_config)
        self.addLink("s1", "s3", **switch_config)
        self.addLink("s3", "s4", **switch_config)

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

        CLI(net)


        os.system("sudo mn -c && clear")
        net.stop()
except Exception as e: 
    info("\n*** Osti errore popo!\n")
    print(e)
    net.stop()