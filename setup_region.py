import pyautogui
from screeninfo import get_monitors

def list_monitors():
    monitors = get_monitors()
    print("🖥 연결된 모니터:")
    for i, m in enumerate(monitors):
        print(f"{i}: {m.width}x{m.height} at ({m.x}, {m.y})")
    return monitors

def get_region_from_monitor(monitor):
    # 상태 아이콘 영역 (오른쪽 하단)
    icon_region = (
        monitor.x + monitor.width - 160,
        monitor.y + monitor.height - 200,
        140, 140
    )
    # 프로그레스 바 영역 (중앙 하단)
    bar_region = (
        monitor.x + monitor.width - 500,
        monitor.y + monitor.height // 2 + 100,
        149, 33
    )

    return {
        "state_icon": icon_region,
        "progress_bar": bar_region
    }

def save_region_txt(regions, filename="region.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for key, (x, y, w, h) in regions.items():
            f.write(f"{key}:{x},{y},{w},{h}\n")

if __name__ == "__main__":
    monitors = list_monitors()
    try:
        choice = int(input("➡ 사용할 모니터 번호 입력: "))
        selected = monitors[choice]
    except (ValueError, IndexError):
        print("❌ 잘못된 입력! 기본 모니터(0)로 설정합니다.")
        selected = monitors[0]

    regions = get_region_from_monitor(selected)
    save_region_txt(regions)
    print(f"\n✅ {choice}번 모니터 기준으로 region.txt 저장 완료!")