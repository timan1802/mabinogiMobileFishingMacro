import cv2
import numpy as np
from mss import mss
import os

def find_template_multiscale(template_path, threshold=0.8, scales=None):
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"템플릿 이미지가 존재하지 않습니다: {template_path}")

    original_template = cv2.imread(template_path)
    if original_template is None:
        raise ValueError(f"이미지를 불러오지 못했습니다: {template_path}")

    if scales is None:
        scales = np.linspace(0.6, 1.4, 16)

    with mss() as sct:
        for idx, monitor in enumerate(sct.monitors[1:]):  # 실제 모니터들만 검사
            print(f"[INFO] 모니터 {idx + 1} 검사 중: {monitor}")
            screenshot = np.array(sct.grab(monitor))
            screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            for scale in scales:
                resized_template = cv2.resize(original_template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                th, tw = resized_template.shape[:2]

                if screenshot_bgr.shape[0] < th or screenshot_bgr.shape[1] < tw:
                    continue

                result = cv2.matchTemplate(screenshot_bgr, resized_template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)

                if max_val >= threshold:
                    print(f"[✓] 매칭됨! 스케일: {scale:.2f}, 유사도: {max_val:.3f}")
                    abs_left = monitor["left"] + max_loc[0]
                    abs_top = monitor["top"] + max_loc[1]

                    # ✅ 매칭된 부분만 잘라서 표시
                    matched_crop = screenshot_bgr[max_loc[1]:max_loc[1]+th, max_loc[0]:max_loc[0]+tw]
                    cv2.imshow(f"Matched: {os.path.basename(template_path)}", matched_crop)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                    return abs_left, abs_top, tw, th

            print(f"[X] 모니터 {idx + 1}에서 미발견")

    print(f"[!] 모든 모니터에서 이미지 미발견: {template_path}")
    return None


def save_region(region_key, region_value):
    path = "region.txt"
    regions = {}

    # 기존 region.txt 로드
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=")
                    regions[key] = val

    # 새 region 저장 또는 덮어쓰기
    regions[region_key] = ",".join(map(str, region_value))

    with open(path, "w", encoding="utf-8") as f:
        for k, v in regions.items():
            f.write(f"{k}={v}\n")


def batch_register_images(img_info_dict):
    for key, path in img_info_dict.items():
        print(f"\n[🔍] '{key}' 이미지 찾는 중... ({path})")
        result = find_template_multiscale(path)
        if result:
            save_region(key, result)
            print(f"[✔] region.txt에 저장됨 → {key}: {result}")
        else:
            print(f"[⚠] '{key}' 이미지 찾지 못함")

if __name__ == "__main__":
    # 등록할 이미지와 키 목록
    image_list = {
        "start": "img/start.png",
        "done": "img/done.png",
        "fishing": "img/fishing.png"
        # 필요한 경우 여기에 더 추가 가능
    }

    batch_register_images(image_list)
