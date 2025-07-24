package csma_ca;

import inet.node.ethernet.EthernetSwitch;
import inet.node.ethernet.EthernetHost;

// 필요시 import 해서 쓸 수도 있지만, 아래처럼 직접 채널 정의하면 불필요
// import inet.linklayer.ethernet.common.EthernetLink;

channel Ethernet100M extends ned.DatarateChannel
{
    datarate = 100Mbps;
    delay = 0.1ms;   // 필요에 따라 조정
}

network CsmaCaNetwork
{
    parameters:
        int numNodes = default(5);
    submodules:
        sw: EthernetSwitch {
            @display("p=200,200;i=block/switch");
        }
        host[numNodes]: EthernetHost {
            @display("p=450,150,row,90");
        }
    connections allowunconnected:
        for i=0..numNodes-1 {
            host[i].ethg     <--> Ethernet100M <--> sw.ethg++;
        }
}
