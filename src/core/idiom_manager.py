"""
成語管理器
負責管理和查詢成語數據
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.logger import logger


class IdiomManager:
    """成語管理器"""

    def __init__(self, data_file: str = "./data/idioms/idioms_database.json"):
        """
        初始化成語管理器

        Args:
            data_file: 成語數據文件路徑
        """
        self.data_file = Path(data_file)
        self.idioms: Dict[str, Dict[str, Any]] = {}
        self._load_idioms()
        logger.info(f"成語管理器初始化完成，加載了 {len(self.idioms)} 個成語")

    def _load_idioms(self):
        """加載成語數據"""
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                idioms_list = data.get("idioms", [])
                for idiom in idioms_list:
                    idiom_id = idiom.get("id")
                    if idiom_id:
                        self.idioms[idiom_id] = idiom
        except Exception as e:
            logger.error(f"加載成語數據失敗: {str(e)}")
            raise

    def get_idiom(self, idiom_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取成語

        Args:
            idiom_id: 成語ID

        Returns:
            成語數據，若不存在則返回 None
        """
        return self.idioms.get(idiom_id)

    def get_idiom_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        根據成語名稱獲取成語

        Args:
            name: 成語名稱

        Returns:
            成語數據
        """
        for idiom in self.idioms.values():
            if idiom.get("idiom") == name:
                return idiom
        return None

    def get_idiom_meaning(self, idiom_id: str) -> str:
        """
        獲取成語含義

        Args:
            idiom_id: 成語ID

        Returns:
            成語含義
        """
        idiom = self.get_idiom(idiom_id)
        return idiom.get("meaning", "") if idiom else ""

    def get_idiom_modern_interpretation(self, idiom_id: str) -> str:
        """
        獲取成語的現代詮釋

        Args:
            idiom_id: 成語ID

        Returns:
            現代詮釋
        """
        idiom = self.get_idiom(idiom_id)
        return idiom.get("modern_interpretation", "") if idiom else ""

    def get_idiom_origin_story(self, idiom_id: str) -> str:
        """
        獲取成語典故

        Args:
            idiom_id: 成語ID

        Returns:
            典故故事
        """
        idiom = self.get_idiom(idiom_id)
        return idiom.get("origin_story", "") if idiom else ""

    def get_suitable_characters(self, idiom_id: str) -> List[str]:
        """
        獲取適合某成語的角色ID列表

        Args:
            idiom_id: 成語ID

        Returns:
            角色ID列表
        """
        idiom = self.get_idiom(idiom_id)
        return idiom.get("suitable_characters", []) if idiom else []

    def get_idioms_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """
        根據主題獲取成語

        Args:
            theme: 主題

        Returns:
            成語列表
        """
        result = []
        for idiom in self.idioms.values():
            themes = idiom.get("story_themes", [])
            if theme in themes:
                result.append(idiom)
        return result

    def get_idioms_by_difficulty(self, difficulty: str) -> List[Dict[str, Any]]:
        """
        根據難度獲取成語

        Args:
            difficulty: 難度 (easy/medium/hard)

        Returns:
            成語列表
        """
        result = []
        for idiom in self.idioms.values():
            if idiom.get("difficulty_level") == difficulty:
                result.append(idiom)
        return result

    def get_all_idioms(self) -> List[Dict[str, Any]]:
        """
        獲取所有成語

        Returns:
            成語列表
        """
        return list(self.idioms.values())

    def get_idiom_count(self) -> int:
        """
        獲取成語總數

        Returns:
            成語數量
        """
        return len(self.idioms)

    def list_idiom_ids(self) -> List[str]:
        """
        列出所有成語ID

        Returns:
            成語ID列表
        """
        return list(self.idioms.keys())

    def get_random_idiom(self, exclude_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        隨機獲取一個成語

        Args:
            exclude_ids: 排除的成語ID列表

        Returns:
            隨機成語數據
        """
        import random

        available_idioms = [
            idiom for idiom in self.idioms.values()
            if exclude_ids is None or idiom.get("id") not in exclude_ids
        ]

        if not available_idioms:
            return None

        return random.choice(available_idioms)

    def get_usage_examples(self, idiom_id: str) -> List[str]:
        """
        獲取成語用法示例

        Args:
            idiom_id: 成語ID

        Returns:
            用法示例列表
        """
        idiom = self.get_idiom(idiom_id)
        return idiom.get("usage_examples", []) if idiom else []
