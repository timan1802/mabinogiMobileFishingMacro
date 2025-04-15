import cv2
import numpy as np
import os
from mss import mss
from PIL import Image

# 탐지에 사용할 이미지 템플릿 경로 정의
# key: region.txt에 저장될 이름, value: 매칭 기준 이미지 경로
TEMPLATE_PATHS = {
    "state_icon": "img/done_clean_center.png",   # 낚시 완료 상태를 나타내는 아이콘
    "start_icon": "img/start.png",               # 낚시 시작 아이콘
    "fishing_icon": "img/fishing.png",           # 낚시 중 아이콘
    "progress_bar": "img/bar.png"                # 진행 바 이미지
}

# 이미지 파일을 불러오는 함수
def load_image(path):
    if not os.path.exists(path):
        print(f"[경고] 이미지 없음: {path}")
        return None
    return cv2.imread(path)

# 모든 모니터에서 특정 템플릿 이미지가 화면에 있는지 찾는 함수
# → 이미지가 발견되면 그 위치의 좌표 (left, top, width, height)를 반환
def find_template_on_all_monitors(template, label):
    with mss() as sct:
        # sct.monitors[1:] → [1]번부터 모든 모니터 (듀얼 모니터 포함)
        for monitor in sct.monitors[1:]:
            sct_img = sct.grab(monitor)  # 현재 모니터 영역 캡처
            screen = np.array(sct_img)
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)  # BGRA → BGR 변환

            # 템플릿 매칭 수행
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            # 일정 임계값 이상일 경우 일치로 판단
            if max_val > 0.8:
                x, y = max_loc
                w, h = template.shape[1], template.shape[0]
                region = (monitor["left"] + x, monitor["top"] + y, w, h)
                print(f"[성공] {label} → 좌표: {region} (유사도: {max_val:.2f})")
                return region

    print(f"[실패] {label} 이미지를 찾지 못함")
    return None

# 전체 좌표 자동 설정 및 region.txt 저장 함수
def auto_setup_regions():
    region_map = {}

    # 각 템플릿 이미지에 대해 화면에서 탐색 수행
    for label, path in TEMPLATE_PATHS.items():
        template = load_image(path)
        if template is not None:
            region = find_template_on_all_monitors(template, label)
            if region:
                region_map[label] = region

    # 유효한 좌표가 존재할 경우 region.txt 파일로 저장
    if region_map:
        with open("region.txt", "w", encoding="utf-8") as f:
            for key, val in region_map.items():
                f.write(f"{key}={','.join(map(str, val))}\n")
        print("[완료] region.txt 저장 완료")
    else:
        print("[오류] 저장할 좌표가 없습니다.")

# 메인 실행 지점
if __name__ == "__main__":
    auto_setup_regions()
