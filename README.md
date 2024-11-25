  <div align="center">
    <img width="190" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/eb0ece56-e66a-4ede-bcd8-2ff7dc8013d2">
      <h1>실내 공기질 유지를 위한 자동 환기 공기 청정 시스템</h1>
  <h4>🗝️ KeyWords <h4/>
  <p>#AirQuality #AutomaticVentilation #AirPurification #IoT #SmartHome</p>
  <br>
  <img src="https://img.shields.io/badge/C-A8B9CC?style=flat-square&logo=C&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=Python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Arduino-00979D?style=flat-square&logo=Arduino&logoColor=white"/>
  <img src="https://img.shields.io/badge/Raspberry Pi-A22846?style=flat-square&logo=Raspberry Pi&logoColor=white"/>
  <br>
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=TensorFlow&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=Pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=flat-square&logo=Ubuntu&logoColor=white"/>
  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=flat-square&logo=Matplotlib&logoColor=white"/>
  <img src="https://img.shields.io/badge/MQTT-660066?style=flat-square&logo=MQTT&logoColor=white"/>
  <img src="https://img.shields.io/badge/Zigbee-EB0443?style=flat-square&logo=Zigbee&logoColor=white"/>


  </div>

---

# 기획의도
- 국민 소득 수준 증가 및 삶의 질에 관한 관심이 증대되고, 하루 중 대부분을 실내 환경에서 생활(일 평균 20.7시간, 86%)
- ‘건강한 실내 환경요소’에 국민 관심이 집중됨에 따라 실내 공기질 유지를 위한 자동 환기 공기 청정 시스템을 개발
- 실내 이산화탄소 정화 및 전염병의 공기 감염 예방을 위한 물리적 자연 환기 시스템 개발

# 서비스 소개
최적 실내 환경 유지 IoT 솔루션
- 실내 공기질 센싱 및 예측을 통한 환기 및 공기 청정 기능

# 기간 및 인원
- 기간 : 7개월
- 인원 : B.E 2명, F.E 1명

# 성과 (B.E 기여도 70%, 주관적 수치)
- Arduino 및 Raspberry Pi 통한 센싱 및 처리 시스템 아키텍처 설계 및 개발
- AWS DynamoDB, Zigbee, MQTT, Serial 통신 통합 서버 개발
- LSTM 및 GRU 모델 추출, Pandas, Matplotlib 활용 데이터 정제 및 전처리
- 하이퍼 파라미터 조정을 통한 성능 개선 (validation loss 0.06 → 0.0045)

# 기능 소개

### ⚙️ 공기 청정 및 예측 시스템(담당)
- 공기청정기에 부착된 다양한 센서를 통해 실내 공기질을 측정하고, 인공지능을 통해 공기질을 예측합니다.
- 예측 데이터를 기반으로 환기 기기를 자동으로 제어하여 최적의 실내 공기질을 유지합니다.

### 🏠 자동 환기 시스템(담당)
- 창문에 부착된 액추에이터를 통해 자동으로 창문을 개폐하여 환기를 시킵니다.
- 외부인의 침입을 감지하는 충격 센서가 포함되어 있습니다.

| <img width="650" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/f8963875-693a-425b-b665-f710ff043f6e"> |
| ----------------------------------------------------------------------------- |
| 공기청정기 및 액추에이터 구성도                                                            |

<details>
<summary>
🧑‍💻 애플리케이션 화면 </summary>
- 실내외 공기질 데이터를 시각화하여 사용자에게 제공하고, 기기들을 제어할 수 있는 인터페이스를 제공합니다.

|<img width="749" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/406d7557-de7a-45d2-a42b-40339683aa9b">|
| ----------------------------------------------------------------------------- |
| 애플리케이션 UI                                                               |
</details>

#  서버 아키텍처
<img width="583" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/2e3703bc-c3f8-486b-91d4-e1a0746bed19">

# 의사결정 알고리즘
<img width="565" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/d5a65e13-35db-4a8d-8cd8-f47334219ba6">

# 인공지능 흐름도
<img width="544" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/a4ac028e-71be-494a-ab08-2a8ce468756e">

# 머신러닝 모델 성능 비교
<img width="582" alt="image" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/17a681e9-0da2-4b49-ab29-6c023efd4a90">


# 팀 소개 (팀명: 불사조)
- 담당 교수: 임창균
- 팀원: 김동준, 진서형, 김가연

# 프로젝트 포스터
<img width="961" alt="컴퓨터공학과-졸업작품 판넬(불사조)" src="https://github.com/hey-dudegg/GreenDays_Project/assets/154962837/520180ea-0283-4007-8537-53b1531d8545">
