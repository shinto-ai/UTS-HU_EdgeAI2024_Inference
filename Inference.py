import os
import time
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import io
from picamera import PiCamera
from grove.button import Button
import grove.grove_led as grove_led

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

def capture_image(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    return Image.open(stream)

def main():
    print("Using CPU for inference")

    # Grove Buttonのセットアップ
    button = Button(BUTTON_PORT)

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
    with PiCamera() as camera:
        camera.resolution = (640, 480)
        camera.framerate = 30
        time.sleep(2)  # カメラのウォームアップ時間

        print("Ready to capture. Press the Grove button to capture and predict. Press Ctrl+C to exit.")
        try:
            while True:
                if button.is_pressed():
                    print("Button pressed, capturing image...")
                    image = capture_image(camera)
                    predicted_label = predict_letter(image, model, class_to_idx, transform)
                    print(f"Predicted letter: {predicted_label}")
                    time.sleep(0.5)  # デバウンス用のディレイ
        except KeyboardInterrupt:
            print("Stopping the program...")

if __name__ == "__main__":
    main()