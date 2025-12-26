import random
import math
import pygame
import config
import utils
from weapons.base_weapon import Weapon
from entities.bat_minion import BatMinion # 박쥐 미니언을 생성하기 위해

class BatController(Weapon):
    def __init__(self, player_ref):
        super().__init__(player_ref)
        self.name = "박쥐 소환"
        self.damage = config.BAT_BASE_DAMAGE
        self.lifesteal_percentage = config.BAT_LIFESTEAL_PERCENTAGE
        self.max_bats = config.BAT_MAX_COUNT_INITIAL
        # 소환 쿨타임은 이제 초기 스폰시에만 의미가 있거나, 
        # 시스템 안정성을 위해 남겨두지만 사실상 while문이 즉시 채워줄 겁니다.
        self.spawn_cooldown = config.FPS * 1 
        self.spawn_timer = 0

    def update(self, slimes_list, game_entities_lists):
        bats_list_ref = game_entities_lists.get('bats')
        if bats_list_ref is None: return

        # 🟢 1. 현재 이 컨트롤러가 소환한 박쥐가 몇 마리인지 체크
        current_bat_count = sum(1 for b in bats_list_ref if isinstance(b, BatMinion) and b.controller == self)

        # 🟢 2. [핵심] 최대 박쥐 수보다 부족하면 즉시 소환 (while 루프 사용)
        # 박쥐 미니언이 자폭하거나 죽어서 자리가 비면 0.0001초만에 새로 뽑습니다.
        while current_bat_count < self.max_bats:
            spawn_angle = random.uniform(0, 2 * math.pi)
            # 플레이어 주변 살짝 떨어진 위치에서 소환
            spawn_dist = random.uniform(config.PLAYER_SIZE, config.PLAYER_SIZE + 20)
            spawn_x = (self.player.world_x + spawn_dist * math.cos(spawn_angle)) % config.MAP_WIDTH
            spawn_y = (self.player.world_y + spawn_dist * math.sin(spawn_angle)) % config.MAP_HEIGHT
            
            # 박쥐 생성 및 리스트 추가
            new_bat = BatMinion(self, spawn_x, spawn_y)
            bats_list_ref.append(new_bat)
            
            current_bat_count += 1
            print(f"DEBUG: 박쥐 결손 감지! 즉시 충원합니다. ({current_bat_count}/{self.max_bats})")

    def draw(self, surface, camera_offset_x, camera_offset_y):
        pass # 박쥐 컨트롤러 자체는 화면에 그릴 것이 없음 (소환된 박쥐들이 직접 그려짐)

    def get_level_up_options(self):
        """레벨업 시 제공할 옵션들"""
        options = [
            {"text": f"박쥐 데미지 ({self.damage} -> {math.ceil(self.damage*config.BAT_DAMAGE_MULTIPLIER_PER_LEVEL)})", "type": "damage", "value": math.ceil(self.damage*config.BAT_DAMAGE_MULTIPLIER_PER_LEVEL)},
            {"text": f"최대 박쥐 수 ({self.max_bats} -> {self.max_bats+config.BAT_MAX_COUNT_INCREASE_PER_LEVEL})", "type": "max_bats", "value": self.max_bats+config.BAT_MAX_COUNT_INCREASE_PER_LEVEL},
            {"text": f"박쥐 흡혈량 ({(self.lifesteal_percentage*100):.0f}% -> {((self.lifesteal_percentage+0.02)*100):.0f}%)", "type": "lifesteal", "value": min(1.0,self.lifesteal_percentage+0.02)}
        ]
        # 옵션 중 무작위로 2개 선택해서 보여줌
        return random.sample(options, min(len(options), 2))

    def apply_upgrade(self, upgrade_info):
        """선택한 업그레이드 적용"""
        if upgrade_info["type"] == "damage": 
            self.damage = upgrade_info["value"]
        elif upgrade_info["type"] == "max_bats": 
            self.max_bats = upgrade_info["value"]
        elif upgrade_info["type"] == "lifesteal": 
            self.lifesteal_percentage = upgrade_info["value"]
        self.level += 1
    
    def on_remove(self):
        """무기 교체 등을 대비한 정리 로직"""
        pass