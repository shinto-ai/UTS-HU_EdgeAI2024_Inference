import os
import time
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import cv2
import numpy as np
import grovepi

# Grove - Buttonが接続されているデジタルポート番号
BUTTON_PORT = 2  # D2ポートに接続されていると仮定

def load_model(model_path, num_classes):
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    
    checkpoint = torch.load(model_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    class_to_idx = checkpoint['class_to_idx']
    
    return model, class_to_idx

def predict_letter(image, model, class_to_idx, transform):
    model.eval()
    image = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        output = model(image)
        _, predicted = output.max(1)
    
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    return idx_to_class[predicted.item()]

def main():
    print("Using CPU for inference")

    # ボタンのセットアップ
    grovepi.pinMode(BUTTON_PORT, "INPUT")
    time.sleep(1)  # セットアップ後の待機時間

    # モデルのロード
    model_path = "best_asl_alphabet_model.pth"
    model, class_to_idx = load_model(model_path, num_classes=29)

    # データの前処理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # カメラの初期化
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("Ready to capture. Press the Grove button to capture and predict. Press 'q' to exit.")

    try:
        while True:
            # カメラからフレームを取得
            ret, frame = cap.read()
            if not ret:
                print("Failed to get frame from camera")
                break

            # フレームを正方形にクロップ
            height, width = frame.shape[:2]
            min_dim = min(height, width)
            start_x = (width - min_dim) // 2
            start_y = (height - min_dim) // 2
            square_frame = frame[start_y:start_y + min_dim, start_x:start_x + min_dim]

            # プレビューに表示するためにコピーを作成
            preview_frame = square_frame.copy()

            # ボタンの状態をチェック
            button_status = grovepi.digitalRead(BUTTON_PORT)
            if button_status == 1:
                # 画像をPIL形式に変換
                image = cv2.cvtColor(square_frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

                # 予測を実行
                predicted_label = predict_letter(image, model, class_to_idx, transform)
                print(f"Predicted letter: {predicted_label}")

                # 予測結果をプレビューに表示
                cv2.putText(preview_frame, f"Prediction: {predicted_label}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                time.sleep(0.5)  # デバウンス用のディレイ

            # プレビューを表示
            cv2.imshow('ASL Recognition', preview_frame)

            # 'q'キーが押された場合、プログラムを終了
            key = cv2.waitKey(1)
            if key == ord('q'):
                print("Exiting the program...")
                break

    except KeyboardInterrupt:
        print("Program interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
