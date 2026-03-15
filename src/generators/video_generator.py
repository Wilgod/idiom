"""
視頻生成器
負責將圖片組合成視頻，添加轉場效果和字幕
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import timedelta

from ..utils.logger import logger


class VideoGenerator:
    """視頻生成器"""

    def __init__(
        self,
        output_dir: str = "./output/videos",
        fps: int = 30,
        resolution: Tuple[int, int] = (1280, 720),
        transition_duration: float = 1.0
    ):
        """
        初始化視頻生成器

        Args:
            output_dir: 輸出目錄
            fps: 幀率
            resolution: 解析度 (寬, 高)
            transition_duration: 轉場時長（秒）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.fps = fps
        self.resolution = resolution
        self.transition_duration = transition_duration

        # 嘗試導入 moviepy
        self.moviepy_available = False
        try:
            from moviepy.editor import ImageClip, CompositeVideoClip, TextClip, CompositeClip
            from moviepy.video.fx import fadein, fadeout
            self.moviepy_available = True
            logger.info("MoviePy 已可用，視頻生成功能已啟用")
        except ImportError:
            logger.warning("MoviePy 未安裝，視頻生成功能將受限")

        logger.info(f"視頻生成器初始化完成，輸出目錄: {self.output_dir}")

    def create_video_from_images(
        self,
        image_paths: List[str],
        output_filename: str,
        scene_durations: Optional[List[float]] = None,
        subtitles: Optional[List[str]] = None,
        title_image: Optional[str] = None,
        end_image: Optional[str] = None
    ) -> str:
        """
        從圖片創建視頻

        Args:
            image_paths: 圖片路徑列表
            output_filename: 輸出文件名
            scene_durations: 每個場景的時長列表（秒）
            subtitles: 字幕列表
            title_image: 標題圖片路徑
            end_image: 結尾圖片路徑

        Returns:
            生成的視頻路徑
        """
        if not self.moviepy_available:
            logger.error("MoviePy 不可用，無法生成視頻")
            raise ImportError("請安裝 moviepy: pip install moviepy")

        logger.info(f"開始從 {len(image_paths)} 張圖片創建視頻...")

        from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips

        clips = []

        # 添加標題圖片
        if title_image and os.path.exists(title_image):
            title_clip = ImageClip(title_image).set_duration(3)
            title_clip = title_clip.fadein(0.5).fadeout(0.5)
            clips.append(title_clip)

        # 處理每個場景
        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                logger.warning(f"圖片不存在，跳過: {image_path}")
                continue

            # 獲取場景時長
            duration = scene_durations[i] if scene_durations and i < len(scene_durations) else 8

            # 創建圖片剪輯
            clip = ImageClip(image_path).set_duration(duration)

            # 添加淡入淡出效果
            clip = clip.fadein(self.transition_duration).fadeout(self.transition_duration)

            # 添加字幕
            if subtitles and i < len(subtitles) and subtitles[i]:
                clip = self._add_subtitle_to_clip(clip, subtitles[i], duration)

            clips.append(clip)

        # 添加結尾圖片
        if end_image and os.path.exists(end_image):
            end_clip = ImageClip(end_image).set_duration(3)
            end_clip = end_clip.fadein(0.5).fadeout(0.5)
            clips.append(end_clip)

        if not clips:
            raise ValueError("沒有有效的剪輯")

        # 合併所有剪輯
        final_clip = concatenate_videoclips(clips, method="compose")

        # 輸出視頻
        output_path = self.output_dir / output_filename
        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )

        logger.info(f"視頻生成成功: {output_path}")
        return str(output_path)

    def _add_subtitle_to_clip(
        self,
        clip,
        subtitle_text: str,
        duration: float
    ):
        """
        為剪輯添加字幕

        Args:
            clip: 視頻剪輯
            subtitle_text: 字幕文字
            duration: 字幕時長

        Returns:
            添加字幕後的剪輯
        """
        try:
            from moviepy.editor import TextClip, CompositeClip

            # 創建字幕
            txt_clip = TextClip(
                subtitle_text,
                fontsize=36,
                color='white',
                font='Microsoft JhengHei',
                stroke_color='black',
                stroke_width=2,
                size=(self.resolution[0] - 100, None),
                method='caption'
            )

            # 設置字幕位置和時長
            txt_clip = txt_clip.set_position(('center', self.resolution[1] - 100))
            txt_clip = txt_clip.set_duration(duration)

            # 淡入淡出
            txt_clip = txt_clip.fadein(0.3).fadeout(0.3)

            # 合併
            return CompositeVideoClip([clip, txt_clip])

        except Exception as e:
            logger.warning(f"字幕添加失敗: {str(e)}")
            return clip

    def create_idiom_intro_video(
        self,
        idiom: str,
        pinyin: str,
        meaning: str,
        output_filename: str = "idiom_intro.mp4"
    ) -> str:
        """
        創建成語介紹視頻

        Args:
            idiom: 成語
            pinyin: 拼音
            meaning: 含義
            output_filename: 輸出文件名

        Returns:
            生成的視頻路徑
        """
        if not self.moviepy_available:
            logger.error("MoviePy 不可用，無法生成視頻")
            raise ImportError("請安裝 moviepy: pip install moviepy")

        logger.info(f"創建成語介紹視頻: {idiom}")

        from moviepy.editor import TextClip, CompositeVideoClip, ColorClip

        # 創建背景
        bg = ColorClip(size=self.resolution, color=(26, 26, 46), duration=5)
        bg = bg.fadein(0.5)

        # 創建成語文字
        idiom_text = TextClip(
            idiom,
            fontsize=72,
            color='#FFD700',
            font='Microsoft JhengHei',
            stroke_color='black',
            stroke_width=3
        )
        idiom_text = idiom_text.set_position(('center', 'center')).set_duration(5)

        # 創建拼音文字
        pinyin_text = TextClip(
            pinyin,
            fontsize=36,
            color='white',
            font='Microsoft JhengHei'
        )
        pinyin_text = pinyin_text.set_position(('center', self.resolution[1] // 2 + 60)).set_duration(5)

        # 創建含義文字
        meaning_text = TextClip(
            meaning,
            fontsize=28,
            color='white',
            font='Microsoft JhengHei',
            size=(self.resolution[0] - 100, None),
            method='caption'
        )
        meaning_text = meaning_text.set_position(('center', self.resolution[1] // 2 + 120)).set_duration(5)

        # 合併
        final_clip = CompositeVideoClip([bg, idiom_text, pinyin_text, meaning_text])
        final_clip = final_clip.fadeout(0.5)

        # 輸出
        output_path = self.output_dir / output_filename
        final_clip.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio=False,
            verbose=False,
            logger=None
        )

        logger.info(f"成語介紹視頻生成成功: {output_path}")
        return str(output_path)

    def add_audio_to_video(
        self,
        video_path: str,
        audio_path: str,
        output_filename: Optional[str] = None
    ) -> str:
        """
        為視頻添加音頻

        Args:
            video_path: 視頻路徑
            audio_path: 音頻路徑
            output_filename: 輸出文件名

        Returns:
            添加音頻後的視頻路徑
        """
        if not self.moviepy_available:
            logger.error("MoviePy 不可用，無法添加音頻")
            raise ImportError("請安裝 moviepy: pip install moviepy")

        logger.info(f"為視頻添加音頻: {video_path}")

        from moviepy.editor import VideoFileClip, AudioFileClip

        # 讀取視頻和音頻
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        # 設置音頻
        video = video.set_audio(audio)

        # 輸出
        if output_filename is None:
            base, ext = os.path.splitext(os.path.basename(video_path))
            output_filename = f"{base}_with_audio{ext}"

        output_path = self.output_dir / output_filename
        video.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

        logger.info(f"音頻添加成功: {output_path}")
        return str(output_path)

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        獲取視頻信息

        Args:
            video_path: 視頻路徑

        Returns:
            視頻信息
        """
        if not self.moviepy_available:
            return {}

        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(video_path)
            info = {
                "duration": clip.duration,
                "fps": clip.fps,
                "size": clip.size,
                "width": clip.w,
                "height": clip.h
            }
            clip.close()
            return info
        except Exception as e:
            logger.error(f"獲取視頻信息失敗: {str(e)}")
            return {}
