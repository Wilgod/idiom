"""
提示詞構建器
負責根據模板和上下文構建各種類型的提示詞
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..utils.logger import logger


class PromptBuilder:
    """提示詞構建器"""

    def __init__(self, config_file: str = "./config/prompt_templates.yaml"):
        """
        初始化提示詞構建器

        Args:
            config_file: 提示詞配置文件路徑
        """
        self.config_file = Path(config_file)
        self.templates: Dict[str, Any] = {}
        self._load_templates()
        logger.info("提示詞構建器初始化完成")

    def _load_templates(self):
        """加載提示詞模板"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.templates = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加載提示詞模板失敗: {str(e)}")
            self.templates = {}

    def build_character_image_prompt(
        self,
        character_prompt: str,
        expression: Optional[str] = None,
        action: Optional[str] = None,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None
    ) -> str:
        """
        構建角色圖片提示詞

        Args:
            character_prompt: 角色基礎提示詞
            expression: 表情類型
            action: 動作類型
            style: 風格描述
            negative_prompt: 負面提示詞

        Returns:
            完整的圖片提示詞
        """
        parts = [character_prompt]

        # 添加表情
        if expression:
            expressions = self.templates.get("image_generation", {}).get("expressions", {})
            expr_prompt = expressions.get(expression, "")
            if expr_prompt:
                parts.append(expr_prompt)

        # 添加動作
        if action:
            actions = self.templates.get("image_generation", {}).get("actions", {})
            action_prompt = actions.get(action, "")
            if action_prompt:
                parts.append(action_prompt)

        # 添加風格
        if style:
            parts.append(style)
        else:
            style_prompt = self.templates.get("image_generation", {}).get("character_base", {}).get("style", "")
            parts.append(style_prompt)

        # 添加質量標籤
        quality_tags = self.templates.get("image_generation", {}).get("character_base", {}).get("quality_tags", "")
        parts.append(quality_tags)

        prompt = "，".join(parts)
        logger.debug(f"角色圖片提示詞: {prompt[:100]}...")
        return prompt

    def build_scene_image_prompt(
        self,
        scene_description: str,
        style: Optional[str] = None,
        include_characters: Optional[List[str]] = None,
        negative_prompt: Optional[str] = None
    ) -> str:
        """
        構建場景圖片提示詞

        Args:
            scene_description: 場景描述
            style: 風格描述
            include_characters: 包含的角色描述
            negative_prompt: 負面提示詞

        Returns:
            完整的圖片提示詞
        """
        parts = []

        # 添加場景描述
        parts.append(scene_description)

        # 添加角色
        if include_characters:
            parts.append("，".join(include_characters))

        # 添加風格
        if style:
            parts.append(style)
        else:
            style_prompt = self.templates.get("image_generation", {}).get("scene_base", {}).get("style", "")
            parts.append(style_prompt)

        # 添加質量標籤
        quality_tags = self.templates.get("image_generation", {}).get("scene_base", {}).get("quality_tags", "")
        parts.append(quality_tags)

        prompt = "，".join(parts)
        logger.debug(f"場景圖片提示詞: {prompt[:100]}...")
        return prompt

    def build_story_generation_prompt(
        self,
        idiom: Dict[str, Any],
        characters: List[Dict[str, Any]],
        template: Dict[str, Any]
    ) -> str:
        """
        構建故事生成提示詞

        Args:
            idiom: 成語數據
            characters: 角色列表
            template: 故事模板

        Returns:
            故事生成提示詞
        """
        system_prompt = self.templates.get("text_generation", {}).get("story_generation", {}).get(
            "system_prompt",
            "你是一個專業的兒童故事編劇。"
        )

        # 構建提示詞
        prompt = f"""# 任務
{system_prompt}

## 成語信息
- 成語: {idiom.get('idiom', '')}
- 拼音: {idiom.get('pinyin', '')}
- 意思: {idiom.get('meaning', '')}
- 現代詮釋: {idiom.get('modern_interpretation', '')}

## 角色
"""
        for char in characters:
            prompt += f"- {char.get('name', '')}: {', '.join(char.get('personality', []))}\n"

        prompt += f"""
## 故事結構要求
故事需要遵循「起承轉合」結構：

1. **起 (起始)**: 介紹主角和背景，建立故事情境
   - 時長: 約{template.get('structure', {}).get('起', {}).get('duration_seconds', 15)}秒
   - 場景數: {template.get('structure', {}).get('起', {}).get('scene_count', 2)}

2. **承 (發展)**: 主角遇到問題或情況，故事發展
   - 時長: 約{template.get('structure', {}).get('承', {}).get('duration_seconds', 20)}秒
   - 場景數: {template.get('structure', {}).get('承', {}).get('scene_count', 3)}

3. **轉 (轉折)**: 成語應用的關鍵時刻，故事高潮
   - 時長: 約{template.get('structure', {}).get('轉', {}).get('duration_seconds', 25)}秒
   - 場景數: {template.get('structure', {}).get('轉', {}).get('scene_count', 3)}

4. **合 (結尾)**: 問題解決，主角學到教訓，故事結尾
   - 時長: 約{template.get('structure', {}).get('合', {}).get('duration_seconds', 20)}秒
   - 場景數: {template.get('structure', {}).get('合', {}).get('scene_count', 2)}

## 輸出要求
請生成一個完整的動畫故事腳本，包括：
1. 故事大綱（簡短描述）
2. 每個場景的詳細描述（{template.get('settings', {}).get('total_scene_count', 10)}個場景）
3. 每個場景需要包含：
   - 場景描述
   - 角色動作和表情
   - 對話（可選）
   - 字幕文字

## 重要提醒
- 故事要生動有趣，適合兒童觀看
- 成語的含義要自然地融入故事中
- 故事結尾要清楚說明成語的意思和教訓

請以 JSON 格式輸出，包含以下字段：
{{
    "story_title": "故事標題",
    "story_outline": "故事大綱",
    "moral": "故事寓意",
    "scenes": [
        {{
            "scene_number": 1,
            "phase": "起/承/轉/合",
            "scene_description": "場景描述",
            "character_actions": "角色動作",
            "subtitle": "字幕文字",
            "duration_seconds": 8
        }}
    ]
}}
"""
        return prompt

    def build_scene_description_prompt(
        self,
        scene_data: Dict[str, Any],
        characters: List[Dict[str, Any]]
    ) -> str:
        """
        構建場景描述生成提示詞

        Args:
            scene_data: 場景數據
            characters: 角色列表

        Returns:
            場景描述提示詞
        """
        system_prompt = self.templates.get("text_generation", {}).get("scene_description", {}).get(
            "system_prompt",
            "你是一個專業的動畫分鏡設計師。"
        )

        prompt = f"""# 任務
{system_prompt}

## 場景信息
- 場景編號: {scene_data.get('scene_number', '')}
- 階段: {scene_data.get('phase', '')}
- 描述: {scene_data.get('scene_description', '')}
- 角色動作: {scene_data.get('character_actions', '')}

## 角色
"""
        for char in characters:
            prompt += f"- {char.get('name', '')}: {char.get('appearance', {}).get('clothing', {}).get('style', '')}\n"

        prompt += """
## 請生成
請生成一個生動的動畫場景描述，包含：
1. 詳細的環境描述
2. 光線和氛圍
3. 角色的位置和姿勢
4. 表情和動作

請直接輸出場景描述文字，不需要 JSON 格式。
"""
        return prompt
