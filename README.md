# 🎣 마비노기 모바일 낚시 자동화 매크로

> 이미지 인식을 기반으로 마비노기 모바일 낚시를 자동화하는 Python 매크로입니다.  
> 다중 모니터를 지원하며, 낚시 이미지를 감지하여 자동으로 낚시를 수행합니다.
---
## ⚙️ 사용 방법
1. setup_region.py를 실행해서 자신의 모니터 좌표값을 찾아옵니다.
2. test_find_img.py를 실행해서 정상적으로 이미지가 매칭되는 지 확인합니다.
3. fishing_macro.py를 실행합니다. 실행 후에는 재빠르게 게임화면으로 전환해야 합니다.
   1. 파이썬을 관리자로 실행해야 keyboard가 제대로 동작합니다.
---

## 🛠️ 설치 방법

```bash
git clone https://github.com/yourname/mabinogiMobileFishingMacro.git
cd mabinogiMobileFishingMacro
pip install -r requirements.txt
```

> 필요한 기본 라이브러리:
> - `opencv-python`
> - `numpy`
> - `pyautogui`
> - `mss`
> - `Pillow`

---

## 📂 폴더 구조

```
mabinogiMobileFishingMacro/
├── img/                   # 상태 이미지 모음 (start.png, done.png, fishing.png 등)
├── setup_region.py        # 자동 좌표 설정용 스크립트
├── fishing_macro.py       # 매크로 실행 파일
├── test_find_img.py       # 이미지 탐색 테스트용 스크립트
├── region.txt             # 낚시 영역 좌표 저장 파일
└── README.md
```

## 📌 참고 사항

- 마비노기 클라이언트는 **전체화면 모드보다는 창 모드**에서 더 안정적으로 인식됩니다.
- 나침반과 프로그래스바의 이미지 매칭이 안되서 start.png로 낚시 가능여부만 판단해서 진행됩니다.
- 이미지 인식이 잘 안되면 임계값을 낮춰서 진행해 보세요.
