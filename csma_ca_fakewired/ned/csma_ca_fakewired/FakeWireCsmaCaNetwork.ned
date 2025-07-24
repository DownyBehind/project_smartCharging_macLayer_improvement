// 시뮬레이션 코드를 체계적으로 관리하기 위한 패키지 이름입니다.
package csma_ca_fakewired;

// INET 프레임워크에서 제공하는 무선 호스트와 무선 매체 모듈을 가져옵니다.
import inet.node.inet.WirelessHost;
import inet.physicallayer.wireless.apsk.packetlevel.ApskScalarRadioMedium;
import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;

// 'FakeWireCsmaCaNetwork'라는 이름의 새로운 네트워크를 정의합니다.
network FakeWireCsmaCaNetwork
{
    // 네트워크 전체에서 사용할 파라미터를 정의하는 섹션입니다.
    parameters:
        // 노드(호스트)의 개수를 정의하는 정수형 파라미터입니다. 기본값은 10개입니다.
        int numNodes = default(10);

    // 네트워크를 구성하는 하위 모듈들을 정의하는 섹션입니다.
    submodules:
        configurator: Ipv4NetworkConfigurator {
            @display("p=100,200;i=block/cog"); // GUI에서 톱니바퀴 아이콘으로 표시
        }
        // 'radioMedium'이라는 이름의 무선 매체 모듈을 정의합니다.
        // 모든 무선 노드(호스트)가 이 매체를 공유하여 통신합니다.
        radioMedium: ApskScalarRadioMedium {
            // OMNeT++ GUI에서 이 모듈이 어떻게 보일지 설정합니다. (위치: p=100,100, 아이콘: wifirouter)
            @display("p=100,100;i=block/wifirouter");
            // ---- 아래는 무선 매체를 '유선처럼' 만들기 위한 물리 계층 설정입니다 ----
            // 배경 잡음의 세기를 -110dBm으로 매우 낮게 설정하여 신호 간섭을 최소화합니다.
            backgroundNoise.power = -110dBm;
            // 신호가 거리에 따라 어떻게 감쇠할지 결정하는 경로 손실 모델을 지정합니다.
            pathLoss.typename = "FreeSpacePathLoss";
            // 경로 손실 지수(alpha)를 0으로 설정하여 거리에 따른 신호 감쇠를 완전히 없앱니다.
            // 모든 노드가 서로의 신호를 동일한 세기로 수신하게 됩니다.
            pathLoss.alpha = 0;
            // 시간에 따라 신호의 세기가 변하는 페이딩(fading) 효과를 사용하지 않도록 설정합니다.
            fading.typename = "";
        }

        // 'host'라는 이름으로 'numNodes' 개수만큼의 'WirelessHost' 모듈 배열을 생성합니다.
        // 예를 들어 numNodes가 10이면 host[0]부터 host[9]까지 10개의 호스트가 생성됩니다.
        host[numNodes]: WirelessHost {
            // 호스트 모듈이 GUI에 표시될 위치를 설정합니다.
            @display("p=400,150");
            // 호스트의 이동성 모델을 'StationaryMobility'로 설정하여 움직이지 않도록 고정합니다.
            mobility.typename = "StationaryMobility";
            // 각 호스트의 초기 X 좌표를 설정합니다. 'index'는 호스트의 배열 번호(0, 1, 2...)를 의미하며,
            // 호스트들이 10m 간격으로 일렬로 배치됩니다. (host[0]은 0m, host[1]은 10m...)
            mobility.initialX = 10m * index;
            // 호스트들의 초기 Y 좌표를 0m로 설정합니다.
            mobility.initialY = 0m;
            // 호스트들의 초기 Z 좌표를 0m로 설정합니다.
            mobility.initialZ = 0m;

            // ---- 전송 전력 및 수신 감도 설정 ----
            // 모든 무선랜 인터페이스(wlan[*])의 송신 전력을 20mW로 설정합니다.
            wlan[*].radio.transmitter.power = 20mW;
            // 수신 감도를 -120dBm으로 매우 낮게(민감하게) 설정하여 아주 약한 신호도 수신할 수 있도록 합니다.
            // 이는 신호 감쇠를 없앤 설정과 함께 모든 노드가 서로 통신 가능하도록 보장합니다.
            wlan[*].radio.receiver.sensitivity = -120dBm;
        }
}