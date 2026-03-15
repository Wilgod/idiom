"""
成語動畫故事生成系統 - 主程式入口
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加 src 目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import logger
from utils.gemini_client import GeminiClient
from core.character_manager import CharacterManager
from core.idiom_manager import IdiomManager
from core.prompt_builder import PromptBuilder
from core.story_generator import StoryGenerator
from generators.image_generator import ImageGenerator
from generators.video_generator import VideoGenerator


class IdiomAnimationGenerator:
    """成語動畫故事生成器"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化成語動畫生成器

        Args:
            config: 配置字典
        """
        logger.info("初始化成語動畫生成器...")

        # 初始化各個模塊
        self.gemini_client = GeminiClient()
        self.character_manager = CharacterManager()
        self.idiom_manager = IdiomManager()
        self.prompt_builder = PromptBuilder()
        self.story_generator = StoryGenerator(
            gemini_client=self.gemini_client,
            character_manager=self.character_manager,
            idiom_manager=self.idiom_manager,
            prompt_builder=self.prompt_builder
        )
        self.image_generator = ImageGenerator(
            gemini_client=self.gemini_client,
            character_manager=self.character_manager,
            prompt_builder=self.prompt_builder
        )
        self.video_generator = VideoGenerator()

        logger.info("成語動畫生成器初始化完成！")

    def generate_animation(
        self,
        idiom_id: str,
        protagonist_id: Optional[str] = None,
        supporting_character_ids: Optional[List[str]] = None,
        generate_video: bool = True,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成成語動畫

        Args:
            idiom_id: 成語ID
            protagonist_id: 主角ID
            supporting_character_ids: 配角ID列表
            generate_video: 是否生成視頻
            output_filename: 輸出文件名

        Returns:
            結果字典，包含成功狀態和各種路徑信息
        """
        result = {
            "success": False,
            "idiom": None,
            "idiom_id": idiom_id,
            "story_structure": None,
            "image_paths": [],
            "video_path": None,
            "error": None
        }

        try:
            # 步驟 1: 獲取成語信息
            logger.info(f"="*50)
            logger.info(f"步驟 1: 獲取成語信息 - {idiom_id}")
            idiom = self.idiom_manager.get_idiom(idiom_id)
            if not idiom:
                raise ValueError(f"成語不存在: {idiom_id}")
            result["idiom"] = idiom
            logger.info(f"成語: {idiom.get('idiom')} - {idiom.get('meaning')}")

            # 步驟 2: 生成故事結構
            logger.info(f"="*50)
            logger.info(f"步驟 2: 生成故事結構")
            story_data = self.story_generator.generate_story(
                idiom_id=idiom_id,
                protagonist_id=protagonist_id,
                supporting_character_ids=supporting_character_ids
            )
            result["story_structure"] = story_data

            # 打印故事摘要
            summary = self.story_generator.get_story_summary(story_data)
            logger.info(f"\n{summary}")

            # 步驟 3: 生成場景描述
            logger.info(f"="*50)
            logger.info(f"步驟 3: 生成場景詳細描述")
            characters = self.character_manager.get_all_characters()
            scenes = self.story_generator.generate_scene_descriptions(story_data, characters)
            story_data["scenes"] = scenes
            result["story_structure"] = story_data

            # 步驟 4: 生成圖片
            logger.info(f"="*50)
            logger.info(f"步驟 4: 生成場景圖片")
            image_paths = self.image_generator.generate_all_scenes(
                story_data=story_data,
                characters=characters
            )
            result["image_paths"] = image_paths

            # 步驟 5: 生成視頻
            if generate_video:
                logger.info(f"="*50)
                logger.info(f"步驟 5: 生成視頻")

                # 準備字幕
                subtitles = [scene.get("subtitle", "") for scene in scenes]

                # 準備場景時長
                scene_durations = [scene.get("duration_seconds", 8) for scene in scenes]

                # 確定輸出文件名
                if output_filename is None:
                    idiom_text = idiom.get("idiom", "idiom")
                    output_filename = f"{idiom_text}_animation.mp4"

                # 創建視頻
                video_path = self.video_generator.create_video_from_images(
                    image_paths=image_paths,
                    output_filename=output_filename,
                    scene_durations=scene_durations,
                    subtitles=subtitles
                )
                result["video_path"] = video_path

            result["success"] = True
            logger.info(f"="*50)
            logger.info(f"成語動畫生成完成！")
            logger.info(f"成語: {idiom.get('idiom')}")
            logger.info(f"總時長: {story_data.get('metadata', {}).get('total_duration', 0)}秒")

            if result["video_path"]:
                logger.info(f"視頻路徑: {result['video_path']}")

            return result

        except Exception as e:
            logger.error(f"生成失敗: {str(e)}")
            result["error"] = str(e)
            return result

    def batch_generate(
        self,
        idiom_ids: List[str],
        protagonist_id: Optional[str] = None,
        supporting_character_ids: Optional[List[str]] = None,
        generate_video: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量生成成語動畫

        Args:
            idiom_ids: 成語ID列表
            protagonist_id: 主角ID
            supporting_character_ids: 配角ID列表
            generate_video: 是否生成視頻

        Returns:
            結果列表
        """
        results = []

        logger.info(f"開始批量生成 {len(idiom_ids)} 個成語動畫...")

        for i, idiom_id in enumerate(idiom_ids):
            logger.info(f"\n{'='*50}")
            logger.info(f"處理第 {i+1}/{len(idiom_ids)} 個成語: {idiom_id}")
            logger.info(f"{'='*50}")

            result = self.generate_animation(
                idiom_id=idiom_id,
                protagonist_id=protagonist_id,
                supporting_character_ids=supporting_character_ids,
                generate_video=generate_video
            )
            results.append(result)

        # 統計結果
        success_count = sum(1 for r in results if r["success"])
        logger.info(f"\n批量生成完成！成功: {success_count}/{len(idiom_ids)}")

        return results

    def list_idioms(self) -> List[Dict[str, Any]]:
        """
        列出所有可用成語

        Returns:
            成語列表
        """
        return self.idiom_manager.get_all_idioms()

    def list_characters(self) -> List[Dict[str, Any]]:
        """
        列出所有可用角色

        Returns:
            角色列表
        """
        return self.character_manager.get_all_characters()


def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="成語動畫故事生成系統")
    parser.add_argument(
        "--idiom",
        "-i",
        help="成語ID (例如: idiom_001)"
    )
    parser.add_argument(
        "--list-idioms",
        "-l",
        action="store_true",
        help="列出所有可用成語"
    )
    parser.add_argument(
        "--list-characters",
        action="store_true",
        help="列出所有可用角色"
    )
    parser.add_argument(
        "--protagonist",
        "-p",
        help="主角ID"
    )
    parser.add_argument(
        "--batch",
        "-b",
        nargs="+",
        help="批量生成成語動畫"
    )
    parser.add_argument(
        "--no-video",
        action="store_true",
        help="只生成圖片，不生成視頻"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="輸出文件名"
    )

    args = parser.parse_args()

    # 初始化生成器
    generator = IdiomAnimationGenerator()

    # 列出成語
    if args.list_idioms:
        idioms = generator.list_idioms()
        print("\n可用成語列表:")
        print("-" * 60)
        for idiom in idioms:
            print(f"  {idiom.get('id'):15} {idiom.get('idiom'):10} ({idiom.get('pinyin')})")
            print(f"    含義: {idiom.get('meaning')}")
            print(f"    難度: {idiom.get('difficulty_level')}")
            print()
        return

    # 列出角色
    if args.list_characters:
        characters = generator.list_characters()
        print("\n可用角色列表:")
        print("-" * 60)
        for char in characters:
            print(f"  {char.get('character_id'):15} {char.get('name'):10} ({char.get('role_type')})")
            print(f"    年齡: {char.get('age')}, 性別: {char.get('gender')}")
            print(f"    性格: {', '.join(char.get('personality', []))}")
            print()
        return

    # 批量生成
    if args.batch:
        results = generator.batch_generate(
            idiom_ids=args.batch,
            protagonist_id=args.protagonist,
            generate_video=not args.no_video
        )

        success = sum(1 for r in results if r["success"])
        print(f"\n批量生成完成！成功: {success}/{len(args.batch)}")
        return

    # 單個生成
    if args.idiom:
        result = generator.generate_animation(
            idiom_id=args.idiom,
            protagonist_id=args.protagonist,
            generate_video=not args.no_video,
            output_filename=args.output
        )

        if result["success"]:
            print("\n生成成功！")
            print(f"成語: {result['idiom'].get('idiom')}")
            print(f"含義: {result['idiom'].get('meaning')}")
            print(f"時長: {result['story_structure'].get('metadata', {}).get('total_duration', 0)}秒")

            if result.get("video_path"):
                print(f"視頻: {result['video_path']}")
            if result.get("image_paths"):
                print(f"圖片: {len(result['image_paths'])} 張")
        else:
            print(f"\n生成失敗: {result.get('error')}")
        return

    # 顯示幫助
    parser.print_help()


if __name__ == "__main__":
    main()
