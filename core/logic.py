import random
import config
import utils
from enemies.slime import Slime
from enemies.mint_slime import MintSlime
from enemies.shooter_slime import ShooterSlime
from enemies.boss_slime import BossSlime
from enemies.boss_minion_slime import BossMinionSlime
from entities.exp_orb import ExpOrb

def update_game_logic(state):
    """스폰 및 시간 흐름에 따른 난이도 상승을 처리합니다."""
    if state.boss_active:
        return # 보스전 중에는 일반 스폰 중단

    # 난이도 상승 타이머
    state.slime_hp_increase_timer += 1
    if state.slime_hp_increase_timer >= config.FPS * config.SLIME_HP_INCREASE_INTERVAL_SECONDS:
        state.slime_hp_increase_timer = 0
        state.current_slime_max_hp += 1

    # 일반 슬라임 스폰
    state.slime_spawn_timer += 1
    if state.slime_spawn_timer >= config.SLIME_SPAWN_INTERVAL:
        state.slime_spawn_timer = 0
        spawn_enemy(state)

def spawn_enemy(state):
    """카메라 외곽에 적을 생성합니다."""
    cam = state.camera_obj
    edge = random.randint(0, 3)
    cam_l, cam_t = cam.world_x, cam.world_y
    cam_r, cam_b = cam_l + config.SCREEN_WIDTH, cam_t + config.SCREEN_HEIGHT
    
    if edge == 0: sx, sy = random.uniform(cam_l-100, cam_r+100), cam_t-100
    elif edge == 1: sx, sy = random.uniform(cam_l-100, cam_r+100), cam_b+100
    elif edge == 2: sx, sy = cam_l-100, random.uniform(cam_t-100, cam_b+100)
    else: sx, sy = cam_r+100, random.uniform(cam_t-100, cam_b+100)
    
    spawn_roll = random.randint(0, 9)
    if spawn_roll < 2:
        state.slimes.append(ShooterSlime(sx % config.MAP_WIDTH, sy % config.MAP_HEIGHT, state.current_slime_max_hp))
    elif spawn_roll < 4:
        state.slimes.append(MintSlime(sx % config.MAP_WIDTH, sy % config.MAP_HEIGHT, state.current_slime_max_hp))
    else:
        state.slimes.append(Slime(sx % config.MAP_WIDTH, sy % config.MAP_HEIGHT, config.SLIME_RADIUS, config.SLIME_GREEN, config.SLIME_SPEED, state.current_slime_max_hp))

def handle_boss_logic(state):
    """보스 등장 및 사망 처리를 담당합니다."""
    # 보스 스폰 체크
    if not state.boss_active and state.player.total_enemies_killed > 0:
        # 설정된 킬 수마다 보스 소환 (예: 150, 300, 450...)
        if state.player.total_enemies_killed % config.BOSS_SLIME_SPAWN_KILL_THRESHOLD == 0 and not state.boss_slimes:
            state.boss_active = True
            
            # 플레이어 근처에 소환
            bx = (state.player.world_x + 300) % config.MAP_WIDTH
            by = (state.player.world_y + 300) % config.MAP_HEIGHT
            
            # 🚩 [리메이크 핵심] BossSlime 생성 시 현재까지 잡은 보스 수(boss_index)를 인자로 넘김!
            # 1번째 보스 소환 시: total_bosses_killed = 0
            # 2번째 보스 소환 시: total_bosses_killed = 1
            # 3번째 보스 소환 시: total_bosses_killed = 2 (이때부터 각성 보스 등장)
            state.boss_slimes.append(BossSlime(bx, by, state.current_slime_max_hp, state.player.total_bosses_killed))
            print(f"보스 등장! (누적 {state.player.total_bosses_killed + 1}회차)")

    # 보스 업데이트 및 사망 처리
    # 보스의 update 함수 내부에서 페이즈 전환, 거대 탄환, 슈터 소환 패턴이 돌아갑니다.
    bosses_to_remove = [b for b in state.boss_slimes if not b.update(state.player.world_x, state.player.world_y, state.get_entities_dict())]
    
    for boss in bosses_to_remove:
        state.boss_active = False
        state.player.total_bosses_killed += 1 # 처치 수 증가
        state.player.trigger_boss_reward_selection() # 보상 창 띄우기
        
        # 보상으로 대량의 경험치 구슬 생성
        for _ in range(20):
            state.exp_orbs.append(ExpOrb(boss.world_x + random.randint(-50,50), boss.world_y + random.randint(-50,50)))
            
    # 사망한 보스 리스트에서 제거
    state.boss_slimes[:] = [b for b in state.boss_slimes if b not in bosses_to_remove]