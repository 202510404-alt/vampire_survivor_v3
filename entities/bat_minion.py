import pygame
import math
import random
import config
import utils
from core.grid import enemy_grid

class BatMinion:
    STATE_WANDERING = 0
    STATE_ATTACKING = 1
    STATE_COOLDOWN = 2
    _id_counter = 1

    def __init__(self, controller_ref, world_x, world_y):
        self.controller = controller_ref
        self.player = self.controller.player 
        self.world_x = float(world_x % config.MAP_WIDTH)
        self.world_y = float(world_y % config.MAP_HEIGHT)
        self.bat_id = BatMinion._id_counter
        BatMinion._id_counter += 1
        
        # 🟢 처형용 위치 추적 (1초 전 좌표)
        self.last_sec_x = self.world_x
        self.last_sec_y = self.world_y
        self.log_timer = 0
        
        self.size = config.BAT_SIZE
        self.color = config.BAT_COLOR
        self.lifespan = config.BAT_LIFESPAN_SECONDS * config.FPS
        self.state = BatMinion.STATE_WANDERING
        self.target_slime = None
        self.attack_cooldown_timer = 0
        self.wander_target_x = self.world_x
        self.wander_target_y = self.world_y
        self.time_to_new_wander_target = 0

    def update(self, slimes_list, game_entities_lists):
        # ----------------------------------------------------
        # 🟢 [처형 시스템] 1초마다 움직임 감시
        # ----------------------------------------------------
        self.log_timer += 1
        if self.log_timer >= config.FPS: # 1초 도달
            # 1단계: 인식 (좌표 변화 체크)
            # 아주 미세한 떨림(0.5px 미만)도 멈춘 것으로 간주
            dist_moved = math.sqrt((self.world_x - self.last_sec_x)**2 + (self.world_y - self.last_sec_y)**2)
            
            print(f"박쥐{self.bat_id} 생존신고 | x:{int(self.world_x)} y:{int(self.world_y)} | 이동거리:{dist_moved:.2f}")

            if dist_moved < 0.5:
                # 2단계: 죽이기 실행
                print(f"🚩 [인식!] 박쥐{self.bat_id}가 멈춰있는 것을 확인했습니다.")
                print(f"💀 [죽이기 실행!] 박쥐{self.bat_id} 처형을 시작합니다.")
                
                # 3단계: 실행 완료 (False를 리턴하면 리스트에서 즉시 삭제됨)
                print(f"✅ [실행 완료!] 박쥐{self.bat_id}가 리스트에서 제거되었습니다.")
                return False 

            # 움직였다면 다음 감시를 위해 현재 좌표 저장
            self.last_sec_x = self.world_x
            self.last_sec_y = self.world_y
            self.log_timer = 0

        # --- 수명 체크 ---
        self.lifespan -= 1
        if self.lifespan <= 0: return False

        # --- 적 발사체 제거 로직 (생략 방지용 유지) ---
        bullets = game_entities_lists.get('slime_bullets')
        if bullets:
            for sb in bullets:
                if not getattr(sb, 'is_hit_by_player_attack', False):
                    if utils.distance_sq_wrapped(self.world_x, self.world_y, sb.world_x, sb.world_y, config.MAP_WIDTH, config.MAP_HEIGHT) < (self.size + sb.size)**2:
                        sb.is_hit_by_player_attack = True

        # --- 상태 머신 및 이동 로직 ---
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1
            if self.attack_cooldown_timer <= 0:
                self.state = BatMinion.STATE_WANDERING

        if self.state == BatMinion.STATE_ATTACKING:
            if not self.target_slime or self.target_slime.hp <= 0:
                self.target_slime = None
                self.state = BatMinion.STATE_WANDERING
            else:
                dx = utils.get_wrapped_delta(self.world_x, self.target_slime.world_x, config.MAP_WIDTH)
                dy = utils.get_wrapped_delta(self.world_y, self.target_slime.world_y, config.MAP_HEIGHT)
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < (self.size + self.target_slime.radius):
                    self.target_slime.take_damage(self.controller.damage)
                    self.player.heal(self.controller.damage * self.controller.lifesteal_percentage)
                    self.state = BatMinion.STATE_COOLDOWN
                    self.attack_cooldown_timer = config.BAT_ATTACK_COOLDOWN
                    self.target_slime = None
                elif dist > 0:
                    self.angle = math.atan2(dy, dx)
                    self.world_x = (self.world_x + math.cos(self.angle) * config.BAT_ATTACK_SPEED) % config.MAP_WIDTH
                    self.world_y = (self.world_y + math.sin(self.angle) * config.BAT_ATTACK_SPEED) % config.MAP_HEIGHT
        
        if self.state != BatMinion.STATE_ATTACKING:
            if self.state == BatMinion.STATE_WANDERING:
                nearby = enemy_grid.get_nearby_enemies(self.world_x, self.world_y, 2)
                for s in nearby:
                    if s.hp > 0 and utils.distance_sq_wrapped(self.world_x, self.world_y, s.world_x, s.world_y, config.MAP_WIDTH, config.MAP_HEIGHT) < config.BAT_DETECTION_RADIUS**2:
                        self.target_slime = s
                        self.state = BatMinion.STATE_ATTACKING
                        break
            self._wander()

        return True

    def _wander(self):
        self.time_to_new_wander_target -= 1
        if self.time_to_new_wander_target <= 0:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(config.BAT_WANDER_RADIUS_FROM_PLAYER*0.5, config.BAT_WANDER_RADIUS_FROM_PLAYER)
            self.wander_target_x = (self.player.world_x + dist * math.cos(angle)) % config.MAP_WIDTH
            self.wander_target_y = (self.player.world_y + dist * math.sin(angle)) % config.MAP_HEIGHT
            self.time_to_new_wander_target = random.randint(config.FPS, config.FPS * 3)

        dx = utils.get_wrapped_delta(self.world_x, self.wander_target_x, config.MAP_WIDTH)
        dy = utils.get_wrapped_delta(self.world_y, self.wander_target_y, config.MAP_HEIGHT)
        dist_sq = dx*dx + dy*dy
        
        if dist_sq > 1.0:
            self.angle = math.atan2(dy, dx)
            self.world_x = (self.world_x + math.cos(self.angle) * config.BAT_WANDER_SPEED) % config.MAP_WIDTH
            self.world_y = (self.world_y + math.sin(self.angle) * config.BAT_WANDER_SPEED) % config.MAP_HEIGHT
        else:
            self.time_to_new_wander_target = 0

    def draw(self, surface, camera_offset_x, camera_offset_y):
        scr_x = (self.world_x - camera_offset_x) % config.MAP_WIDTH
        if scr_x > config.MAP_WIDTH / 2: scr_x -= config.MAP_WIDTH
        scr_y = (self.world_y - camera_offset_y) % config.MAP_HEIGHT
        if scr_y > config.MAP_HEIGHT / 2: scr_y -= config.MAP_HEIGHT
        if -self.size < scr_x < config.SCREEN_WIDTH + self.size and -self.size < scr_y < config.SCREEN_HEIGHT + self.size:
            pygame.draw.circle(surface, self.color, (int(scr_x), int(scr_y)), self.size)