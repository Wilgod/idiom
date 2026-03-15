"""
故事生成器
負責生成完整的成語動畫故事結構
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.logger import logger
from ..utils.gemini_client import GeminiClient
from .character_manager import CharacterManager
from .idiom_manager import IdiomManager
from .prompt_builder import PromptBuilder


class StoryGenerator:
    """故事生成器"""

    def __init__(
        self,
        gemini_client: GeminiClient,
        character_manager: CharacterManager,
        idiom_manager: IdiomManager,
        prompt_builder: PromptBuilder,
        template_path: str = "./data/story_templates/modern_daily.json"
    ):
        """
        初始化故事生成器

        Args:
            gemini_client: Gemini 客戶端
            character_manager: 角色管理器
            idiom_manager: 成語管理器
            prompt_builder: 提示詞構建器
            template_path: 故事模板路徑
        """
        self.gemini_client = gemini_client
        self.character_manager = character_manager
        self.idiom_manager = idiom_manager
        self.prompt_builder = prompt_builder
        self.template = self._load_template(template_path)
        logger.info("故事生成器初始化完成")

    def _load_template(self, template_path: str) -> Dict[str, Any]:
        """加載故事模板"""
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = json.load(f)
                logger.info(f"加載故事模板: {template.get('name', template_path)}")
                return template
        except Exception as e:
            logger.error(f"加載故事模板失敗: {str(e)}")
            raise

    def generate_story(
        self,
        idiom_id: str,
        protagonist_id: Optional[str] = None,
        supporting_character_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成完整的故事

        Args:
            idiom_id: 成語ID
            protagonist_id: 主角ID，若為 None則使用默認主角
            supporting_character_ids: 配角ID列表

        Returns:
            故事結構數據
        """
        logger.info(f"開始生成故事，成語ID: {idiom_id}")

        # 獲取成語數據
        idiom = self.idiom_manager.get_idiom(idiom_id)
        if not idiom:
            raise ValueError(f"成語不存在: {idiom_id}")

        # 獲取角色
        characters = []

        # 獲取主角
        if protagonist_id:
            protagonist = self.character_manager.get_character(protagonist_id)
        else:
            protagonist = self.character_manager.get_default_protagonist()

        if protagonist:
            characters.append(protagonist)
        else:
            raise ValueError("無法獲取主角")

        # 獲取配角
        if supporting_character_ids:
            for char_id in supporting_character_ids:
                char = self.character_manager.get_character(char_id)
                if char:
                    characters.append(char)
        else:
            # 自動選擇適合的配角
            suitable_chars = self.idiom_manager.get_suitable_characters(idiom_id)
            for char_id in suitable_chars:
                if char_id != protagonist.get("character_id"):
                    char = self.character_manager.get_character(char_id)
                    if char:
                        characters.append(char)
                        if len(characters) >= 3:  # 最多3個角色
                            break

        logger.info(f"使用角色: {[c.get('name') for c in characters]}")

        # 構建故事生成提示詞
        prompt = self.prompt_builder.build_story_generation_prompt(
            idiom=idiom,
            characters=characters,
            template=self.template
        )

        # 生成故事
        logger.info("正在生成故事結構...")
        story_data = self.gemini_client.generate_json(prompt)

        # 驗證和處理故事數據
        story_data = self._process_story_data(story_data, idiom, characters)

        logger.info(f"故事生成完成: {story_data.get('story_title', '')}")
        return story_data

    def _process_story_data(
        self,
        story_data: Dict[str, Any],
        idiom: Dict[str, Any],
        characters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        處理和驗證故事數據

        Args:
            story_data: 原始故事數據
            idiom: 成語數據
            characters: 角色列表

        Returns:
            處理後的故事數據
        """
        # 確保必要字段存在
        if "scenes" not in story_data:
            story_data["scenes"] = []

        # 計算總時長
        total_duration = sum(
            scene.get("duration_seconds", 8)
            for scene in story_data["scenes"]
        )

        # 添加元數據
        story_data["metadata"] = {
            "idiom": idiom.get("idiom"),
            "idiom_id": idiom.get("id"),
            "pinyin": idiom.get("pinyin"),
            "meaning": idiom.get("meaning"),
            "total_duration": total_duration,
            "scene_count": len(story_data["scenes"]),
            "characters": [
                {
                    "id": c.get("character_id"),
                    "name": c.get("name")
                }
                for c in characters
            ]
        }

        return story_data

    def generate_scene_descriptions(
        self,
        story_data: Dict[str, Any],
        characters: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        為每個場景生成詳細描述

        Args:
            story_data: 故事數據
            characters: 角色列表

        Returns:
            帶詳細描述的場景列表
        """
        scenes = story_data.get("scenes", [])

        for scene in scenes:
            prompt = self.prompt_builder.build_scene_description_prompt(
                scene_data=scene,
                characters=characters
            )

            description = self.gemini_client.generate_text(prompt)
            scene["detailed_description"] = description

        return scenes

    def get_story_summary(self, story_data: Dict[str, Any]) -> str:
        """
        獲取故事摘要

        Args:
            story_data: 故事數據

        Returns:
            故事摘要文字
        """
        metadata = story_data.get("metadata", {})
        idiom = metadata.get("idiom", "")
        meaning = metadata.get("meaning", "")

        summary = f"""
成語: {idiom}
拼音: {metadata.get('pinyin', '')}
含義: {meaning}
時長: {metadata.get('total_duration', 0)}秒
場景數: {metadata.get('scene_count', 0)}
角色: {', '.join([c.get('name', '') for c in metadata.get('characters', [])])}

標題: {story_data.get('story_title', '')}
大綱: {story_data.get('story_outline', '')}
寓意: {story_data.get('moral', '')}
"""
        return summary
