import cv2
import numpy as np
import pyautogui
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
                    key, val = line.strip().split("=")
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

# 이미지 매칭 함수
def is_image_match(screenshot, template_path, threshold=0.8, debug=False):
    template = load_image(template_path)
    if template is None:
        return False

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if debug:
        print(f"[{template_path}] 매칭 점수: {max_val:.3f}")
        h, w = template.shape[:2]
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, max_loc, (max_loc[0]+w, max_loc[1]+h), (0, 0, 255), 2)
        resized_template = cv2.resize(template, (w, h))
        if resized_template.shape[0] != debug_img.shape[0]:
            height = min(resized_template.shape[0], debug_img.shape[0])
            resized_template = resized_template[:height, :, :]
            debug_img = debug_img[:height, :, :]
        combined = np.hstack((resized_template, debug_img))
        cv2.imshow(f"Debug - {template_path}", combined)
        cv2.waitKey(1)

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

        if is_image_match(screen_img, "img/done.png", debug=DEBUG_MODE):
            print("[상태] 낚시 종료 감지 → W 키 입력")
            keyboard.press_and_release("w")
            time.sleep(1.0)
            continue

        if is_image_match(screen_img, "img/start.png", debug=DEBUG_MODE):
            print("[상태] 낚시 시작 감지 → 스페이스바 입력")
            keyboard.press_and_release("space")
            time.sleep(1.0)
            continue

        if is_image_match(screen_img, "img/fishing.png", debug=DEBUG_MODE):
            print("[상태] 낚시 중...")
            bar_img = capture_screen(region_map["progress_bar"])
            if analyze_progress_bar(bar_img):
                print("[상태] 물고기 감지! 스페이스바 입력")
                keyboard.press_and_release("space")
                time.sleep(1.0)

        time.sleep(0.1)

if __name__ == "__main__":
    run_fishing_macro()
