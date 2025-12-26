import math
import config
import utils
from entities.storm_projectile import StormProjectile

class StormSkill:
    def __init__(self, player_ref):
        self.player = player_ref
        self.name = "태풍"
        self.level = 1
        self.base_damage = config.STORM_SKILL_BASE_DAMAGE
        self.cooldown = config.STORM_SKILL_COOLDOWN_SECONDS * config.FPS
        self.cooldown_timer = self.cooldown
        self.num_projectiles = 1

    def update(self):
        if self.cooldown_timer < self.cooldown:
            self.cooldown_timer += 1

    def get_current_projectile_damage(self):
        if self.num_projectiles == 0: return 0
        return math.ceil(self.base_damage / self.num_projectiles)

    # 🟢 [수정] 좌표 인자(target_x, y)를 제거했습니다.
    def activate(self, game_entities_lists):
        if self.cooldown_timer >= self.cooldown:
            self.cooldown_timer = 0
            storm_list = game_entities_lists.get('storm_projectiles')
            if storm_list is None: return

            # 🚩 플레이어의 현재 보는 방향 각도를 가져옵니다.
            center_angle = self.player.facing_angle
            
            # 발사 각도 계산 (부채꼴)
            if self.num_projectiles == 1:
                angles = [center_angle]
            else:
                total_spread = math.pi # 180도 범위
                angle_step = total_spread / (self.num_projectiles - 1)
                start_angle = center_angle - total_spread / 2
                angles = [start_angle + i * angle_step for i in range(self.num_projectiles)]

            damage = self.get_current_projectile_damage()
            for angle in angles:
                storm_list.append(StormProjectile(self.player.world_x, self.player.world_y, angle, damage))

    def generate_upgrade_options(self):
        # (업그레이드 옵션은 기존과 동일)
        options = [
            {"text": f"폭풍 개수 증가 ({self.num_projectiles} -> {self.num_projectiles+1})", "type": "num_projectiles", "value": self.num_projectiles+1},
            {"text": f"데미지 증가 ({self.base_damage} -> {self.base_damage+config.STORM_SKILL_DAMAGE_INCREASE})", "type": "damage", "value": self.base_damage+config.STORM_SKILL_DAMAGE_INCREASE},
            {"text": "쿨타임 감소", "type": "cooldown", "value": max(config.FPS*5, self.cooldown - config.STORM_SKILL_COOLDOWN_DECREASE_SECONDS*config.FPS)}
        ]
        return options

    def apply_upgrade(self, upgrade_info):
        if upgrade_info["type"] == "num_projectiles": self.num_projectiles = upgrade_info["value"]
        elif upgrade_info["type"] == "damage": self.base_damage = upgrade_info["value"]
        elif upgrade_info["type"] == "cooldown": self.cooldown = upgrade_info["value"]
        self.level += 1