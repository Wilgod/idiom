"""
分鏡圖生成器
生成包含所有場景的3x3網格分鏡圖
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap


class StoryboardGenerator:
    """分鏡圖生成器"""

    def __init__(self, storyboard_path: str):
        """
        初始化

        Args:
            storyboard_path: 分鏡JSON文件路徑
        """
        with open(storyboard_path, 'r', encoding='utf-8') as f:
            self.storyboard = json.load(f)

        self.scenes = self.storyboard['scenes']
        self.total_scenes = self.storyboard['total_scenes']
        self.story_title = self.storyboard['story_title']

    def create_text_image(self, scene: dict, width: int = 800, height: int = 600) -> Image.Image:
        """
        創建場景文字描述圖片（當沒有實際圖片時使用）

        Args:
            scene: 場景數據
            width: 圖片寬度
            height: 圖片高度

        Returns:
            PIL Image對象
        """
        # 創建圖片
        img = Image.new('RGB', (width, height), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)

        # 嘗試加載字體，如果失敗則使用默認字體
        try:
            # Windows 繁體中文字體
            title_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 24)
            content_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 16)
            small_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 14)
        except:
            # 使用默認字體
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # 場景編號和名稱
        scene_num = f"場景 {scene['scene_number']}"
        scene_name = scene['name']
        phase = f"【{scene['phase']}】"
        duration = f"時長: {scene['duration']}秒"

        # 繪製標題區域背景
        draw.rectangle([0, 0, width, 80], fill=(70, 130, 180))

        # 繪製場景編號
        draw.text((20, 10), scene_num, fill='white', font=title_font)
        draw.text((150, 10), phase, fill='yellow', font=title_font)

        # 繪製場景名稱
        draw.text((20, 45), scene_name, fill='white', font=content_font)

        # 繪製時長（右上角）
        draw.text((width - 120, 30), duration, fill='lightyellow', font=small_font)

        # 內容區域
        y_offset = 100
        line_height = 25

        # 場景描述
        desc_label = "場景描述:"
        draw.text((20, y_offset), desc_label, fill='black', font=content_font)
        y_offset += line_height

        # 自動換行
        wrapped_desc = textwrap.wrap(scene['description'], width=35)
        for line in wrapped_desc:
            draw.text((30, y_offset), line, fill='darkgray', font=small_font)
            y_offset += line_height - 5

        y_offset += 10

        # 鏡頭角度
        camera_label = f"鏡頭: {scene['camera_angle']}"
        draw.text((20, y_offset), camera_label, fill='darkblue', font=small_font)
        y_offset += line_height

        # 情緒
        mood_label = f"情緒: {scene['mood']}"
        draw.text((20, y_offset), mood_label, fill='darkgreen', font=small_font)
        y_offset += line_height + 5

        # 關鍵元素
        elements_label = "關鍵元素:"
        draw.text((20, y_offset), elements_label, fill='black', font=small_font)
        y_offset += line_height - 5

        for element in scene['key_elements'][:5]:  # 只顯示前5個
            elem_text = f"• {element}"
            draw.text((30, y_offset), elem_text, fill='gray', font=small_font)
            y_offset += line_height - 8

        # 底部提示
        prompt_preview = "Nano Banana Prompt (英文提示詞已包含)"
        draw.rectangle([0, height - 30, width, height], fill=(100, 100, 100))
        draw.text((20, height - 25), prompt_preview, fill='white', font=small_font)

        return img

    def create_grid_storyboard(self, output_path: str = None) -> str:
        """
        創建3x3網格分鏡圖

        Args:
            output_path: 輸出路徑，如果為None則使用默認路徑

        Returns:
            輸出文件路徑
        """
        # 網格設置
        grid_size = 3
        cell_width = 800
        cell_height = 600
        padding = 20

        # 計算總畫布大小
        total_width = cell_width * grid_size + padding * (grid_size + 1)
        total_height = cell_height * grid_size + padding * (grid_size + 1) + 100  # 額外空間給標題

        # 創建畫布
        canvas = Image.new('RGB', (total_width, total_height), color=(50, 50, 60))
        draw = ImageDraw.Draw(canvas)

        # 加載字體
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 36)
        except:
            title_font = ImageFont.load_default()

        # 繪製標題
        title = f"{self.story_title} - 分鏡設計"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((total_width - title_width) // 2, 30),
            title,
            fill='white',
            font=title_font
        )

        # 放置場景到網格中
        for idx, scene in enumerate(self.scenes):
            # 計算網格位置
            row = idx // grid_size
            col = idx % grid_size

            # 計算座標
            x = padding + col * (cell_width + padding)
            y = 100 + padding + row * (cell_height + padding)

            # 創建場景圖片
            scene_img = self.create_text_image(scene, cell_width, cell_height)

            # 粘貼到畫布
            canvas.paste(scene_img, (x, y))

        # 在第9格添加總結信息（如果有）
        if self.total_scenes < 9:
            summary_x = padding + 2 * (cell_width + padding)
            summary_y = 100 + padding + 2 * (cell_height + padding)

            # 創建總結卡片
            summary_img = Image.new('RGB', (cell_width, cell_height), color=(70, 130, 180))
            summary_draw = ImageDraw.Draw(summary_img)

            try:
                summary_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 20)
                info_font = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 16)
            except:
                summary_font = ImageFont.load_default()
                info_font = ImageFont.load_default()

            # 總結信息
            info_lines = [
                "故事總覽",
                "",
                f"總場景數: {self.total_scenes}",
                f"網格布局: {self.storyboard.get('grid_layout', '3x3')}",
                "",
                "主要角色:",
                f"• {self.storyboard['characters']['protagonist']['name']}",
            ]

            for support in self.storyboard['characters']['supporting']:
                info_lines.append(f"• {support['name']}")

            info_lines.extend([
                "",
                "視覺風格:",
                f"• {self.storyboard['visual_style']['art_style']}",
                "",
                "特色:",
                "• 現代少年漫畫風格",
                "• 鮮豔色彩",
                "• 誇張特效"
            ])

            y_text = 50
            for line in info_lines:
                if line.startswith("故事") or line.startswith("主要") or line.startswith("視覺"):
                    summary_draw.text((40, y_text), line, fill='yellow', font=summary_font)
                else:
                    summary_draw.text((40, y_text), line, fill='white', font=info_font)
                y_text += 30

            canvas.paste(summary_img, (summary_x, summary_y))

        # 保存文件
        if output_path is None:
            output_dir = Path("./output")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{self.story_title}_分鏡圖.png"

        canvas.save(output_path, 'PNG', quality=95)

        return str(output_path)

    def generate_scene_images(self, output_dir: str = "./output/scenes"):
        """
        生成單獨的場景圖片

        Args:
            output_dir: 輸出目錄

        Returns:
            生成的圖片路徑列表
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_paths = []

        for scene in self.scenes:
            img = self.create_text_image(scene)
            filename = f"場景{scene['scene_number']:02d}_{scene['name']}.png"
            filepath = output_path / filename
            img.save(filepath, 'PNG')
            image_paths.append(str(filepath))

        return image_paths


