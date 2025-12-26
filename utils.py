import math
import json
import asyncio
import config
import sys

# 1. 환경 감지 (pygbag 실행 시 무조건 emscripten으로 잡힘)
IS_WEB = (sys.platform == "emscripten")

# 🚩 [필살기] 브라우저 F12 콘솔에 무조건 로그 찍는 함수
def log_to_browser(msg, data=None):
    message = f"🚀 [Vampire-Debug] {msg}"
    if data:
        message += f" | DATA: {data}"
    
    if IS_WEB:
        try:
            import js
            # 브라우저 F12 콘솔에 직접 출력
            js.window.console.log(message)
        except:
            print(message)
    else:
        print(message)

# 랭킹 항목 정의
RANK_CATEGORIES = ["Levels", "Kills", "Bosses", "DifficultyScore", "SurvivalTime"]

# ----------------------------------------------------
# 2. Supabase 통신 함수 (pyfetch 사용)
# ----------------------------------------------------
async def _fetch_supabase(endpoint, method, data=None):
    url = f"{config.SUPABASE_URL}/rest/v1/{endpoint}"
    log_to_browser(f"통신 시도 ({method})", url)

    if IS_WEB:
        try:
            from pyodide.http import pyfetch
            headers = {
                "apikey": config.SUPABASE_KEY,
                "Authorization": f"Bearer {config.SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # 멈춤 방지용 양보
            await asyncio.sleep(0.01)
            
            response = await pyfetch(
                url=url,
                method=method,
                headers=headers,
                body=json.dumps(data) if data else None
            )
            
            if response.status in [200, 201]:
                res_text = await response.string()
                log_to_browser("✅ 통신 성공!")
                return res_text
            else:
                log_to_browser(f"❌ API 에러 코드: {response.status}")
                return None
        except Exception as e:
            log_to_browser(f"🔥 치명적 오류 발생", str(e))
            return None
    else:
        # 로컬(VSC) 환경용 (urllib)
        import urllib.request
        try:
            headers = {
                "apikey": config.SUPABASE_KEY,
                "Authorization": f"Bearer {config.SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            req_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as res:
                return res.read().decode('utf-8')
        except Exception as e:
            print(f"LOCAL DB ERROR: {e}")
            return None

# ----------------------------------------------------
# 3. 랭킹 로드/저장 로직
# ----------------------------------------------------
async def load_rankings_online():
    log_to_browser("랭킹 로드 시퀀스 시작")
    # 컬럼명 에러 방지를 위해 정렬 없이 가져오기 시도
    data_str = await _fetch_supabase("rankings?select=*", 'GET')
    
    formatted_list = []
    if data_str:
        try:
            raw_list = json.loads(data_str)
            log_to_browser(f"데이터 수신 완료: {len(raw_list)}개")
            for row in raw_list:
                for cat in RANK_CATEGORIES:
                    # DB 컬럼명 매칭 (소문자 기준)
                    db_col = cat.lower().replace("score", "_score").replace("time", "_time")
                    formatted_list.append({
                        "ID": row.get("name", "익명"),
                        "RankCategory": cat,
                        "RankValue": float(row.get(db_col, 0)),
                        "Levels": row.get("levels", 0),
                        "Kills": row.get("kills", 0)
                    })
        except Exception as e:
            log_to_browser("JSON 파싱 에러", str(e))
    return formatted_list

async def save_new_ranking_online(name, score_data):
    log_to_browser(f"점수 저장 시작: {name}")
    new_row = {
        "name": str(name),
        "levels": int(score_data.get('levels', 0)),
        "kills": int(score_data.get('kills', 0)),
        "bosses": int(score_data.get('bosses', 0)),
        "difficulty_score": float(score_data.get('difficulty_score', 0.0)),
        "survival_time": float(score_data.get('survival_time', 0.0))
    }
    await _fetch_supabase("rankings", 'POST', data=new_row)
    return True

# ----------------------------------------------------
# 4. 필수 수학 유틸 (삭제 금지)
# ----------------------------------------------------
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