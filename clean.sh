sudo mn -c  # Rimuove la configurazione Mininet precedente
# Delete all flow entries on Open vSwitch (OVS) bridges
for bridge in $(sudo ovs-vsctl list-br)
do
    sudo ovs-ofctl del-flows $bridge
done
