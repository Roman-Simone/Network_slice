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

class MyController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        setLogLevel("info")
        #Bind host MAC adresses to interface

        self.mac_to_port = {
            1: {
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:04": 2
            },
            2: {
                "00:00:00:00:00:01": 1
            },
            3: {
                "00:00:00:00:00:01": 1
            },


        }

        #9998 used for iperf testing, 9999 used for service packets
        self.slice_TCport = [9998, 9999]

        #Associate interface to slice
        self.slice_ports = {
            1: {2: 1, 3: 2}, 
        }

        #Server starts on h2
        self.current_sever_ip = "10.0.0.2"
        #The optimal slice at the beginning is 1
        self.current_slice = 1


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
        # ev is the EventOFPPacketIn event received

        # Extract the message inside the packet
        msg = ev.msg

        # Extract the datapath
        datapath = msg.datapath

        # Extract the input port
        in_port = msg.match["in_port"]

        # Create packet object from received message's data
        pkt = packet.Packet(msg.data)

        # Extract ethernet protocol from the packet
        eth = pkt.get_protocol(ethernet.ethernet)

        # Checks if ethernet frame type is LLDP
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
        # Extract the destination MAC address
        dst = eth.dst

        src = eth.src



        # Extract the dpid of the switch
        dpid = datapath.id

        print(src,dst,dpid)

        if dpid in self.mac_to_port:
        # Check if the destination MAC address is inside the dpid map of the mac_to_port table
            if dst in self.mac_to_port[dpid]: 
                

                # Extract the output port
                out_port = self.mac_to_port[dpid][dst]

                # Define a list of actions that are executed if the new flow entry is matched
                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

                # Creating a new OFPMatch object to match incoming packets based on the destination MAC address
                match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
                
                # Add a new flow entry to the flow table of the switch
                self.add_flow(datapath, 1, match, actions)

                # Send the packet
                self._send_package(msg, datapath, in_port, actions)

            elif pkt.get_protocol(icmp.icmp):
                #Create new flow automatically and send to low performance slice
                print("5\n")
                slice_number = 2
                if self.current_slice == 2:
                    slice_number = 1
                out_port = self.slice_ports[dpid][slice_number]
                match = datapath.ofproto_parser.OFPMatch(
                    in_port=in_port,
                    eth_dst=dst,
                    eth_src=src,
                    eth_type=ether_types.ETH_TYPE_IP,
                    ip_proto=0x01,  # icmp
                )
                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)


#     CONF = cfg.CONF
#     CONF.register_opts([
#         cfg.StrOpt('address', default='127.0.0.1', help='RYU controller IP address'),
#         cfg.IntOpt('port', default=6653, help='RYU controller port')
#     ])

#     ryu_run()
