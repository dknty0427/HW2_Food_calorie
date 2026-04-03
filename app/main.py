from fastapi import FastAPI, File, UploadFile
from app.core.config import FOOD_CALORIES
import random

app = FastAPI(
    title="Food Calorie Classifier API",
    description="음식 이미지를 업로드하면 해당 음식의 종류와 칼로리를 예측해주는 API입니다. (Mock 모델 사용 중)",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Food Calorie Classifier API 서버가 정상적으로 실행 중입니다."}

@app.get("/foods")
def get_supported_foods():
    """현재 분류 가능한 음식 모델의 리스트와 칼로리 목록을 반환합니다."""
    return {"supported_foods": FOOD_CALORIES}

@app.post("/predict")
async def predict_food(image: UploadFile = File(...)):
    """
    이미지를 업로드하면 MLOps 모델 파이프라인을 거쳐 음식 종류와 칼로리를 반환하는 엔드포인트입니다.
    현재는 Mockup 로직으로 구현되어 무작위로 음식을 선택합니다. (추후 실제 PyTorch/TensorFlow 모델 추론 코드로 교체)
    """
    # TODO: image 파일을 읽고 실제 딥러닝 모델의 입력으로 전처리하여 추론 결과를 도출하는 로직 작성
    # content = await image.read()
    # predicted_class = model.predict(content)
    
    # [Mockup 추론 로직]: 등록된 음식 중에서 랜덤으로 결과를 하나 반환합니다.
    predicted_food = random.choice(list(FOOD_CALORIES.keys()))
    calories = FOOD_CALORIES[predicted_food]
    
    return {
        "filename": image.filename,
        "classification": predicted_food,
        "calories": calories,
        "message": f"{predicted_food}({calories}kcal)"
    }
