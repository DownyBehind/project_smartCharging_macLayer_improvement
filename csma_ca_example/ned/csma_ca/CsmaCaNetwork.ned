package csma_ca;

//
// 무선 CSMA/CA 실험용 간단 네트워크
//
import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.apsk.packetlevel.ApskScalarRadioMedium;

network CsmaCaNetwork
{
    parameters:
        int numNodes = default(5);   // INI 에서 **.numNodes 로 덮어씀
        @display("bgb=600,400");
    submodules:
        radioMedium: ApskScalarRadioMedium {
            @display("p=100,100");
        }
        host[numNodes]: WirelessHost {
            @display("p=250,120");   // 자동(row, col) 배치 제거
        }
}
