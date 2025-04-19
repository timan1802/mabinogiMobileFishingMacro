import cv2
import numpy as np
import time
import keyboard
import os
from mss import mss


# 디버그 모드
DEBUG_MODE = True

# region.txt 불러오기
def load_region():
    region_map = {}
    if not os.path.exists("region.txt"):
        raise FileNotFoundError("region.txt 파일이 존재하지 않습니다.")
    with open("region.txt", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    key, val = line.strip().split(":")
                    region_map[key] = tuple(map(int, val.strip().split(",")))
                except ValueError:
                    print(f"[경고] 무시된 잘못된 줄: {line.strip()}")
    return region_map

# 이미지 불러오기
def load_image(path):
    if not os.path.exists(path):
        print(f"이미지 파일 없음: {path}")
        return None
    return cv2.imread(path)


def is_image_match(screenshot, template_path, threshold=0.8, debug=False):
    template = load_image(template_path)
    if template is None:
        return False

    # 이미지 전처리
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # 노이즈 제거
    screenshot_gray = cv2.GaussianBlur(screenshot_gray, (3,3), 0)
    template_gray = cv2.GaussianBlur(template_gray, (3,3), 0)
    
    # 히스토그램 평활화
    screenshot_gray = cv2.equalizeHist(screenshot_gray)
    template_gray = cv2.equalizeHist(template_gray)

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if debug:
        print(f"매칭 점수: {max_val:.3f} (임계값: {threshold})")

    return max_val >= threshold

# 화면 캡처 함수 (mss 사용)
def capture_screen(region):
    with mss() as sct:
        monitor = {"top": region[1], "left": region[0], "width": region[2], "height": region[3]}
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

# 프로그레스 바 판단 함수
def analyze_progress_bar(screenshot, threshold_ratio=0.7):
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    white_pixels = np.sum(binary == 255)
    total_pixels = binary.shape[0] * binary.shape[1]
    ratio = white_pixels / total_pixels
    if DEBUG_MODE:
        print(f"Progress Ratio: {ratio:.2f}")
        cv2.imshow("Progress Bar", binary)
        cv2.waitKey(1)
    return ratio >= threshold_ratio

# 메인 루프 함수
def run_fishing_macro():
    region_map = load_region()
    print("매크로 시작 (Ctrl + C로 종료)")

    while True:
        screen_img = capture_screen(region_map["state_icon"])

        # 나침반 감지가 안됨.
        # if is_image_match(screen_img, "img/done.png", debug=DEBUG_MODE):
        #     print("[상태] 낚시 종료 감지 → W 키 입력")
        #     keyboard.press_and_release("w")
        #     time.sleep(1.0)
        #     continue

        if is_image_match(screen_img, "img/start.png", debug=DEBUG_MODE):
            print("[상태] 낚시 가능 시작 감지 → 스페이스바 입력")
            keyboard.press_and_release("space")
            time.sleep(13.0)
            continue

        # 낚시 중 감지는 되지만, progress_bar 감지가 안됨.
        # if is_image_match(screen_img, "img/fishing.png", debug=DEBUG_MODE):
        #     print("[상태] 낚시 중...")
        #     bar_img = capture_screen(region_map["progress_bar"])
        #     if analyze_progress_bar(bar_img):
        #         print("[상태] 물고기 감지! 스페이스바 입력")
        #         keyboard.press_and_release("space")
        #         time.sleep(1.0)

        keyboard.press_and_release("w")
        time.sleep(1.0)

if __name__ == "__main__":
    run_fishing_macro()