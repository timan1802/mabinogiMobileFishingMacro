import json
import time

import keyboard
import win32con
import win32gui
from pynput import mouse
from pynput.mouse import Button, Controller

WAIT_SECONDS = 50

def save_coordinates():
    coordinates_data = {
        "생활_스킬": None,
        "채집_카테고리": None,
        "need_scroll": None,
        "채집물": None,
        "가까운_위치": None
    }

    global current_target
    scroll_detected = False

    def on_click(x, y, button, pressed):
        global current_target
        if button == mouse.Button.left and pressed:
            coordinates_data[current_target] = (x, y)
            print(f'{current_target} 좌표가 저장되었습니다: ({x}, {y})')
            return False

    def on_scroll(x, y, dx, dy):
        nonlocal scroll_detected
        scroll_detected = True

    print('좌표를 입력받아 저장을 시작합니다.')
    print("마비노기 화면으로 이동후 c 키를 눌러주세요...")
    keyboard.wait('c')

    for target in ["생활_스킬", "채집_카테고리"]:
        print(f"\n{target.replace('_', ' ')} 위치를 클릭해주세요.")
        current_target = target
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    print("\n채집물 위치를 클릭해주세요. 스크롤를 기억합니다.")
    current_target = "채집물"
    with mouse.Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

    coordinates_data["need_scroll"] = scroll_detected

    print("\n가까운 위치를 클릭해주세요.")
    current_target = "가까운_위치"
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # 좌표 세트의 이름 입력받기
    print("\n이 좌표 세트의 이름을 입력해주세요 (예: 루아브릿지, 티르코네일 등):")
    set_name = input().strip()

    # 기존 데이터 로드 또는 새로운 딕셔너리 생성
    try:
        with open('daily_collection_regions.json', 'r', encoding='utf-8') as f:
            all_coordinates = json.load(f)
    except FileNotFoundError:
        all_coordinates = {}

    # 새로운 좌표 세트 저장
    all_coordinates[set_name] = coordinates_data

    # 모든 데이터를 파일에 저장
    with open('daily_collection_regions.json', 'w', encoding='utf-8') as f:
        json.dump(all_coordinates, f, ensure_ascii=False, indent=2)

    print(f"\n'{set_name}' 좌표 세트가 저장되었습니다.")
    print("저장된 데이터:")
    for key, value in coordinates_data.items():
        print(f"{key.replace('_', ' ')}: {value}")


def get_numeric_keyboard_input():
    """숫자 키만 입력 받는 함수"""
    while True:
        # 이전 입력 버퍼 비우기
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()

        print("\n사용할 좌표 세트 번호를 선택해주세요 (종료: q):")
        event = keyboard.read_event(suppress=True)

        if event.event_type == 'down':
            if event.name == 'q':
                return 'q'
            if event.name.isdigit():
                return event.name
            else:
                print("숫자만 입력해주세요")

def load_coordinates():
    try:
        with open('daily_collection_regions.json', 'r', encoding='utf-8') as f:
            all_coordinates = json.load(f)
            if not all_coordinates:
                print("저장된 좌표 세트가 없습니다.")
                return None

            print("\n저장된 좌표 세트:")
            coord_list = list(all_coordinates.keys())
            for idx, name in enumerate(coord_list, 1):
                print(f"{idx}. {name}")

            while True:
                user_input = get_numeric_keyboard_input()

                if user_input == 'q':
                    print("프로그램을 종료합니다.")
                    return None

                try:
                    choice = int(user_input)
                    if 1 <= choice <= len(coord_list):
                        selected_name = coord_list[choice-1]
                        print(f"선택된 좌표 세트: '{selected_name}'")
                        return all_coordinates[selected_name]
                    else:
                        print(f"유효한 번호를 입력해주세요 (1-{len(coord_list)})")
                except ValueError:
                    print(f"올바른 숫자를 입력해주세요 (1-{len(coord_list)})")

    except FileNotFoundError:
        print("좌표 정보 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return None

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
    try:
        # 현재 포그라운드 윈도우 핸들 가져오기
        current_hwnd = win32gui.GetForegroundWindow()

        # 현재 포그라운드 윈도우의 스레드 ID 가져오기
        current_thread = win32gui.GetWindowThreadProcessId(current_hwnd)[0]

        # 대상 윈도우의 스레드 ID 가져오기
        target_thread = win32gui.GetWindowThreadProcessId(hwnd)[0]

        # 스레드 입력 상태를 연결
        win32gui.AttachThreadInput(target_thread, current_thread, True)

        # 창이 최소화되어 있다면 복원
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # 창을 전면으로 가져오기
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)

        # 스레드 입력 상태 연결 해제
        win32gui.AttachThreadInput(target_thread, current_thread, False)

        # 잠시 대기하여 창 전환이 완료되도록 함
        time.sleep(0.5)

    except Exception as e:
        print(f"창 포커스 전환 중 오류 발생: {str(e)}")
        return False

    return True

