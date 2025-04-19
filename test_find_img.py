import os
import time
import cv2
import numpy as np
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


def is_image_match(screenshot, template_path, threshold=0.7, debug=False):
    template = load_image(template_path)
    if template is None:
        return False

    # 이미지 전처리
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # 노이즈 제거
    screenshot_gray = cv2.GaussianBlur(screenshot_gray, (3, 3), 0)
    template_gray = cv2.GaussianBlur(template_gray, (3, 3), 0)

    # 히스토그램 평활화
    screenshot_gray = cv2.equalizeHist(screenshot_gray)
    template_gray = cv2.equalizeHist(template_gray)

    # 스크린샷과 템플릿 이미지의 크기 출력
    screenshot_h, screenshot_w = screenshot.shape[:2]
    template_h, template_w = template.shape[:2]

    if debug:
        print(f"\n=== 디버그 정보 ===")
        print(f"템플릿 경로: {template_path}")
        print(f"스크린샷 크기: {screenshot_w}x{screenshot_h}")
        print(f"템플릿 크기: {template_w}x{template_h}")

        # 스크린샷과 템플릿 이미지 저장
        cv2.imwrite("debug_screenshot.png", screenshot)
        cv2.imwrite("debug_template.png", template)

    if template_h > screenshot_h or template_w > screenshot_w:
        if debug:
            print(f"[경고] 템플릿({template_w}x{template_h})이 스크린샷({screenshot_w}x{screenshot_h})보다 큽니다.")
        return False

    result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if debug:
        print(f"매칭 점수: {max_val:.3f} (임계값: {threshold})")
        print("==================")

        # 매칭 결과 시각화
        h, w = template.shape[:2]
        debug_img = screenshot.copy()
        cv2.rectangle(debug_img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 0, 255), 2)
        cv2.imwrite("debug_result.png", debug_img)

        # 창 위치 설정하여 겹치지 않게 표시
        cv2.namedWindow("Template")
        cv2.namedWindow("Screenshot")
        cv2.namedWindow("Result")

        cv2.moveWindow("Template", 0, 0)  # 템플릿 이미지는 좌상단
        cv2.moveWindow("Screenshot", template_w + 10, 0)  # 스크린샷은 템플릿 옆에
        cv2.moveWindow("Result", 0, template_h + 10)  # 결과는 템플릿 아래에

        cv2.imshow("Template", template)
        cv2.imshow("Screenshot", screenshot)
        cv2.imshow("Result", debug_img)
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
            print("낚시 종료 찾음")
            break

        if is_image_match(screen_img, "img/start.png", debug=DEBUG_MODE):
            print("낚시 시작 찾음")
            break

        if is_image_match(screen_img, "img/fishing.png", debug=DEBUG_MODE):
            print("낚시 중 찾음")
            break

        bar_img = capture_screen(region_map["progress_bar"])
        if analyze_progress_bar(bar_img):
            print("progress_bar 감지!")
            break

        time.sleep(1)

if __name__ == "__main__":
    run_fishing_macro()