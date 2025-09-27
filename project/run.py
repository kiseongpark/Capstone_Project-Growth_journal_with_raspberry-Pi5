# run.py
import os
import cv2
from collections import Counter
from itertools import islice
from ultralytics import YOLO
import google.generativeai as genai

# --- Picamera2 ---
from picamera2 import Picamera2
from libcamera import Transform  # 회전/미러가 필요할 때 사용(옵션)

# --- TTS/요약 유틸 ---
from tts_utils import extract_summary, speak_ko

# --- Pushbullet 유틸 (오타 대비: 두 이름 모두 시도) ---
try:
    from pushbullet_utils import send_push_note, send_push_file, PushbulletError
except ImportError:
    from pyshbullet_utils import send_push_note, send_push_file, PushbulletError  # fallback

# ===== 설정 =====
SHOW_WINDOW = True        # SSH/헤드리스면 False 권장
TARGET_LABEL_COUNT = 10   # 수집할 라벨 개수
SAVE_FIRST_FRAME_PATH = "saved_frame.jpg"
SAVE_FIRST_ANN_PATH = "saved_frame_annotated.jpg"
MODEL_PATH = "best1.pt"   # YOLO 가중치 경로

# ===== Google Generative AI (Gemini) =====
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("환경변수 GOOGLE_API_KEY 가 설정되지 않았습니다.")
genai.configure(api_key=API_KEY)

# 사용 모델 (프로젝트 권한에 맞는 모델명으로 교체 가능)
GEMINI_MODEL_NAME = "gemini-2.0-flash"
gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)

def main():
    # ===== YOLO 로드 =====
    yolo_model = YOLO(MODEL_PATH)

    # ===== Picamera2 설정 =====
    picam = Picamera2()
    config = picam.create_preview_configuration(
        main={"size": (1280, 720), "format": "RGB888"},
        transform=Transform()  # 예: Transform(hflip=1, vflip=0, rotation=0)
    )
    picam.configure(config)
    picam.start()

    labels = []
    saved_frame_written = False

    print("라벨 수집을 시작합니다. ESC 를 누르면 중단합니다.")
    try:
        while len(labels) < TARGET_LABEL_COUNT:
            frame = picam.capture_array()
            results = yolo_model(frame, verbose=False)

            if results and len(results) > 0 and getattr(results[0], "boxes", None) is not None:
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    label = yolo_model.names.get(cls, str(cls))
                    labels.append(label)

            if not saved_frame_written:
                try:
                    cv2.imwrite(SAVE_FIRST_FRAME_PATH, frame)
                    if results and len(results) > 0:
                        annotated0 = results[0].plot()
                        cv2.imwrite(SAVE_FIRST_ANN_PATH, annotated0)
                    print(f"프레임 저장 완료: {SAVE_FIRST_FRAME_PATH}, {SAVE_FIRST_ANN_PATH}")
                except Exception as e:
                    print(f"[저장 경고] 첫 프레임 저장 실패: {e}")
                saved_frame_written = True

            if SHOW_WINDOW and results and len(results) > 0:
                annotated = results[0].plot()
                cv2.imshow("YOLO + Picamera2", annotated)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            if labels:
                print(f"Detected Labels (count={len(labels)}): {labels[-5:]} ...")

    except KeyboardInterrupt:
        print("\n[중단] 사용자 인터럽트")
    finally:
        picam.stop()
        if SHOW_WINDOW:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    # ===== 라벨 정리 및 성장일지 =====
    if labels:
        counts = Counter(labels)
        top_labels = [k for k, _ in islice(counts.most_common(5), 5)]
    else:
        top_labels = []

    print("\n--- 성장일지 작성 시작 ---")
    if top_labels:
        levels_str = ", ".join(top_labels)
        prompt = (
            f"YOLO로 방울토마토의 성장 단계를 {levels_str}와 같이 감지했어. "
            f"이 결과를 바탕으로 방울토마토의 현재 성장 상태를 통합하여 3줄짜리 성장일지를 작성해줘. "
            f"레벨별로 구분하지 말고, 전체적인 성장 상태만 설명해줘. "
            f"작성 결과는 독거노인에게 전송될 예정이니 귀여운 손자 컨셉으로 가줘. "
            f"칭찬과 격려의 말을 꼭 포함해줘."
            f"위 성장일지 한줄로 요약해줘. 특수 문자 제거해주고 이모티콘은 빼줘 "
        )
        try:
            response = gemini_model.generate_content(prompt)
            text = getattr(response, "text", "") or ""
            print("\n[방울토마토 종합 성장일지]")
            print(text)

            summary_line = extract_summary(text)
            if summary_line:
                print("\n[TTS]")
                print(summary_line)
                speak_ko(summary_line)
            else:
                print("\n[요약 추출 실패] 응답 형식을 확인하세요.")

            # === Pushbullet 전송 ===
            try:
                send_push_note(
                    title="[방울토마토 종합 성장일지]",
                    body=text,
                )
                send_push_file(
                    title="[방울토마토 첫 프레임]",
                    body="금일 저장된 프레임을 첨부합니다.",
                    filepath=SAVE_FIRST_FRAME_PATH,
                )
            except PushbulletError as pe:
                print(f"[Pushbullet 오류] {pe}")

        except Exception as e:
            print(f"\n[오류] 성장일지 생성 중 문제가 발생했습니다: {e}")
    else:
        print("감지된 라벨이 없어 성장일지를 작성할 수 없습니다.")

    print("\n--- 성장일지 작성 완료 ---")

if __name__ == "__main__":
    main()
