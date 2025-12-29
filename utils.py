import math
import json
import asyncio
import sys
import config

# 1. 환경 감지
IS_WEB = (sys.platform == "emscripten")

js = None
if IS_WEB:
    try:
        import js
        from pyodide.ffi import to_js
    except ImportError:
        pass

def browser_debug(msg, is_error=False):
    full_msg = f"🚀 [Vampire-Fix] {msg}"
    if IS_WEB and js:
        try:
            if is_error: js.window.console.log(full_msg) if not is_error else js.window.console.error(full_msg)
        except: pass
    print(full_msg)

RANK_CATEGORIES = ["Levels", "Kills", "Bosses", "DifficultyScore", "SurvivalTime"]

# ----------------------------------------------------
# 2. Supabase 통신 (프록시 필살기 적용)
# ----------------------------------------------------
async def _fetch_supabase(endpoint, method, data=None):
    # 🚩 [핵심] 원래 주소 앞에 프록시 서버 주소를 붙여서 CORS를 강제로 뚫어버림
    base_url = f"{config.SUPABASE_URL}/rest/v1/{endpoint}"
    url = f"https://corsproxy.io/?{base_url}"
    
    # 2025년형 신규 키(sb_publishable)는 apikey 헤더만 있어도 작동하는 경우가 많음
    headers = {
        "apikey": config.SUPABASE_KEY,
        "Authorization": f"Bearer {config.SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    if IS_WEB and js:
        try:
            from pyodide.ffi import to_js
            
            # JS용 옵션 설정
            options = {
                "method": method,
                "headers": headers,
                "mode": "cors"
            }
            if data:
                options["body"] = json.dumps(data)

            # Python dict -> JS Object 변환 (가장 안전한 방식)
            js_options = to_js(options, dict_converter=js.Object.fromEntries)
            
            browser_debug(f"연결 시도 중 (프록시): {endpoint}")
            
            # fetch 호출
            response = await js.window.fetch(url, js_options)
            
            if response.ok:
                res_text = await response.text()
                return res_text
            else:
                browser_debug(f"API 에러 발생: {response.status}", True)
                return None
        except Exception as e:
            browser_debug(f"네트워크 치명적 오류: {str(e)}", True)
            return None
    else:
        # 로컬 환경 (VSC)
        import urllib.request
        try:
            req_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(base_url, data=req_data, headers=headers, method=method)
            with urllib.request.urlopen(req) as res:
                return res.read().decode('utf-8')
        except Exception as e:
            print(f"LOCAL ERROR: {e}")
            return None

# ----------------------------------------------------
# 3. 데이터 로드/저장 (기존 로직 유지)
# ----------------------------------------------------
async def load_rankings_online():
    browser_debug("데이터 불러오기 시작...")
    data_str = await _fetch_supabase("rankings?select=*", 'GET')
    
    formatted_list = []
    if data_str:
        try:
            raw_list = json.loads(data_str)
            browser_debug(f"수신 성공: {len(raw_list)}명")
            for row in raw_list:
                for cat in RANK_CATEGORIES:
                    db_col = cat.lower().replace("score", "_score").replace("time", "_time")
                    formatted_list.append({
                        "ID": row.get("name", "익명"),
                        "RankCategory": cat,
                        "RankValue": float(row.get(db_col, 0)),
                        "Levels": row.get("levels", 0),
                        "Kills": row.get("kills", 0)
                    })
        except: pass
    return formatted_list

async def save_new_ranking_online(name, score_data):
    browser_debug(f"저장 시도: {name}")
    new_row = {
        "name": str(name),
        "levels": int(score_data.get('levels', 0)),
        "kills": int(score_data.get('kills', 0)),
        "bosses": int(score_data.get('bosses', 0)),
        "difficulty_score": float(score_data.get('difficulty_score', 0.0)),
        "survival_time": float(score_data.get('survival_time', 0.0))
    }
    res = await _fetch_supabase("rankings", 'POST', data=new_row)
    if res:
        browser_debug("저장 완료!")
        return True
    return False

# ----------------------------------------------------
# 4. 물리 유틸리티
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