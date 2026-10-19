
from pathlib import Path
import re

from recommendation_profiles import (
    CPU_LEVEL_ORDER,
    GPU_MODEL_TIERS,
    GPU_TIER_ORDER,
    RECOMMENDATION_PROFILES,
)

def normalized(value):
    '''모델명과 레벨을 비교할 수 있도록 공백과 대소문자를 통일'''
    if value is None:
        return ''

    return re.sub(r'\s+', ' ', str(value)).strip().upper()

# 등급별 모델 목록을 모델명으로 등급을 찾을 수 있는 딕셔너리로 변환
GPU_MODEL_TO_TIER = {
    normalized(model): tier
    for tier, models in GPU_MODEL_TIERS.items()
    for model in models
}

def number(value):
    '''값을 양의 유한한 숫자로 변환하고, 잘못된 값이면 None을 반환'''
    if isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None