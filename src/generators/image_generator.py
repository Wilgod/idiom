"""
圖片生成器
負責使用 Gemini API 生成動畫圖片
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.logger import logger
from ..utils.gemini_client import GeminiClient
from ..core.character_manager import CharacterManager
from ..core.prompt_builder import PromptBuilder


class ImageGenerator:
    """圖片生成器"""

    def __init__(
        self,
        gemini_client: GeminiClient,
        character_manager: CharacterManager,
        prompt_builder: PromptBuilder,
        output_dir: str = "./output/images"
    ):
        """
        初始化圖片生成器

        Args:
            gemini_client: Gemini 客戶端
            character_manager: 角色管理器
            prompt_builder: 提示詞構建器
            output_dir: 輸出目錄
        """
        self.gemini_client = gemini_client
        self.character_manager = character_manager
        self.prompt_builder = prompt_builder
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"圖片生成器初始化完成，輸出目錄: {self.output_dir}")

    def generate_character_image(
        self,
        character_id: str,
        expression: Optional[str] = None,
        action: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> str:
        """
        生成角色圖片

        Args:
            character_id: 角色ID
            expression: 表情類型
            action: 動作類型
            output_filename: 輸出文件名

        Returns:
            生成的圖片路徑
        """
        logger.info(f"生成角色圖片: {character_id}, expression={expression}, action={action}")

        # 獲取角色基礎提示詞
        character = self.character_manager.get_character(character_id)
        if not character:
            raise ValueError(f"角色不存在: {character_id}")

        base_prompt = character.get("gemini_prompts", {}).get("base", "")

        # 構建圖片提示詞
        prompt = self.prompt_builder.build_character_image_prompt(
            character_prompt=base_prompt,
            expression=expression,
            action=action
        )

        # 確定輸出路徑
        if not output_filename:
            parts = [character_id]
            if expression:
                parts.append(expression)
            if action:
                parts.append(action)
            output_filename = "_".join(parts) + ".png"

        output_path = self.output_dir / output_filename

        # 生成圖片
        try:
            self.gemini_client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            logger.info(f"角色圖片生成成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"角色圖片生成失敗: {str(e)}")
            raise

    def generate_scene_image(
        self,
        scene_description: str,
        include_characters: Optional[List[Dict[str, Any]]] = None,
        output_filename: Optional[str] = None,
        scene_number: int = 0
    ) -> str:
        """
        生成場景圖片

        Args:
            scene_description: 場景描述
            include_characters: 包含的角色列表
            output_filename: 輸出文件名
            scene_number: 場景編號

        Returns:
            生成的圖片路徑
        """
        logger.info(f"生成場景圖片: 場景 {scene_number}")

        # 準備角色描述
        character_descriptions = []
        if include_characters:
            for char in include_characters:
                char_desc = self.prompt_builder.build_character_image_prompt(
                    character_prompt=char.get("gemini_prompts", {}).get("base", ""),
                    expression=char.get("expression"),
                    action=char.get("action")
                )
                character_descriptions.append(char_desc)

        # 構建圖片提示詞
        prompt = self.prompt_builder.build_scene_image_prompt(
            scene_description=scene_description,
            include_characters=character_descriptions
        )

        # 確定輸出路徑
        if not output_filename:
            output_filename = f"scene_{scene_number:02d}.png"

        output_path = self.output_dir / output_filename

        # 生成圖片
        try:
            self.gemini_client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            logger.info(f"場景圖片生成成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"場景圖片生成失敗: {str(e)}")
            raise

    def generate_idiom_card(
        self,
        idiom: str,
        pinyin: str,
        meaning: str,
        output_filename: str = "idiom_card.png"
    ) -> str:
        """
        生成成語卡片圖片

        Args:
            idiom: 成語
            pinyin: 拼音
            meaning: 含義
            output_filename: 輸出文件名

        Returns:
            生成的圖片路徑
        """
        logger.info(f"生成成語卡片: {idiom}")

        # 成語卡片的提示詞（使用文字渲染方式，不使用 Gemini 生成的圖片）
        # 這裡我們生成一個背景圖
        prompt = f"成語卡片背景設計，傳統中國風，書法氣息，深藍色底色配金色花紋，華麗的邊框設計，古典優雅的氛圍，高質量動畫風格"

        output_path = self.output_dir / output_filename

        try:
            self.gemini_client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            logger.info(f"成語卡片背景生成成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"成語卡片生成失敗: {str(e)}")
            raise

    def generate_all_scenes(
        self,
        story_data: Dict[str, Any],
        characters: List[Dict[str, Any]]
    ) -> List[str]:
        """
        生成故事所有場景的圖片

        Args:
            story_data: 故事數據
            characters: 角色列表

        Returns:
            生成的圖片路徑列表
        """
        scenes = story_data.get("scenes", [])
        image_paths = []

        logger.info(f"開始生成 {len(scenes)} 個場景的圖片...")

        for i, scene in enumerate(scenes):
            scene_number = scene.get("scene_number", i + 1)

            # 準備這個場景要出現的角色
            include_characters = []
            for char in characters:
                char_info = {
                    "character_id": char.get("character_id"),
                    "name": char.get("name"),
                    "gemini_prompts": char.get("gemini_prompts", {}),
                    "expression": scene.get("character_expressions", {}).get(char.get("character_id")),
                    "action": scene.get("character_actions", {}).get(char.get("character_id"))
                }
                include_characters.append(char_info)

            # 生成場景圖片
            output_filename = f"scene_{scene_number:02d}.png"
            image_path = self.generate_scene_image(
                scene_description=scene.get("detailed_description", scene.get("scene_description", "")),
                include_characters=include_characters,
                output_filename=output_filename,
                scene_number=scene_number
            )

            image_paths.append(image_path)

        logger.info(f"所有場景圖片生成完成，共 {len(image_paths)} 張")
        return image_paths

    def generate_title_card(
        self,
        story_title: str,
        idiom: str,
        output_filename: str = "title_card.png"
    ) -> str:
        """
        生成標題卡片

        Args:
            story_title: 故事標題
            idiom: 成語
            output_filename: 輸出文件名

        Returns:
            生成的圖片路徑
        """
        logger.info(f"生成標題卡片: {story_title}")

        prompt = f"動畫標題画面，'{idiom}'成語故事，華麗的標題設計，傳統中國元素與現代動畫結合，色彩鮮明，高質量動畫風格"

        output_path = self.output_dir / output_filename

        try:
            self.gemini_client.generate_image(
                prompt=prompt,
                output_path=str(output_path)
            )
            logger.info(f"標題卡片生成成功: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"標題卡片生成失敗: {str(e)}")
            raise
