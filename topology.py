import os
import json
import subprocess
from comnetsemu.cli import CLI
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import info, setLogLevel
from mininet.util import dumpNodeConnections

from mininet.topo import Topo
from mininet.node import OVSKernelSwitch, RemoteController

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.parse import urlparse, parse_qs

from itertools import combinations
import logging

httpd = ""
avaibleScenarios = ["default","scenario1","scenario2","scenario3"]
logging.basicConfig(filename='log.txt', level=logging.INFO)

class MyHandler(BaseHTTPRequestHandler):
    def __init__(self, net, *args, **kwargs):
        self.net = net
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        # Save the log message to a file
        logging.info(format % args)

    def do_GET(self):

        if self.path == '/webapp/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Read the HTML file
            with open('WebApp/webapp.html', 'r') as file:
                html_content = file.read()

            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/get/throughput/tcp/':
            # Gestisci la chiamata API
            data = mapNetworkScenariosTcp(self.net)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))

        elif self.path == '/get/throughput/udp/':

            data = mapNetworkScenariosUdp(self.net)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))

        elif self.path == '/get/pingall/':

            data = pingall(self.net)
            print("data : {data}\n")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))

        elif '/changeScenario/' in self.path:

            print("Richiesta scenario arrivata")

            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            if 'data' in query_params:
                data = query_params['data'][0]  # Assume che ci sia solo un parametro 'data'
                # Fai qualcosa con il parametro 'data' ricevuto dal client
                if(data in avaibleScenarios):
                    print(data)
                    process = subprocess.Popen(f"cd scenarios/ && ./{data}.sh", shell=True, stdout=subprocess.PIPE)
                    process.wait()

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                
                else :
                    self.send_response(204)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

            else:
                self.send_response(204)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()


def run_server(variable):
    global httpd
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, lambda *args, **kwargs: MyHandler(variable, *args, **kwargs))
    print('Server in esecuzione...')
    httpd.serve_forever()
    

def mapNetworkScenariosTcp(net: Mininet, host_pairs: list = [["h1","h3"],["h2","h4"],["h1","h4"],["h2","h3"],["h5","h6"],["h7","h8"]]) -> str :


    # Execute iperf on each pair
    network_map = {"network": []}

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
            host1_speed,host2_speed = net.iperf(hosts=[h1, h2], seconds=2) # Host connected, testing bandwidt
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

    return json.dumps(network_map)


    

def pingall(net: Mininet)->str:
    network :dict= {"h1": {},"h2":{},"h3":{},"h4":{},"h5": {},"h6":{},"h7":{},"h8":{}}

    all_slice = [["h1","h2","h3","h4"],["h5","h6"],["h7","h8"]]

    for lst in all_slice:
        all_pairs = list(combinations(lst, 2))
        for pair in all_pairs:
            hosts = []

            for host in net.hosts:
                if host.name in pair:
                    hosts.append(host)
            
            if len(hosts) != 2:
                continue

            h1, h2 = hosts
            result = net.ping([h1,h2],timeout="0.5")
            if result < 100 :
                network[h1.name][h2.name] = True 
                network[h2.name][h1.name] = True 
            else :
                network[h1.name][h2.name] = False 
                network[h2.name][h1.name] = False 

    
    return json.dumps(network, indent = 4) 


def mapNetworkScenariosUdp(net: Mininet, host_pairs: list = [["h1","h3"],["h2","h4"],["h1","h4"],["h2","h3"]])-> str:

        # Execute iperf on each pair
    network_map = {"network": []}

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
            iperf_result = net.iperf(hosts=[h1, h2],l4Type="UDP",seconds=2) # Host connected, testing bandwidth
            host1_speed = iperf_result[1]
            host2_speed = iperf_result[2]
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
    
    return json.dumps(network_map)

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

        os.system("bash ./scenarios/default.sh")

        dumpNodeConnections(net.hosts)

        # Crea un nuovo thread per eseguire run_server(my_variable)
        server_thread = threading.Thread(target=run_server, args=(net,))
        server_thread.start()


        inMenu = True
        while inMenu:
            choice = input("\n*** MENU:\n1) Open CLI\n2) iperf \n3) Stop network simulation\nACTION: ")
            if choice=="1":
                #1 = Mininet CLI
                CLI(net)
            elif choice=="2":
                    network_map_tcp = mapNetworkScenariosTcp(net)
                    network_map_udp = mapNetworkScenariosUdp(net)
            elif choice=="3":
                inMenu = False
                httpd.shutdown()




        net.stop()
        os.system("sudo mn -c && clear")

except Exception as e: 
    info("\n*** Osti errore popo!\n")
    print(e)
    httpd.shutdown()

    net.stop()

    