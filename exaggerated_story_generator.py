"""
誇張成語故事生成器
專門生成超級誇張、超有記憶點的漫畫風格故事
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class ExaggeratedStoryGenerator:
    """誇張故事生成器"""

    def __init__(self):
        """初始化"""
        self.visual_effects = {
            "火焰特效": ["眼睛燃燒", "動作產生火焰", "背景著火"],
            "閃電特效": ["快速移動閃電", "組合技視覺", "衝擊力表現"],
            "爆炸特效": ["背景爆炸", "物品崩塌", "情緒爆發"],
            "誇張表情": ["下巴掉落", "眼睛凸出", "變成石像", "崩潰成灰"],
            "擬聲詞": ["轟", "砰", "刷刷刷", "咚"],
            "慢動作": ["重要時刻", "衝擊畫面", "戲劇性轉折"]
        }

        self.dramatic_elements = {
            "視覺衝擊": ["超大尺寸", "強烈對比", "鮮豔色彩"],
            "情感共鳴": ["極度驚訝", "超級崩潰", "絕望感"],
            "荒謬元素": ["不合理數量", "超現實場景", "意想不到結果"],
            "反轉效果": ["完美→失敗", "自信→崩潰", "得意→絕望"]
        }

    def generate_exaggerated_story(
        self,
        idiom: str,
        meaning: str,
        version: int = 1
    ) -> Dict[str, Any]:
        """
        生成誇張版本的故事

        Args:
            idiom: 成語
            meaning: 成語含義
            version: 版本號

        Returns:
            誇張故事數據
        """
        # 這裡會根據成語生成超級誇張的故事
        # 實際應用中可以結合 Gemini API

        story_templates = self._get_exaggerated_template(idiom, version)

        return {
            "idiom": idiom,
            "meaning": meaning,
            "version": version,
            "style": "超級誇張漫畫風",
            **story_templates
        }

    def _get_exaggerated_template(self, idiom: str, version: int) -> Dict:
        """獲取誇張模板"""
        # 返回預設的誇張元素
        return {
            "visual_effects": list(self.visual_effects.keys()),
            "dramatic_elements": list(self.dramatic_elements.keys()),
            "memory_points": self._generate_memory_points(idiom)
        }

    def _generate_memory_points(self, idiom: str) -> List[str]:
        """生成記憶點"""
        memory_points = [
            "超級誇張的視覺效果",
            "戲劇性的情節轉折",
            "極度的情感表現",
            "荒謬的元素設計",
            "意想不到的結局"
        ]
        return memory_points

    def add_exaggerated_effects(self, scene: Dict) -> Dict:
        """
        為場景添加誇張效果

        Args:
            scene: 場景數據

        Returns:
            添加效果後的場景
        """
        # 添加誇張的視覺效果描述
        effects = []

        # 根據場景階段添加不同效果
        phase = scene.get("phase", "")

        if phase == "起":
            effects.extend([
                "金光閃閃的開場",
                "背景星光璀璨",
                "角色登場特效"
            ])
        elif phase == "承":
            effects.extend([
                "火焰燃燒的氣勢",
                "閃電環繞的效果",
                "能量爆發的視覺"
            ])
        elif phase == "轉":
            effects.extend([
                "超級爆炸場面",
                "極度震驚表情",
                "天崩地裂特效"
            ])
        elif phase == "合":
            effects.extend([
                "教學卡片特效",
                "總結光芒效果",
                "學習完成標誌"
            ])

        scene["exaggerated_effects"] = effects
        return scene


def create_exaggerated_story_example():
    """創建誇張故事示例"""

    generator = ExaggeratedStoryGenerator()

    # 示例：生成「畫蛇添足」的誇張版本
    story = {
        "idiom": "畫蛇添足",
        "version": 1,
        "title": "小明 VS 畫畫大魔王",
        "setting": "全國超級無敵美術大賽現場",
        "characters": ["小明(天才畫家)", "評審長(超嚴格)", "觀眾(萬人)"],
        "duration_seconds": 90,
        "style": "少年熱血漫畫風",
        "outline": "全國美術大賽決賽！小明畫出一條超級完美的蛇...",
        "scenes": []
    }

    # 生成8個場景
    scene_templates = [
        ("起", "體育館內燈光聚焦，小明站在畫布前，背後是萬人觀眾", 12),
        ("起", "開始作畫！小明的畫筆快到產生殘影", 12),
        ("承", "完成！觀眾驚呆，評審準備給滿分", 10),
        ("承", "突然！小明內心獨白「還可以更完美！」", 10),
        ("轉", "倒數10秒！小明瘋狂畫上四隻火焰腳", 10),
        ("轉", "時間到！全場安靜3秒...評審下巴掉落", 12),
        ("轉", "評審大喊「蛇沒有腳！」小明石化崩潰", 12),
        ("合", "成語教學卡片出現", 12)
    ]

    for i, (phase, desc, duration) in enumerate(scene_templates, 1):
        scene = {
            "scene": i,
            "phase": phase,
            "description": desc,
            "duration": duration
        }

        # 添加誇張效果
        scene = generator.add_exaggerated_effects(scene)

        story["scenes"].append(scene)

    return story


def main():
    """主演示函數"""

    print("=" * 70)
    print("超級誇張成語故事生成器")
    print("=" * 70)
    print()

    # 創建示例
    story = create_exaggerated_story_example()

    # 顯示故事
    print(f"成語: {story['idiom']}")
    print(f"標題: {story['title']}")
    print(f"場景: {story['setting']}")
    print(f"風格: {story['style']}")
    print(f"時長: {story['duration_seconds']}秒")
    print()

    print("場景列表:")
    print("-" * 70)

    for scene in story["scenes"]:
        print(f"\n【場景 {scene['scene']}】- {scene['phase']}階段")
        print(f"描述: {scene['description']}")
        print(f"時長: {scene['duration']}秒")
        print(f"誇張效果:")
        for effect in scene.get("exaggerated_effects", []):
            print(f"  - {effect}")

    print()
    print("=" * 70)
    print("誇張故事生成完成！")
    print("=" * 70)

    # 保存到文件
    output_file = Path("./output/exaggerated_story_example.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(story, f, ensure_ascii=False, indent=2)

    print(f"\n故事已保存到: {output_file}")


if __name__ == "__main__":
    main()