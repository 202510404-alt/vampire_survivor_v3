import utils
import config
from enemies.boss_minion_slime import BossMinionSlime
from entities.exp_orb import ExpOrb

def handle_collisions(state):
    """모든 엔티티 간의 충돌을 처리합니다."""
    entities = state.get_entities_dict()
    
    # 1. 단검 vs 적 (일반 슬라임 + 보스)
    d_hit = set()
    for d in state.daggers:
        for s in state.slimes + state.boss_slimes:
            if s.hp > 0 and utils.distance_sq_wrapped(d.world_x, d.world_y, s.world_x, s.world_y, config.MAP_WIDTH, config.MAP_HEIGHT) < (d.size/2 + s.radius)**2:
                s.take_damage(d.damage)
                d_hit.add(d)
                break
    state.daggers[:] = [d for d in state.daggers if d not in d_hit]

    # 2. 폭풍 발사체 업데이트 및 충돌
    state.storm_projectiles[:] = [p for p in state.storm_projectiles if p.update(state.slimes + state.boss_slimes)]

    # 3. 적 발사체 vs 플레이어
    sb_keep = []
    for sb in state.slime_bullets:
        if sb.update():
            dist_sq = utils.distance_sq_wrapped(state.player.world_x, state.player.world_y, sb.world_x, sb.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
            if dist_sq < (config.PLAYER_SIZE/2 + sb.size/2)**2:
                state.player.take_damage(config.SLIME_BULLET_DAMAGE)
            else:
                sb_keep.append(sb)
    state.slime_bullets[:] = sb_keep

    # 4. 적 접촉 데미지 (플레이어)
    for s in state.slimes + state.boss_slimes:
        if s.hp > 0:
            dist_sq = utils.distance_sq_wrapped(state.player.world_x, state.player.world_y, s.world_x, s.world_y, config.MAP_WIDTH, config.MAP_HEIGHT)
            if dist_sq < ((config.PLAYER_SIZE/2)*config.PLAYER_DAMAGE_HITBOX_MULTIPLIER + s.radius)**2:
                state.player.take_damage(s.damage_to_player)

    # 5. 경험치 획득 로직
    o_rem = []
    for o in state.exp_orbs:
        # update가 True를 반환하거나 플레이어와 닿으면 획득
        if o.update(state.player.world_x, state.player.world_y) or \
           utils.distance_sq_wrapped(o.world_x, o.world_y, state.player.world_x, state.player.world_y, config.MAP_WIDTH, config.MAP_HEIGHT) < (config.EXP_ORB_RADIUS + config.PLAYER_SIZE/2)**2:
            state.player.gain_exp(o.value)
            o_rem.append(o)
    state.exp_orbs[:] = [o for o in state.exp_orbs if o not in o_rem]
    
    # 6. 박쥐 업데이트
    state.bats[:] = [b for b in state.bats if b.update(state.slimes, entities)]