def perform_click(mouse, x, y, delay=1):
    mouse.position = (x, y)
    time.sleep(delay)
    mouse.click(Button.left)
    time.sleep(delay)


def run_macro():
    # 좌표 데이터 로드
    coords = load_coordinates()
    if not coords:
        return

    # 게임 창 찾기 및 포커스 이동
    # TODO module 'win32gui' has no attribute 'GetWindowThreadProcessId' 오류 발생. 수정 필요
    # window_handle = find_mabinogi_window()
    # if window_handle:
    #     print("마비노기 모바일 창을 찾았습니다. 창으로 포커스를 이동합니다.")
    #     if focus_window(window_handle):
    #         # 포커스 이동 성공 후 1초 대기
    #         time.sleep(1)
    #     else:
    #         print("창 포커스 이동 실패")
    #         return
    # else:
    #     print("마비노기 모바일 창을 찾을 수 없습니다.")
    #     return

    mouse = Controller()
    print("매크로가 시작되었습니다. 'q' 키를 누르면 종료됩니다.")
    sleep_with_countdown(5, "마비노기 모바일 창으로 이동하세요.")

    try:
        while not keyboard.is_pressed('q'):
            print("캐릭터 화면으로 이동합니다.")
            keyboard.press_and_release("c")

            # 생활 스킬 클릭
            perform_click(mouse, *coords["생활_스킬"])

            # 일상 채집 클릭
            perform_click(mouse, *coords["채집_카테고리"])

            # 스크롤이 필요한 경우 처리
            if coords["need_scroll"]:
                mouse.position = coords["채집물"]
                time.sleep(0.5)

                # 스크롤 수행
                for _ in range(6):
                    mouse.scroll(0, -1)  # 항상 아래로 스크롤
                    time.sleep(0.1)  # 각 스크롤 사이에 약간의 딜레이

                time.sleep(0.5)

            # 채집물 클릭
            perform_click(mouse, *coords["채집물"])

            # 가까운 위치 클릭
            perform_click(mouse, *coords["가까운_위치"])

            # 대기 시간 설정
            print(f"{WAIT_SECONDS}초 대기 중...")
            for i in range(WAIT_SECONDS, 0, -1):
                if keyboard.is_pressed('q'):
                    break
                if i % 5 == 0:
                    print(f"남은 시간: {i}초")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n매크로가 중지되었습니다.")

# perform_click과 run_macro 함수는 동일하게 유지


def sleep_with_countdown(seconds, prefix=""):
    for i in range(int(seconds), 0, -1):
        print(f"{prefix} {i}초 후")  # \r 제거, 매 초마다 새 줄에 출력
        time.sleep(1)
    print(" " * 50)

def run_macro_with_clean_input():
    # 키보드 버퍼 초기화
    def clear_keyboard_buffer():
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    
    # print("매크로를 시작하려면 '2' 키를 누르세요...")
    # keyboard.wait('2')
    
    # 키보드 버퍼 비우기
    clear_keyboard_buffer()
    
    # stdin 버퍼 비우기
    import sys
    sys.stdin.flush()
    
    # 매크로 실행
    run_macro()

def get_numeric_key_input():
    """숫자 키만 입력 받는 함수"""
    while True:
        event = keyboard.read_event(suppress=True)
        if event.event_type == 'down':  # 키가 눌렸을 때만 처리
            if event.name.isdigit():  # 숫자 키인지 확인
                return event.name
            else:
                print("숫자만 입력해주세요 (1 또는 2)")

if __name__ == "__main__":
    print("다음 중 선택해주세요:")
    print("1. 새로운 좌표 저장")
    print("2. 매크로 실행")
    
    key = get_numeric_key_input()
    
    if key == '1':
        save_coordinates()
        print("\n좌표 저장이 완료되었습니다. 매크로를 실행하려면 프로그램을 다시 실행해주세요.")
    elif key == '2':
        run_macro_with_clean_input()
    else:
        print("잘못된 입력입니다.")