import utils
import config
from core.grid import enemy_grid # 그리드 엔진 필수

def handle_collisions(state):
    """모든 엔티티 간의 충돌 및 업데이트를 처리합니다."""
    entities = state.get_entities_dict()
    
    # --- 1. 단검 vs 적 (그리드 최적화) ---
    d_hit = set()
    for d in state.daggers:
        # 단검 주변 적들만 탐색
        nearby = enemy_grid.get_nearby_enemies(d.world_x, d.world_y, 1)
        for s in nearby:
            if s.hp > 0:
                dist_sq = utils.distance_sq_wrapped(d.world_x, d.world_y, s.world_x, s.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
                if dist_sq < (d.size/2 + s.radius)**2:
                    s.take_damage(d.damage)
                    d_hit.add(d)
                    break
    state.daggers[:] = [d for d in state.daggers if d not in d_hit]

    # --- 2. 폭풍 발사체 업데이트 ---
    state.storm_projectiles[:] = [p for p in state.storm_projectiles if p.update(state.slimes + state.boss_slimes)]

    # --- 3. 적 발사체 vs 플레이어 ---
    sb_keep = []
    for sb in state.slime_bullets:
        if sb.update():
            dist_sq = utils.distance_sq_wrapped(state.player.world_x, state.player.world_y, sb.world_x, sb.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
            if dist_sq < (config.PLAYER_SIZE/2 + sb.size/2)**2:
                state.player.take_damage(config.SLIME_BULLET_DAMAGE)
            else:
                sb_keep.append(sb)
    state.slime_bullets[:] = sb_keep

    # --- 4. 적 접촉 데미지 (그리드 최적화) ---
    nearby_for_p = enemy_grid.get_nearby_enemies(state.player.world_x, state.player.world_y, 1)
    for s in nearby_for_p:
        if s.hp > 0:
            dist_sq = utils.distance_sq_wrapped(state.player.world_x, state.player.world_y, s.world_x, s.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
            if dist_sq < ((config.PLAYER_SIZE/2)*config.PLAYER_DAMAGE_HITBOX_MULTIPLIER + s.radius)**2:
                state.player.take_damage(s.damage_to_player)

    # --- 5. 🚩 경험치 획득 로직 (완전 복구!) ---
    o_rem = []
    for o in state.exp_orbs:
        # 구슬이 플레이어에게 빨려오거나(update), 직접 닿았을 때
        is_collected = o.update(state.player.world_x, state.player.world_y)
        dist_sq_orb = utils.distance_sq_wrapped(o.world_x, o.world_y, state.player.world_x, state.player.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
        
        if is_collected or dist_sq_orb < (config.EXP_ORB_RADIUS + config.PLAYER_SIZE/2)**2:
            state.player.gain_exp(o.value) # 플레이어 경험치 증가
            o_rem.append(o)
    # 획득한 구슬 리스트에서 제거
    state.exp_orbs[:] = [o for o in state.exp_orbs if o not in o_rem]
    
    # --- 6. 🚩 박쥐 업데이트 (필살기: 리턴값에 따라 리스트 즉시 갱신) ---
    # b.update가 False를 리턴(1초 멈춤 자폭)하는 순간, 명단에서 가차없이 삭제됨!
    state.bats[:] = [b for b in state.bats if b.update(enemy_grid.get_nearby_enemies(b.world_x, b.world_y, 2), entities)]