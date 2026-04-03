from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os
import io
from PIL import Image
import torch
from torchvision import models, transforms
from app.core.config import FOOD_CALORIES, IMAGENET_TO_FOOD
import random

app = FastAPI(
    title="Food Calorie Classifier API",
    description="음식 이미지를 업로드하면 PyTorch MobileNetV2 모델을 사용하여 음식의 종류와 칼로리를 예측해주는 API입니다.",
    version="1.0.0"
)

# 모델 초기화 (전역 변수로 띄워 서버 웜업 유지)
weights = models.MobileNet_V2_Weights.DEFAULT
model = models.mobilenet_v2(weights=weights)
model.eval()
categories = weights.meta["categories"]

# 전처리 로직 설정
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def map_imagenet_class(imagenet_label: str) -> str:
    """ImageNet 영단어를 한글 메뉴로 치환합니다."""
    label_lower = imagenet_label.lower()
    for key_word, food_name in IMAGENET_TO_FOOD.items():
        if key_word in label_lower:
            return food_name
    return f"기타 음식({imagenet_label})"

@app.get("/", response_class=HTMLResponse)
def read_root():
    # 예쁜 웹 UI (인덱스 파일)를 반환합니다.
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()
@app.get("/foods")
def get_supported_foods():
    """현재 분류 가능한 음식 모델의 리스트와 칼로리 목록을 반환합니다."""
    return {"supported_foods": FOOD_CALORIES}

@app.post("/predict")
async def predict_food(image: UploadFile = File(...)):
    """
    업로드된 사진을 PyTorch MobileNet 모델에 넣고 추론한 뒤 결과를 반환합니다.
    """
    try:
        content = await image.read()
        pil_image = Image.open(io.BytesIO(content)).convert("RGB")
        
        # 1. 텐서 전처리
        input_tensor = preprocess(pil_image)
        input_batch = input_tensor.unsqueeze(0)  # 배치 차원 추가

        # 2. 모델 추론
        with torch.no_grad():
            output = model(input_batch)
        
        # 3. Softmax 확률 적용 및 1등(Top-1) 가져오기
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        top1_prob, top1_catid = torch.topk(probabilities, 1)
        
        imagenet_class = categories[top1_catid[0].item()]
        
        # 4. 결과 매핑
        predicted_food = map_imagenet_class(imagenet_class)
        # 딕셔너리에 있으면 칼로리를 가져오고, 없으면 0이나 임의값 설정
        calories = FOOD_CALORIES.get(predicted_food, 450) # 못 찾으면 임의로 450kcal
        
        return {
            "filename": image.filename,
            "classification": predicted_food,
            "calories": calories,
            "message": f"{predicted_food}({calories}kcal) 예측 성공"
        }
    except Exception as e:
        return {
            "error": str(e)
        }
