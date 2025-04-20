import json
import time
from pynput.mouse import Button, Controller
import keyboard
from pynput import mouse

# 저장할 데이터 딕셔너리
coordinates_data = {
    "생활_스킬": None,
    "일상_채집": None,
    "need_scroll": None,  # 스크롤 필요 여부
    "채집물": None,
    "가까운_위치": None
}

def save_coordinates():
    global current_target
    scroll_detected = False
    
    def on_click(x, y, button, pressed):
        global current_target
        if button == mouse.Button.left and pressed:
            coordinates_data[current_target] = (x, y)
            print(f'{current_target} 좌표가 저장되었습니다: ({x}, {y})')
            return False  # 리스너 중지

    def on_scroll(x, y, dx, dy):
        nonlocal scroll_detected
        scroll_detected = True

    print('좌표를 입력받아 저장을 시작합니다.')
    print("마비노기 화면으로 이동후 c 키를 눌러주세요...")
    keyboard.wait('c')

    # 순서대로 좌표 입력 받기
    for target in ["생활_스킬", "일상_채집"]:
        print(f"\n{target.replace('_', ' ')} 위치를 클릭해주세요.")
        current_target = target
        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    # 채집물 좌표 입력 전 스크롤 감지 시작
    print("\n채집물 위치를 클릭해주세요. 스크롤를 기억합니다.")
    current_target = "채집물"
    with mouse.Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

    # 스크롤 여부 저장
    coordinates_data["need_scroll"] = scroll_detected

    # 마지막 좌표 입력 받기
    print("\n가까운 위치를 클릭해주세요.")
    current_target = "가까운_위치"
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    # 데이터를 파일에 저장
    with open('daily_collection_region.txt', 'w', encoding='utf-8') as f:
        json.dump(coordinates_data, f, ensure_ascii=False, indent=2)

    print("\n모든 좌표가 저장되었습니다.")
    print("저장된 데이터:")
    for key, value in coordinates_data.items():
        print(f"{key.replace('_', ' ')}: {value}")

def load_coordinates():
    try:
        with open('daily_collection_region.txt', 'r', encoding='utf-8') as f:
            return json.load(f)
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
                
                # 스크롤 수행, 스크롤 인식이 안되서 for문으로 여러번 처리.
                for _ in range(6):
                    mouse.scroll(0, -1)  # 항상 아래로 스크롤
                    time.sleep(0.1)  # 각 스크롤 사이에 약간의 딜레이
                
                time.sleep(0.5)
            
            # 채집물 클릭
            perform_click(mouse, *coords["채집물"])
            
            # 가까운 위치 클릭
            perform_click(mouse, *coords["가까운_위치"])
            
            # 1개 채집에 10, 11초 정도 걸림. 총 10개 채집.
            wait_seconds = 120
            print(f"{120}초 대기 중...")
            for i in range(120, 0, -1):
                if keyboard.is_pressed('q'):
                    break
                if i % 5 == 0:
                    print(f"남은 시간: {i}초")
                time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n매크로가 중지되었습니다.")

if __name__ == "__main__":
    print("좌표를 새로 저장하려면 'r' 키를, 매크로를 실행하려면 다른 아무 키나 누르세요...")
    
    if keyboard.read_event(suppress=True).name == 'r':
        save_coordinates()
        print("\n좌표 저장이 완료되었습니다. 매크로를 실행하려면 프로그램을 다시 실행해주세요.")
    else:
        print("매크로를 시작하려면 's' 키를 누르세요...")
        keyboard.wait('s')
        run_macro()