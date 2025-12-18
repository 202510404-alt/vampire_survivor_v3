# utils.py
import math
import json
import config # MAP_WIDTH, MAP_HEIGHT를 가져오기 위해


RANKING_FILE = "rankings.json"
def load_rankings():
    """랭킹 파일을 읽어와서 리스트 형태로 반환합니다."""
    try:
        with open(RANKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
        # 💡 [참고] 웹 환경(pygbag)에서 파일 로드는 더 복잡할 수 있습니다. 
        # 일단 로컬 환경을 위해 이렇게 진행하고, 웹 환경에서 오류가 나면 나중에 수정합니다.
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_new_ranking(name, score_data):
    """새로운 기록을 랭킹 리스트에 추가하고 파일을 업데이트합니다."""
    rankings = load_rankings()
    
    # score_data는 딕셔너리 형태로 받습니다: {'level': 10, 'kills': 500, 'bosses': 5, 'time': 120.5}
    new_record = {
        "name": name,
        "level": score_data.get('level', 0),
        "kills": score_data.get('kills', 0),
        "bosses": score_data.get('bosses', 0),
        "survival_time": score_data.get('time', 0.0),
        "timestamp": pygame.time.get_ticks() 
    }
    rankings.append(new_record)
    
    # 핵심 점수인 '생존 시간' 기준으로 내림차순 정렬 (높은 점수가 위로)
    rankings.sort(key=lambda x: x['survival_time'], reverse=True)
    
    # 상위 10개만 유지
    rankings = rankings[:10] 

    with open(RANKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(rankings, f, indent=4, ensure_ascii=False)

    return rankings

def get_wrapped_delta(val1, val2, map_dim):
    delta = val2 - val1
    if abs(delta) > map_dim / 2:
        if delta > 0: delta -= map_dim
        else: delta += map_dim
    return delta

def distance_sq_wrapped(x1, y1, x2, y2, map_w, map_h):
    dx = get_wrapped_delta(x1, x2, map_w)
    dy = get_wrapped_delta(y1, y2, map_h)
    return dx*dx + dy*dy