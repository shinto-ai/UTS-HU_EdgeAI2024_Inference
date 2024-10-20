import os
import time
from picamera import PiCamera
from grove.button import Button

# Grove - Buttonが接続されているデジタルポート番号
BUTTON_PORT = 2  # D2ポートに接続されていると仮定

# 保存先のベースディレクトリ
BASE_DIR = "captured_image"

# 有効なラベルのリスト
VALID_LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ["del", "space", "nothing"]

def capture_image(camera):
    """カメラで画像を撮影し、PILイメージオブジェクトとして返す"""
    camera.capture('temp.jpg')
    return 'temp.jpg'

def save_image(image_path, label):
    """指定されたラベルのフォルダに画像を保存する"""
    label_dir = os.path.join(BASE_DIR, label)
    os.makedirs(label_dir, exist_ok=True)
    
    # 既存の画像の数を数える
    existing_images = len([f for f in os.listdir(label_dir) if f.endswith('.jpg')])
    
    # 新しい画像名を生成
    new_image_name = f"{label}_{existing_images + 1}.jpg"
    new_image_path = os.path.join(label_dir, new_image_name)
    
    # 画像を新しい場所に移動
    os.rename(image_path, new_image_path)
    print(f"Saved image as {new_image_path}")

def main():
    # ユーザーにラベルの入力を求める
    while True:
        label = input("Enter the label for the images (A-Z, del, space, nothing): ").lower()
        if label in [l.lower() for l in VALID_LABELS]:
            break
        else:
            print("Invalid label. Please try again.")
    
    label = label.upper()  # ラベルを大文字に統一
    
    # Grove Buttonのセットアップ
    button = Button(BUTTON_PORT)

    # カメラの初期化
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        time.sleep(2)  # カメラのウォームアップ時間

        print(f"Ready to capture images for label '{label}'. Press the Grove button to capture. Press Ctrl+C to exit.")
        try:
            while True:
                if button.is_pressed():
                    print("Button pressed, capturing image...")
                    image_path = capture_image(camera)
                    save_image(image_path, label)
                    time.sleep(0.5)  # デバウンス用のディレイ
        except KeyboardInterrupt:
            print("Stopping the program...")

if __name__ == "__main__":
    main()