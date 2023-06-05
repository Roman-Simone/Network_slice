from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Node, OVSSwitch,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import dumpNodeConnections
from mininet.node import RemoteController
from os import system


class MyTopology(Topo):
    
    def __init__(self):


        Topo.__init__(self)

        http_link_config = dict(bw=2)
        video_link_config = dict(bw=15)
        host_link_config = dict()

        # Aggiungi host specificando gli indirizzi IP
        h1 = self.addHost('h1', ip='10.0.0.1/24',mac="00:00:00:00:00:01")
        h2 = self.addHost('h2', ip='10.0.0.2/24',mac="00:00:00:00:00:02")
        h3 = self.addHost('h3', ip='10.0.0.3/24',mac="00:00:00:00:00:03")
        h4 = self.addHost('h4', ip='10.0.0.4/24',mac="00:00:00:00:00:04")
        h5 = self.addHost('h5', ip='10.0.0.5/24',mac="00:00:00:00:00:05")
                
                

        switches = {}
        for i in range(3):
            sconfig = {"dpid": "%016x" % (i + 1)}
            switches["s" + str(i+1)] = self.addSwitch("s%d" % (i + 1) ,**sconfig)


        # questo qui definisce i mac_to_port

        self.addLink(switches["s1"], switches["s2"], **video_link_config)
        self.addLink(switches["s1"], switches["s3"], **http_link_config)


        # Collego host e switch con un link
        self.addLink(h1, switches["s1"], **host_link_config)

        self.addLink(h2, switches["s2"], **host_link_config)
        self.addLink(h3, switches["s2"], **host_link_config)


        self.addLink(h4, switches["s3"], **host_link_config)
        self.addLink(h5, switches["s3"], **host_link_config)

                
        links_index = {}
        links_index["s1s2"] = 1
        links_index["s2s4"] = 2
        links_index["s1s3"] = 2
        links_index["s3s4"] = 2


if __name__ == '__main__':

    # Crea un'istanza della rete Mininet con la topologia personalizzata
    topo = MyTopology()
    net = Mininet(topo=topo,
                switch=OVSKernelSwitch,
                build=False,
                autoSetMacs=True,
                autoStaticArp=True,
                link=TCLink,
                controller=RemoteController( 'c0', ip='127.0.0.1')
                )

    # Avvia la rete
    net.start()

    # # Add RYU controller
    # controller = net.addController('ryu_controller', controller=RemoteController, ip='127.0.0.1', port=6653)

    # # Connect switches to the controller
    # for switch in net.switches:
    #     switch.start([controller])

    # Test connectivity
    dumpNodeConnections(net.hosts)



    # Esegui comandi di rete tra gli host utilizzando la CLI di Mininet
    CLI(net)

    # Arresta la rete
    net.stop()

    # Clear
    system("sudo mn -c && clear")
