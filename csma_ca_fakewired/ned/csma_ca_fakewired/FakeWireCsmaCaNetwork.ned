package csma_ca_fakewired;

import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.apsk.packetlevel.ApskScalarRadioMedium;

network FakeWireCsmaCaNetwork
{
    parameters:
        int numNodes = default(10);
    submodules:
        radioMedium: ApskScalarRadioMedium {
            @display("p=100,100;i=block/wifirouter");
            // ---- 매체를 '유선처럼' 만들기 위한 물리계층 설정 ----
            backgroundNoise.power = -110dBm;           // 적당한 잡음
            pathLoss.typename = "FreeSpacePathLoss";   // 경로손실 모델
            pathLoss.alpha = 0;                        // 감쇠 없음
            fading.typename = "";                      // 페이딩 끔
        }
        host[numNodes]: WirelessHost {
            @display("p=400,150");                     // 자동배치 인자 제거
            mobility.typename = "StationaryMobility";
            mobility.initialX = 10m * index;           // 각 호스트 X좌표 다르게
            mobility.initialY = 0m;
            mobility.initialZ = 0m;

            // 전송전력/수신감도(선택적으로 낮게/높게 조정)
            wlan[*].radio.transmitter.power = 20mW;
            wlan[*].radio.receiver.sensitivity = -120dBm;
        }
}
