import time
import cv2
import numpy as np
import pyautogui
from mss import mss

# region.txt 파일에서 이미지별 좌표 영역을 불러오는 함수
def load_regions():
    regions = {}
    try:
        with open("region.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=")
                    regions[key] = tuple(map(int, val.split(",")))
    except FileNotFoundError:
        print("[!] region.txt 파일이 없습니다. setup_region.py를 먼저 실행하세요.")
        exit()
    return regions

# 특정 영역을 캡처해서 numpy 배열로 반환
def capture_region(region):
    left, top, width, height = region
    with mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        return np.array(screenshot)

# 지정한 이미지 템플릿이 해당 영역 내에 존재하는지 여부를 판단
def is_image_visible(region, template, threshold=0.9):
    screen = capture_region(region)

    # 템플릿 크기 검증
    if (template.shape[0] > screen.shape[0]) or (template.shape[1] > screen.shape[1]):
        print(f"[!] 템플릿이 화면 영역보다 큽니다. 템플릿: {template.shape}, 화면: {screen.shape}")
        return False

    # 채널 일치 확인 (BGR → Grayscale로 통일할 경우 추가)
    # screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    # template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= threshold

# 메인 매크로 함수
def main():
    print("[시작] region.txt 불러오는 중...")
    regions = load_regions()

    # 필요한 영역들이 모두 있는지 확인
    if not all(k in regions for k in ("start", "fishing")):
        print("[!] region.txt에 'start' 또는 'fishing' 영역 정보가 없습니다.")
        return

    # 이미지 템플릿 불러오기
    print("[✓] start.png, fishing.png 불러오는 중...")
    start_template = cv2.imread("img/start.png", cv2.IMREAD_COLOR)
    fishing_template = cv2.imread("img/fishing.png", cv2.IMREAD_COLOR)

    if start_template is None or fishing_template is None:
        print("[!] start.png 또는 fishing.png 파일이 없습니다.")
        return

    start_region = regions["start"]
    fishing_region = regions["fishing"]

    print("[▶] 낚시 매크로 시작합니다. Ctrl+C로 종료하세요.")
    try:
        while True:
            is_start = is_image_visible(start_region, start_template)
            is_fishing = is_image_visible(fishing_region, fishing_template)

            if is_start:
                # 낚시 준비 완료 상태 → 시작 버튼 클릭
                print("[🎯] 낚시 준비 완료 → 시작 버튼 클릭")
                x, y, _, _ = start_region
                pyautogui.moveTo(x + 5, y + 5)
                pyautogui.click()
                time.sleep(1)

            elif is_fishing:
                # 낚시 중 상태 → 일정 시간 대기
                print("[🎣] 낚시 진행 중... 대기 중")
                time.sleep(1)

            else:
                # 둘 다 안 보이면 → 낚시 성공 또는 실패 → SPACE 입력
                print("[✓] 낚시 완료 추정 → SPACE 입력")
                pyautogui.press("space")
                time.sleep(3)  # 결과 처리 대기 후 다음 루프

    except KeyboardInterrupt:
        print("\n[종료] 사용자에 의해 종료됨")

# 프로그램 시작
if __name__ == "__main__":
    main()
