package csma_ca;

import inet.node.ethernet.EthernetHost;
import inet.node.ethernet.EthernetHub;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;
import ned.*;

network CsmaCaNetwork
{
    parameters:
        int numNodes @display("i=block/app;");

    submodules:
        hub: EthernetHub {
            @display("p=200,150;i=device/hub");
        }
        host[numNodes]: EthernetHost {
            @display("p=450,100,row,80");
        }
        configurator: Ipv4NetworkConfigurator {
            @display("p=100,50;i=block/cogwheel");
        }

    connections allowunconnected:
        for i=0..numNodes-1 {
            host[i].ethg <--> DatarateChannel { datarate = 100Mbps; delay = 0us; } <--> hub.ethg++;
        }
}