def main():
    """主演示函數"""
    print("=" * 70)
    print("分鏡圖生成器")
    print("=" * 70)
    print()

    # 加載分鏡數據
    storyboard_path = "./output/宇宙袋鼠籃球災難_分鏡設計.json"

    if not Path(storyboard_path).exists():
        print(f"錯誤: 找不到分鏡文件 {storyboard_path}")
        return

    print(f"加載分鏡數據: {storyboard_path}")

    # 創建生成器
    generator = StoryboardGenerator(storyboard_path)

    print(f"\n故事標題: {generator.story_title}")
    print(f"總場景數: {generator.total_scenes}")

    # 生成3x3網格分鏡圖
    print("\n正在生成3x3網格分鏡圖...")
    grid_path = generator.create_grid_storyboard()
    print(f"[完成] 網格分鏡圖已生成: {grid_path}")

    # 生成單獨的場景圖片
    print("\n正在生成單獨的場景圖片...")
    scene_paths = generator.generate_scene_images()
    print(f"[完成] 已生成 {len(scene_paths)} 個場景圖片到 ./output/scenes/")

    print()
    print("=" * 70)
    print("分鏡圖生成完成！")
    print("=" * 70)
    print()
    print("提示:")
    print("- 網格分鏡圖適合整體預覽和規劃")
    print("- 單獨場景圖片可用於視頻製作")
    print("- 每個場景都包含完整的 nano banana prompt（存儲在JSON中）")
    print("- 可以使用 Gemini API 根據 prompt 生成實際場景圖片")


if __name__ == "__main__":
    main()