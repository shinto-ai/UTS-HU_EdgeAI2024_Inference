import os
import time
import cv2
import grovepi

# Grove - Buttonが接続されているデジタルポート番号
BUTTON_PORT = 2  # D2ポートに接続されていると仮定

# 保存先のベースディレクトリ
BASE_DIR = "captured_image"

# 有効なラベルのリスト
VALID_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["del", "space", "nothing"]

def save_image(image, label):
    """指定されたラベルのフォルダに画像を保存する"""
    label_dir = os.path.join(BASE_DIR, label)
    os.makedirs(label_dir, exist_ok=True)
    
    # 既存の画像の数を数える
    existing_images = len([f for f in os.listdir(label_dir) if f.endswith('.jpg')])
    
    # 新しい画像名を生成
    new_image_name = f"{label}_{existing_images + 1}.jpg"
    new_image_path = os.path.join(label_dir, new_image_name)
    
    # 画像を保存
    cv2.imwrite(new_image_path, image)
    print(f"画像を保存しました: {new_image_path}")

def main():
    # ユーザーにラベルの入力を求める
    while True:
        label = input("画像のラベルを入力してください (A-Z, del, space, nothing): ").lower()
        if label in [l.lower() for l in VALID_LABELS]:
            break
        else:
            print("無効なラベルです。もう一度入力してください。")
    
    label = label.upper()  # ラベルを大文字に統一

    # ボタンのセットアップ
    grovepi.pinMode(BUTTON_PORT, "INPUT")
    time.sleep(1)  # セットアップ後の待機時間

    # カメラの初期化
    cap = cv2.VideoCapture(0)  # カメラデバイスIDが0でない場合は変更してください
    if not cap.isOpened():
        print("カメラを開けませんでした")
        exit()

    # カメラの解像度を設定
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"ラベル '{label}' の画像をキャプチャする準備ができました。画像を撮影するにはGroveボタンを押してください。終了するには 'q' を押してください。")
    try:
        while True:
            # カメラからフレームを取得
            ret, frame = cap.read()
            if not ret:
                print("フレームの取得に失敗しました")
                break

            # フレームを正方形にクロップ
            height, width = frame.shape[:2]
            min_dim = min(height, width)
            start_x = (width - min_dim) // 2
            start_y = (height - min_dim) // 2
            square_frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]

            # フレームを表示
            cv2.imshow('Camera Preview', square_frame)

            # 'q'キーが押された場合、プログラムを終了
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("プログラムを終了します...")
                break

            # ボタンの状態をチェック
            button_status = grovepi.digitalRead(BUTTON_PORT)
            if button_status == 1:
                print("ボタンが押されました。画像を保存します...")
                save_image(square_frame, label)
                time.sleep(0.3)  # デバウンス用のディレイ

    except KeyboardInterrupt:
        print("プログラムを中断しました")
    finally:
        # リソースの解放
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
