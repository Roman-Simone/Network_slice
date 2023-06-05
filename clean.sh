sudo mn -c  # Rimuove la configurazione Mininet precedente
sudo ifconfig s1-eth2 down
sudo ifconfig s2-eth2 down
sudo ip link delete s1-eth2
sudo ip link delete s2-eth2
