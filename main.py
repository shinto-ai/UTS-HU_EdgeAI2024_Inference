import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

def load_model(model_path, num_classes):
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, num_classes)
    
    checkpoint = torch.load(model_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    class_to_idx = checkpoint['class_to_idx']
    
    return model, class_to_idx

def predict_letter(image_path, model, class_to_idx, transform):
    model.eval()
    image = Image.open(image_path).convert("RGB")
    image = transform(image).unsqueeze(0)
    
    with torch.no_grad():
        output = model(image)
        _, predicted = output.max(1)
    
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    return idx_to_class[predicted.item()]

def main():
    print("Using CPU for inference")

    # モデルのロード
    model_path = "best_asl_alphabet_model.pth"
    model, class_to_idx = load_model(model_path, num_classes=29)  # 29 classes including 'del', 'nothing', and 'space'

    # データの前処理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # /captured_image フォルダから画像を読み込む
    image_folder = "captured_image"
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print("No image found in captured_image folder.")
        return

    # 最初の画像を使用
    image_path = os.path.join(image_folder, image_files[0])

    # 推論の実行
    predicted_label = predict_letter(image_path, model, class_to_idx, transform)

    print(f"Predicted label for the image: {predicted_label}")

if __name__ == "__main__":
    main()