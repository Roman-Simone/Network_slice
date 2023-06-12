#!/usr/bin/bash

clear

bash ./reset.sh


printf "[INFO] Loading Scenario Default \n"

printf "[INFO] Setting up switches...\n\n"

# # Delete all flow entries on Open vSwitch (OVS) bridges
# for bridge in $(sudo ovs-vsctl list-br)
# do
#     sudo ovs-ofctl del-flows $bridge
# done

# Switch 1
printf "Switch 1\n"
sudo ovs-vsctl -- \
set port s1-eth1 qos=@newqos -- \
set port s1-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=200000000 \
queues:12=@1q \
queues:34=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=6000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=8000000


# Switch 2
printf "\nSwitch 2\n"
sudo ovs-vsctl -- \
set port s2-eth1 qos=@newqos -- \
set port s2-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=200000000 \
queues:12=@1q \
queues:34=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=4000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=6000000 

# Switch 3
printf "\nSwitch 3\n"
sudo ovs-vsctl -- \
set port s3-eth1 qos=@newqos -- \
set port s3-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=200000000 \
queues:12=@1q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=8000000

# Switch 4
printf "\nSwitch 4\n"
sudo ovs-vsctl -- \
set port s4-eth1 qos=@newqos -- \
set port s4-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=200000000 \
queues:12=@1q \
queues:34=@2q \
queues:56=@3q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=10000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=4000000 -- \
--id=@3q create queue other-config:min-rate=1000000 other-config:max-rate=6000000

# Creating links
printf "\n[INFO] Creating links..."

# Switch 1
sudo ovs-ofctl add-flow s1 cookie=0x0,duration=70.374s,table=0,n_packets=22,n_bytes=1596,priority=0,actions=CONTROLLER:65535


# sudo ovs-ofctl add-flow s1 ip,priority=65500,in_port=1,idle_timeout=0,actions=set_queue:12,output:3

# sudo ovs-ofctl add-flow s1 ip,priority=65500,in_port=5,idle_timeout=0,actions=drop

# sudo ovs-ofctl add-flow s1 ip,priority=65500,in_port=4,idle_timeout=0,actions=set_queue:34,output:2
# sudo ovs-ofctl add-flow s1 ip,priority=65500,in_port=2,idle_timeout=0,actions=set_queue:34,output:4

# sudo ovs-ofctl add-flow s1 ip,priority=65500,in_port=6,idle_timeout=0,actions=drop

# Switch 2
sudo ovs-ofctl add-flow s2 table=0,priority=65500,in_port=3,idle_timeout=0,actions=set_queue:34,output:2
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.8,idle_timeout=0,actions=set_queue:34,output:3
sudo ovs-ofctl add-flow s2 cookie=0x0,duration=70.374s,table=0,n_packets=22,n_bytes=1596,priority=0,actions=CONTROLLER:65535


# Switch 3
sudo ovs-ofctl add-flow s3 table=0,priority=65500,in_port=1,idle_timeout=0,actions=set_queue:12,output:2
sudo ovs-ofctl add-flow s3 table=0,priority=65500,in_port=2,idle_timeout=0,actions=set_queue:12,output:1
sudo ovs-ofctl add-flow s3 cookie=0x0,duration=70.374s,table=0,n_packets=22,n_bytes=1596,priority=0,actions=CONTROLLER:65535

# sudo ovs-ofctl add-flow s3 table=0,priority=65500,in_port=1,idle_timeout=0,actions=set_queue:34,output:2
# sudo ovs-ofctl add-flow s3 table=0,priority=65500,in_port=2,idle_timeout=0,actions=set_queue:34,output:1


# Switch 4
sudo ovs-ofctl add-flow s4 table=0,priority=65500,in_port=5,idle_timeout=0,actions=set_queue:34,output:1
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.7,idle_timeout=0,actions=set_queue:34,output:5
sudo ovs-ofctl add-flow s4 cookie=0x0,duration=70.374s,table=0,n_packets=22,n_bytes=1596,priority=0,actions=CONTROLLER:65535

# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=1,idle_timeout=0,actions=set_queue:12,output:3
# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=3,idle_timeout=0,actions=set_queue:12,output:1

# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=5,idle_timeout=0,actions=drop

# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=2,idle_timeout=0,actions=set_queue:34,output:4
# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=4,idle_timeout=0,actions=set_queue:34,output:2

# sudo ovs-ofctl add-flow s4 ip,priority=65500,in_port=6,idle_timeout=0,actions=drop

printf "OK\n\n"


