from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.cmd.manager import main as ryu_run
from ryu import cfg
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import ether_types
from ryu.lib.packet import udp
from ryu.lib.packet import tcp
from ryu.lib.packet import icmp
from ryu.lib import hub
from mininet.log import info, setLogLevel
from subprocess import check_output
import shlex
import time
import paramiko
import requests
import socket


class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        setLogLevel("info")
        #Bind host MAC adresses to interface
        self.services_slicing_hosts = ["00:00:00:00:00:01","00:00:00:00:00:02","00:00:00:00:00:03","00:00:00:00:00:04"]
        self.host_connects_to_switch = {
            1 : ["00:00:00:00:00:01","00:00:00:00:00:02"],
            2 : ["00:00:00:00:00:07"],
            3 : ["00:00:00:00:00:05"],
            4 : ["00:00:00:00:00:03","00:00:00:00:00:04"]
        }
        self.slice_host = {
            "00:00:00:00:00:01" : 1,
            "00:00:00:00:00:02" : 1,
            "00:00:00:00:00:03" : 1,
            "00:00:00:00:00:04" : 1,
            "00:00:00:00:00:05" : 2,
            "00:00:00:00:00:06" : 2,
            "00:00:00:00:00:07" : 3,
            "00:00:00:00:00:08" : 3,
        }
        self.mac_to_port = {
            1: {
                "00:00:00:00:00:01": 3,
                "00:00:00:00:00:02": 4,
                "00:00:00:00:00:05": 2,
                "00:00:00:00:00:06": 5,
            },
            2: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:03": 2,
                "00:00:00:00:00:04": 2,
                "00:00:00:00:00:07": 3,
                "00:00:00:00:00:08": 2
            },
            3: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:03": 2,
                "00:00:00:00:00:04": 2,
                "00:00:00:00:00:05": 3,
                "00:00:00:00:00:06": 1
            },
            4: {
                "00:00:00:00:00:03": 3,
                "00:00:00:00:00:04": 4,
                "00:00:00:00:00:07": 1,
                "00:00:00:00:00:08": 5,
            },
        }

        

        #9998 used for iperf testing, 9999 used for service packets
        self.slice_TCport = [9998, 9999]

        #Associate interface to slice
        self.slice_ports = {
            1: {1: 1, 2: 2}, 
            4: {1: 1, 2: 2},
        }
        self.end_swtiches = [1, 4]
    
        self.link_stats = {}



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #Construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):


        #Get packet info
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id

        # print(src,dst,dpid)
        #check stesso slice
        if dpid in self.mac_to_port and ((src in self.slice_host.keys() and dst in self.slice_host.keys()) and self.slice_host[src] == self.slice_host[dst]):

            
            # check se gli host di partenza e arrivo sono tra quelli che fanno lo slicing di servizio
            if src in self.services_slicing_hosts and dst in self.services_slicing_hosts:
                # check se l'host di arrivo è direttamente connesso allo switch (dpid)
                if dst in self.host_connects_to_switch[dpid]:
                    print("Invio diretto")
                    
                    out_port = self.mac_to_port[dpid][dst]
                    print("outport " + str(out_port))
                    actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                    match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
                    self.add_flow(datapath, 1, match, actions) #ok
                    self._send_package(msg, datapath, in_port, actions)

                elif dpid in self.end_swtiches :
                    print("siamo nello switch 1 o 4")

                    # siamo nello switch 1 o 4

                    #decidere se andare sulla slice video (UDP) o non-video (NON UDP)

                    if (pkt.get_protocol(udp.udp)):
                        print("siamo nella slice 1 video")
                        #siamo nella slice 1 
                        slice_number = 1
                        out_port = self.slice_ports[dpid][slice_number]
                        match = datapath.ofproto_parser.OFPMatch(
                            in_port=in_port,
                            eth_dst=dst,
                            eth_type=ether_types.ETH_TYPE_IP,
                            ip_proto=0x11,  # udp
                            udp_dst=pkt.get_protocol(udp.udp).dst_port,
                        )
                        actions = [datapath.ofproto_parser.OFPActionSetQueue(12),datapath.ofproto_parser.OFPActionOutput(out_port)]
                        self.add_flow(datapath, 2, match, actions) #ok
                        self._send_package(msg, datapath, in_port, actions)


                    else : 
                        print("siamo nella slice 1 non video")
                        #siamo nella slice 2
                        # mandare pacchetti degli altri tipi

                        if pkt.get_protocol(tcp.tcp):
                            print("tcp")
                            #Create new flow automatically and send to low performance slice
                            slice_number = 2
                            out_port = self.slice_ports[dpid][slice_number]
                            match = datapath.ofproto_parser.OFPMatch(
                                in_port=in_port,
                                eth_dst=dst,
                                eth_src=src,
                                eth_type=ether_types.ETH_TYPE_IP,
                                ip_proto=0x06,  # tcp
                            )
                            actions = [datapath.ofproto_parser.OFPActionSetQueue(34),datapath.ofproto_parser.OFPActionOutput(out_port)]
                            self.add_flow(datapath, 1, match, actions) #ok
                            self._send_package(msg, datapath, in_port, actions)
                        elif pkt.get_protocol(icmp.icmp):
                            print("icmp")
                            #Create new flow automatically and send to low performance slice
                            slice_number = 2
                            out_port = self.slice_ports[dpid][slice_number]
                            match = datapath.ofproto_parser.OFPMatch(
                                in_port=in_port,
                                eth_dst=dst,
                                eth_src=src,
                                eth_type=ether_types.ETH_TYPE_IP,
                                ip_proto=0x01,  # icmp
                            )
                            actions = [datapath.ofproto_parser.OFPActionSetQueue(34),datapath.ofproto_parser.OFPActionOutput(out_port)]
                            self.add_flow(datapath, 1, match, actions) #ok
                            self._send_package(msg, datapath, in_port, actions)

                    
                    out_port = self.slice_ports[dpid][slice_number]

                else :

                    # siamo nello switch 2 o 3 oppure 
                    print("siamo nello switch 2 o 3")

                    # Extract the output port
                    out_port = self.mac_to_port[dpid][dst]

                    # Define a list of actions that are executed if the new flow entry is matched
                    actions = [datapath.ofproto_parser.OFPActionSetQueue(12),datapath.ofproto_parser.OFPActionOutput(out_port)]

                    # Creating a new OFPMatch object to match incoming packets based on the destination MAC address
                    match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
                    
                    # Add a new flow entry to the flow table of the switch
                    self.add_flow(datapath, 1, match, actions)#ok

                    # Send the packet
                    self._send_package(msg, datapath, in_port, actions)

            elif src not in self.services_slicing_hosts and dst not in self.services_slicing_hosts:

                # Extract the output port
                if dst in self.mac_to_port[dpid] and self.slice_host[src] == self.slice_host[dst]:
                    print("caso slice 2 o 3")
                    out_port = self.mac_to_port[dpid][dst]

                    # Define a list of actions that are executed if the new flow entry is matched
                    actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

                    # Creating a new OFPMatch object to match incoming packets based on the destination MAC address
                    match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
                    
                    # Add a new flow entry to the flow table of the switch
                    # self.add_flow(datapath, 1, match, actions)

                    # Send the packet
                    self._send_package(msg, datapath, in_port, actions)


                # print("outport " + str(out_port))

                # match = datapath.ofproto_parser.OFPMatch(
                #     in_port=in_port,
                #     eth_dst=dst,
                #     eth_type=ether_types.ETH_TYPE_IP,
                #     ip_proto=0x11,  # udp
                #     udp_dst=pkt.get_protocol(udp.udp).dst_port,
                # )

                # actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                # self.add_flow(datapath, 2, match, actions)
                # self._send_package(msg, datapath, in_port, actions)










        #     if dst in self.host_connects_to_switch[dpid]:
        #         print("1\n")
        #         #Create new flow based on known flow table
        #         out_port = self.mac_to_port[dpid][dst]
        #         print("outport " + str(out_port))
        #         actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #         match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
        #         self.add_flow(datapath, 1, match, actions)
        #         self._send_package(msg, datapath, in_port, actions)
        #     elif (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port in self.slice_TCport):
        #         #Create new flow automatically and send to high performance slice
        #         print("2\n")

        #         slice_number = self.current_slice
        #         out_port = self.slice_ports[dpid][slice_number]
        #         print("outport " + str(out_port))

        #         match = datapath.ofproto_parser.OFPMatch(
        #             in_port=in_port,
        #             eth_dst=dst,
        #             eth_type=ether_types.ETH_TYPE_IP,
        #             ip_proto=0x11,  # udp
        #             udp_dst=pkt.get_protocol(udp.udp).dst_port,
        #         )

        #         actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #         self.add_flow(datapath, 2, match, actions)
        #         self._send_package(msg, datapath, in_port, actions)
        #     elif (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port not in self.slice_TCport):
        #         #Create new flow automatically and send to low performance slice
        #         print("3\n")
        #         slice_number = 2
        #         if self.current_slice == 2:
        #             slice_number = 1
        #         out_port = self.slice_ports[dpid][slice_number]
        #         print("outport " + str(out_port))
        #         match = datapath.ofproto_parser.OFPMatch(
        #             in_port=in_port,
        #             eth_dst=dst,
        #             eth_src=src,
        #             eth_type=ether_types.ETH_TYPE_IP,
        #             ip_proto=0x11,  # udp
        #             udp_dst=pkt.get_protocol(udp.udp).dst_port,
        #         )
        #         actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #         self.add_flow(datapath, 1, match, actions)
        #         self._send_package(msg, datapath, in_port, actions)
        #     elif pkt.get_protocol(tcp.tcp):
        #         #Create new flow automatically and send to low performance slice
        #         print("4\n")
        #         slice_number = 2
        #         if self.current_slice == 2:
        #             slice_number = 1
        #         out_port = self.slice_ports[dpid][slice_number]
        #         print("outport " + str(out_port))
        #         match = datapath.ofproto_parser.OFPMatch(
        #             in_port=in_port,
        #             eth_dst=dst,
        #             eth_src=src,
        #             eth_type=ether_types.ETH_TYPE_IP,
        #             ip_proto=0x06,  # tcp
        #         )
        #         actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #         self.add_flow(datapath, 1, match, actions)
        #         self._send_package(msg, datapath, in_port, actions)
        #     elif pkt.get_protocol(icmp.icmp):
        #         #Create new flow automatically and send to low performance slice
        #         print("5\n")
        #         slice_number = 2
        #         if self.current_slice == 2:
        #             slice_number = 1
        #         out_port = self.slice_ports[dpid][slice_number]
        #         print("outport " + str(out_port))
        #         match = datapath.ofproto_parser.OFPMatch(
        #             in_port=in_port,
        #             eth_dst=dst,
        #             eth_src=src,
        #             eth_type=ether_types.ETH_TYPE_IP,
        #             ip_proto=0x01,  # icmp
        #         )
        #         actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #         self.add_flow(datapath, 1, match, actions)
        #         self._send_package(msg, datapath, in_port, actions)
        # elif dpid not in self.end_swtiches:
        #     print("6\n")
        #     #Unknown switch, flood
        #     out_port = ofproto.OFPP_FLOOD
        #     print("outport " + str(out_port))
        #     actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        #     match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
        #     self.add_flow(datapath, 1, match, actions)
        #     self._send_package(msg, datapath, in_port, actions)