import os
import time
import cv2
import keyboard
import numpy as np
import win32con
import win32gui
from mss import mss
from datetime import datetime, timedelta

# 디버그 모드
DEBUG_MODE = False

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
def analyze_progress_bar(screenshot, threshold_ratio=0.69):
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


def wait_for_fishing(region_map):
    """낚는 중 상태를 감지하고 10초 카운트다운을 수행하는 함수"""
    while True:
        print("[상태] 낚는 중 이미지 감지 대기중...")
        screen_img = capture_screen(region_map["state_icon"])
        if is_image_match(screen_img, "img/fishing.png", debug=DEBUG_MODE):
            waiting_second = 7  # 물고기가 걸렸든, 안걸렸든 둘다 처리가능한 최상의 시간
            print(f"[상태] 낚는 중 감지. {waiting_second}초후 스페이스바 입력.")
            for i in range(waiting_second, 0, -1):
                print(f"[카운트다운] {i}초 남음...")
                time.sleep(1.0)
            keyboard.press_and_release("space")
            time.sleep(1.0)
            break  # 내부 while 루프를 빠져나감
        time.sleep(1.0)
        continue

    print("낚시 완료. 💯")
    print("모션 대기 3초.")
    time.sleep(3.0)


def format_elapsed_time(elapsed_seconds):
    """경과 시간을 시:분:초 형식으로 변환"""
    hours = int(elapsed_seconds // 3600)
    minutes = int((elapsed_seconds % 3600) // 60)
    seconds = int(elapsed_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def run_fishing_macro():
    region_map = load_region()
    fishing_count = 0
    start_time = datetime.now()
    print(f"매크로 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')} (Ctrl + C로 종료)")

    while True:
        screen_img = capture_screen(region_map["state_icon"])

        if is_image_match(screen_img, "img/start.png", debug=DEBUG_MODE):
            fishing_count += 1
            current_time = datetime.now()
            elapsed_time = (current_time - start_time).total_seconds()
            elapsed_formatted = format_elapsed_time(elapsed_time)

            status_msg = (
                f"[상태] 낚시 가능 시작 감지\n"
                f"=> 경과 시간: {elapsed_formatted}\n"
                f"=> 총 낚시 횟수: {fishing_count}마리\n"
            )
            print(status_msg)
            
            keyboard.press_and_release("space")
            wait_for_fishing(region_map)
            sleep_with_countdown(1.0, "[대기]")
            continue

        keyboard.press_and_release("w")
        sleep_with_countdown(1.0, "[대기]")



def find_mabinogi_window():
    def callback(hwnd, window_list):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if "마비노기 모바일" in window_title:
                window_list.append(hwnd)
        return True

    window_list = []
    win32gui.EnumWindows(callback, window_list)
    return window_list[0] if window_list else None

def focus_window(hwnd):
    # 창이 최소화되어 있다면 복원
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    # 창을 전면으로 가져오고 포커스 설정
    win32gui.SetForegroundWindow(hwnd)

def check_game_window():
    window_handle = find_mabinogi_window()
    
    if window_handle:
        print("마비노기 모바일 창을 찾았습니다. 창으로 포커스를 이동합니다.")
        focus_window(window_handle)
        return True
    else:
        print("마비노기 모바일 창을 찾을 수 없습니다. 게임을 실행해주세요.")
        return False

def sleep_with_countdown(seconds, prefix=""):
    """
    주어진 시간(초) 동안 카운트다운을 출력하며 대기합니다.
    prefix: 카운트다운 메시지 앞에 붙일 문자열 (예: "[낚시 대기]")
    """
    for i in range(int(seconds * 10), 0, -1):
        print(f"{prefix} {i/10:.1f}초 후", end="\r")
        time.sleep(0.1)
    print(" " * 50, end="\r")  # 이전 메시지 지우기

if __name__ == "__main__":
    if check_game_window():
        # 창을 찾았을 경우, 매크로 실행
        time.sleep(1)  # 포커스 이동 후 잠시 대기
        run_fishing_macro()