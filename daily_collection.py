import json
import time
from pynput.mouse import Button, Controller
import keyboard
from pynput import mouse


def save_coordinates():
    coordinates_data = {
        "생활_스킬": None,
        "일상_채집": None,
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

    for target in ["생활_스킬", "일상_채집"]:
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


def load_coordinates():
    try:
        with open('daily_collection_regions.json', 'r', encoding='utf-8') as f:
            all_coordinates = json.load(f)
            if not all_coordinates:
                print("저장된 좌표 세트가 없습니다.")
                return None

            print("\n저장된 좌표 세트:")
            for idx, name in enumerate(all_coordinates.keys(), 1):
                print(f"{idx}. {name}")

            while True:
                print("\n사용할 좌표 세트 번호를 선택해주세요:")
                try:
                    choice = int(input().strip())
                    if 1 <= choice <= len(all_coordinates):
                        selected_name = list(all_coordinates.keys())[choice - 1]
                        print(f"'{selected_name}' 좌표 세트를 선택했습니다.")
                        return all_coordinates[selected_name]
                    else:
                        print("올바른 번호를 입력해주세요.")
                except ValueError:
                    print("숫자를 입력해주세요.")

    except FileNotFoundError:
        print("좌표 정보 파일을 찾을 수 없습니다.")
        return None


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

    mouse = Controller()
    print("매크로가 시작되었습니다. 'q' 키를 누르면 종료됩니다.")

    try:
        while not keyboard.is_pressed('q'):
            print("캐릭터 화면으로 이동합니다.")
            keyboard.press_and_release("c")

            # 생활 스킬 클릭
            perform_click(mouse, *coords["생활_스킬"])

            # 일상 채집 클릭
            perform_click(mouse, *coords["일상_채집"])

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
            wait_seconds = 120
            print(f"{wait_seconds}초 대기 중...")
            for i in range(wait_seconds, 0, -1):
                if keyboard.is_pressed('q'):
                    break
                if i % 5 == 0:
                    print(f"남은 시간: {i}초")
                time.sleep(1)

    except KeyboardInterrupt:
        print("\n매크로가 중지되었습니다.")

# perform_click과 run_macro 함수는 동일하게 유지

if __name__ == "__main__":
    print("다음 중 선택해주세요:")
    print("1. 새로운 좌표 저장 (r)")
    print("2. 매크로 실행 (다른 아무 키나 누르세요)")

    if keyboard.read_event(suppress=True).name == 'r':
        save_coordinates()
        print("\n좌표 저장이 완료되었습니다. 매크로를 실행하려면 프로그램을 다시 실행해주세요.")
    else:
        print("매크로를 시작하려면 's' 키를 누르세요...")
        keyboard.wait('s')
        run_macro()