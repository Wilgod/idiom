"""
角色管理器
負責加載和管理角色數據
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.logger import logger


class CharacterManager:
    """角色管理器"""

    def __init__(self, data_dir: str = "./data/characters"):
        """
        初始化角色管理器

        Args:
            data_dir: 角色數據目錄
        """
        self.data_dir = Path(data_dir)
        self.characters: Dict[str, Dict[str, Any]] = {}
        self._load_characters()
        logger.info(f"角色管理器初始化完成，加載了 {len(self.characters)} 個角色")

    def _load_characters(self):
        """加載所有角色數據"""
        # 加載主要角色
        main_dir = self.data_dir / "main"
        if main_dir.exists():
            for file in main_dir.glob("*.json"):
                self._load_character_file(file)

        # 加載配角
        supporting_dir = self.data_dir / "supporting"
        if supporting_dir.exists():
            for file in supporting_dir.glob("*.json"):
                self._load_character_file(file)

    def _load_character_file(self, file_path: Path):
        """加載單個角色文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                character = json.load(f)
                character_id = character.get("character_id")
                if character_id:
                    self.characters[character_id] = character
                    logger.debug(f"加載角色: {character_id} - {character.get('name')}")
        except Exception as e:
            logger.error(f"加載角色文件失敗 {file_path}: {str(e)}")

    def get_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取角色

        Args:
            character_id: 角色ID

        Returns:
            角色數據，若不存在則返回 None
        """
        return self.characters.get(character_id)

    def get_character_name(self, character_id: str) -> str:
        """
        獲取角色名稱

        Args:
            character_id: 角色ID

        Returns:
            角色名稱
        """
        character = self.get_character(character_id)
        return character.get("name", character_id) if character else character_id

    def get_characters_by_type(self, role_type: str) -> List[Dict[str, Any]]:
        """
        根據角色類型獲取角色

        Args:
            role_type: 角色類型 (protagonist/supporting)

        Returns:
            角色列表
        """
        return [
            char for char in self.characters.values()
            if char.get("role_type") == role_type
        ]

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """
        獲取所有角色

        Returns:
            角色列表
        """
        return list(self.characters.values())

    def get_character_prompt(
        self,
        character_id: str,
        prompt_type: str = "base"
    ) -> str:
        """
        獲取角色的 Gemini 提示詞

        Args:
            character_id: 角色ID
            prompt_type: 提示詞類型 (base/expressions/actions)

        Returns:
            提示詞文本
        """
        character = self.get_character(character_id)
        if not character:
            logger.warning(f"角色不存在: {character_id}")
            return ""

        gemini_prompts = character.get("gemini_prompts", {})

        if prompt_type == "base":
            return gemini_prompts.get("base", "")

        if "." in prompt_type:
            # 例如: expressions.happy 或 actions.running
            parts = prompt_type.split(".")
            return gemini_prompts.get(parts[0], {}).get(parts[1], "")

        return gemini_prompts.get(prompt_type, "")

    def get_character_expression_prompt(
        self,
        character_id: str,
        expression: str
    ) -> str:
        """
        獲取角色的表情提示詞

        Args:
            character_id: 角色ID
            expression: 表達類型 (happy/sad/thinking等)

        Returns:
            表情提示詞
        """
        return self.get_character_prompt(character_id, f"expressions.{expression}")

    def get_character_action_prompt(
        self,
        character_id: str,
        action: str
    ) -> str:
        """
        獲取角色的動作提示詞

        Args:
            character_id: 角色ID
            action: 動作類型 (reading/running/standing等)

        Returns:
            動作提示詞
        """
        return self.get_character_prompt(character_id, f"actions.{action}")

    def get_character_tags(self, character_id: str) -> List[str]:
        """
        獲取角色的標籤

        Args:
            character_id: 角色ID

        Returns:
            標籤列表
        """
        character = self.get_character(character_id)
        return character.get("tags", []) if character else []

    def get_default_protagonist(self) -> Optional[Dict[str, Any]]:
        """
        獲取默認主角

        Returns:
            主角角色數據
        """
        protagonists = self.get_characters_by_type("protagonist")
        return protagonists[0] if protagonists else None

    def list_character_ids(self) -> List[str]:
        """
        列出所有角色ID

        Returns:
            角色ID列表
        """
        return list(self.characters.keys())
