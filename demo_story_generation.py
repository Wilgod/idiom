"""
演示腳本：生成「畫蛇添足」成語動畫故事
展示完整的故事結構、秒數分配和分鏡處理
"""

import json
import sys
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import logger
from src.utils.gemini_client import GeminiClient
from src.core.character_manager import CharacterManager
from src.core.idiom_manager import IdiomManager
from src.core.prompt_builder import PromptBuilder
from src.core.story_generator import StoryGenerator


def print_section(title: str):
    """打印分隔線"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_story_details(story_data: dict):
    """打印故事詳細信息"""
    # 故事基本信息
    print_section("故事基本信息")
    metadata = story_data.get("metadata", {})
    print(f"成語: {metadata.get('idiom')}")
    print(f"拼音: {metadata.get('pinyin')}")
    print(f"含義: {metadata.get('meaning')}")
    print(f"總時長: {metadata.get('total_duration')} 秒")
    print(f"場景數: {metadata.get('scene_count')} 個")
    print(f"角色: {', '.join([c.get('name') for c in metadata.get('characters', [])])}")

    # 故事標題和大綱
    print_section("故事內容")
    print(f"標題: {story_data.get('story_title')}")
    print(f"\n大綱:")
    print(f"  {story_data.get('story_outline')}")
    print(f"\n寓意:")
    print(f"  {story_data.get('moral')}")

    # 詳細分鏡表
    print_section("詳細分鏡表")
    scenes = story_data.get("scenes", [])

    for i, scene in enumerate(scenes, 1):
        scene_num = scene.get("scene_number", i)
        phase = scene.get("phase", "未知")
        duration = scene.get("duration_seconds", 8)

        print(f"\n【場景 {scene_num}】- {phase}階段")
        print(f"┌{'─'*66}┐")
        print(f"│ 時長: {duration} 秒{' '*55}│")
        print(f"├{'─'*66}┤")
        print(f"│ 場景描述:")
        desc = scene.get("scene_description", "")
        # 格式化描述
        for line in wrap_text(desc, 60):
            print(f"│   {line}{' '*(62-len(line))}│")

        if scene.get("character_actions"):
            print(f"├{'─'*66}┤")
            print(f"│ 角色動作:")
            actions = scene.get("character_actions", "")
            for line in wrap_text(actions, 60):
                print(f"│   {line}{' '*(62-len(line))}│")

        if scene.get("subtitle"):
            print(f"├{'─'*66}┤")
            print(f"│ 字幕:")
            subtitle = scene.get("subtitle", "")
            for line in wrap_text(subtitle, 60):
                print(f"│   {line}{' '*(62-len(line))}│")

        print(f"└{'─'*66}┘")

    # 統計信息
    print_section("時間統計")
    phase_durations = {}
    for scene in scenes:
        phase = scene.get("phase", "未知")
        duration = scene.get("duration_seconds", 8)
        phase_durations[phase] = phase_durations.get(phase, 0) + duration

    print("各階段時長分配:")
    phase_names = {"起": "起始", "承": "發展", "轉": "轉折", "合": "結尾"}
    for phase, duration in phase_durations.items():
        percentage = (duration / metadata.get("total_duration", 1)) * 100
        phase_name = phase_names.get(phase, phase)
        print(f"  {phase} ({phase_name}): {duration} 秒 ({percentage:.1f}%)")

    print(f"\n總計: {metadata.get('total_duration')} 秒")

    # 輸出 JSON
    print_section("完整 JSON 數據")
    print(json.dumps(story_data, ensure_ascii=False, indent=2))


def wrap_text(text: str, width: int = 60) -> list:
    """文字換行"""
    if not text:
        return []

    lines = []
    current_line = ""

    # 按中文字符寬度處理
    for char in text:
        # 中文字符算2個寬度
        char_width = 2 if '\u4e00' <= char <= '\u9fff' else 1

        if len(current_line) + char_width <= width:
            current_line += char
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines


def main():
    """主演示流程"""
    print_section("畫蛇添足 - 成語動畫故事生成演示")

    try:
        # 初始化組件
        print("正在初始化系統組件...")
        gemini_client = GeminiClient()
        character_manager = CharacterManager()
        idiom_manager = IdiomManager()
        prompt_builder = PromptBuilder()
        story_generator = StoryGenerator(
            gemini_client=gemini_client,
            character_manager=character_manager,
            idiom_manager=idiom_manager,
            prompt_builder=prompt_builder
        )
        print("✓ 系統初始化完成\n")

        # 獲取成語信息
        print("正在獲取成語信息...")
        idiom = idiom_manager.get_idiom("idiom_001")
        if idiom:
            print(f"✓ 成語: {idiom.get('idiom')}")
            print(f"  拼音: {idiom.get('pinyin')}")
            print(f"  含義: {idiom.get('meaning')}\n")

        # 生成故事
        print("正在生成故事結構（這可能需要 10-30 秒）...")
        print("提示：使用 Gemini API 生成故事內容...\n")

        story_data = story_generator.generate_story(
            idiom_id="idiom_001",
            protagonist_id="xiaoming",  # 小明作為主角
            supporting_character_ids=["lily", "laoshi"]  # 小麗和王老師作為配角
        )

        # 生成詳細場景描述
        print("正在生成詳細場景描述...")
        characters = [
            character_manager.get_character("xiaoming"),
            character_manager.get_character("lily"),
            character_manager.get_character("laoshi")
        ]
        characters = [c for c in characters if c]  # 過濾 None

        scenes = story_generator.generate_scene_descriptions(story_data, characters)
        story_data["scenes"] = scenes

        print("✓ 故事生成完成\n")

        # 打印完整故事
        print_story_details(story_data)

        # 保存到文件
        output_file = Path("./output/畫蛇添足_story.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(story_data, f, ensure_ascii=False, indent=2)

        print_section("完成")
        print(f"✓ 故事數據已保存到: {output_file}")

    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

        print("\n提示：請確保已設置正確的 GEMINI_API_KEY")
        print("在 .env 文件中設置：")
        print("  GEMINI_API_KEY=your_actual_api_key_here")


if __name__ == "__main__":
    main()