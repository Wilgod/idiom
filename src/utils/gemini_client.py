"""
Gemini API 客戶端封裝
提供文本生成和圖片生成功能
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from PIL import Image
import io

from .logger import logger


class GeminiClient:
    """Gemini API 客戶端"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 Gemini 客戶端

        Args:
            api_key: Gemini API Key，若為 None則從環境變量讀取
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                raise ValueError("請在 .env 文件中設置 GEMINI_API_KEY")

        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.image_model = "imagen-3.0-generate-002"
        logger.info("Gemini 客戶端初始化完成")

    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        max_tokens: int = 2048
    ) -> str:
        """
        生成文本

        Args:
            prompt: 提示詞
            temperature: 溫度參數
            top_p: top_p 參數
            top_k: top_k 參數
            max_tokens: 最大輸出 tokens

        Returns:
            生成的文本
        """
        try:
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "max_output_tokens": max_tokens,
            }

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            logger.info("文本生成成功")
            return response.text

        except Exception as e:
            logger.error(f"文本生成失敗: {str(e)}")
            raise

    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式的文本

        Args:
            prompt: 提示詞
            temperature: 溫度參數
            top_p: top_p 參數
            max_tokens: 最大輸出 tokens

        Returns:
            解析後的 JSON 對象
        """
        # 添加 JSON 格式要求
        json_prompt = f"{prompt}\n\n請以 JSON 格式輸出。"

        try:
            response_text = self.generate_text(
                json_prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )

            # 嘗試解析 JSON
            # 去除可能的markdown標記
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            result = json.loads(response_text.strip())
            logger.info("JSON 解析成功")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {str(e)}")
            logger.error(f"原始響應: {response_text}")
            raise
        except Exception as e:
            logger.error(f"JSON 生成失敗: {str(e)}")
            raise

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        number_of_images: int = 1,
        aspect_ratio: str = "1:1"
    ) -> List[str]:
        """
        生成圖片

        Args:
            prompt: 圖片生成提示詞
            output_path: 輸出路徑，若為 None則不保存
            number_of_images: 生成圖片數量
            aspect_ratio: 寬高比

        Returns:
            生成的圖片路徑列表
        """
        try:
            # 使用 image generation API
            result = genai.generate_image(
                model=self.image_model,
                prompt=prompt,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio
            )

            output_paths = []

            if output_path:
                # 確保目錄存在
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            for i, generated_image in enumerate(result.images):
                if output_path:
                    # 處理路徑
                    if number_of_images > 1:
                        base, ext = os.path.splitext(output_path)
                        img_path = f"{base}_{i+1}{ext}"
                    else:
                        img_path = output_path

                    # 保存圖片
                    generated_image.save(img_path)
                    output_paths.append(img_path)
                    logger.info(f"圖片已保存: {img_path}")
                else:
                    output_paths.append(generated_image)

            logger.info(f"成功生成 {len(output_paths)} 張圖片")
            return output_paths

        except Exception as e:
            logger.error(f"圖片生成失敗: {str(e)}")
            raise

    def generate_image_with_retry(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> List[str]:
        """
        帶重試的圖片生成

        Args:
            prompt: 圖片生成提示詞
            output_path: 輸出路徑
            max_retries: 最大重試次數
            **kwargs: 其他參數

        Returns:
            生成的圖片路徑列表
        """
        for attempt in range(max_retries):
            try:
                return self.generate_image(prompt, output_path, **kwargs)
            except Exception as e:
                logger.warning(f"圖片生成嘗試 {attempt + 1} 失敗: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                logger.info("等待 2 秒後重試...")
                import time
                time.sleep(2)

        return []
