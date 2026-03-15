# 畫蛇添足 - 故事創建指南

本指南詳細說明如何使用系統創建「畫蛇添足」成語動畫故事。

## 一、快速開始

### 方法 1: 使用演示腳本（推薦）

```bash
# 運行演示腳本，會自動生成完整故事
python demo_story_generation.py
```

這個腳本會：
1. 自動連接 Gemini API
2. 生成完整的故事結構
3. 生成詳細的場景描述
4. 顯示分鏡表和時間分配
5. 保存 JSON 結果到 `output/畫蛇添足_story.json`

### 方法 2: 使用命令行

```bash
# 列出所有成語
python -m src.main --list-idioms

# 生成畫蛇添足動畫
python -m src.main --idiom idiom_001

# 指定主角和配角
python -m src.main --idiom idiom_001 --protagonist xiaoming

# 只生成圖片，不生成視頻
python -m src.main --idiom idiom_001 --no-video
```

### 方法 3: 使用 Python 代碼

```python
from src.main import IdiomAnimationGenerator

# 初始化生成器
generator = IdiomAnimationGenerator()

# 生成故事（只生成結構，不生成圖片和視頻）
result = generator.generate_animation(
    idiom_id='idiom_001',
    protagonist_id='xiaoming',
    supporting_character_ids=['lily', 'laoshi'],
    generate_video=False  # 只生成故事結構
)

# 獲取故事數據
story = result['story_structure']

# 打印故事標題
print(f"標題: {story['story_title']}")
print(f"時長: {story['metadata']['total_duration']} 秒")
print(f"場景數: {story['metadata']['scene_count']} 個")

# 查看每個場景
for scene in story['scenes']:
    print(f"\n場景 {scene['scene_number']}: {scene['phase']}")
    print(f"描述: {scene['scene_description']}")
    print(f"時長: {scene['duration_seconds']} 秒")
```

## 二、故事結構詳解

### 起承轉合結構

故事遵循傳統的「起承轉合」結構，總時長約 78-80 秒：

```
┌─────────────────────────────────────────┐
│  起 (起始) - 15 秒，2 場景              │
│  介紹背景、角色、情境                   │
├─────────────────────────────────────────┤
│  承 (發展) - 20 秒，3 場景              │
│  故事發展，問題出現                     │
├─────────────────────────────────────────┤
│  轉 (轉折) - 25 秒，3 場景              │
│  高潮時刻，成語展現                     │
├────────────────────────��────────────────┤
│  合 (結尾) - 20 秒，2 場景              │
│  問題解決，寓意總結                     │
└─────────────────────────────────────────┘
```

### 場景詳細內容（畫蛇添足示例）

#### 【起 - 起始階段】(場景 1-2)

**場景 1 (8秒)**
- 情境：教室場景，老師宣布作業
- 角色：小明認真聽講
- 目的：建立故事背景

**場景 2 (7秒)**
- 情境：開始創作
- 角色：小明選擇畫蛇
- 目的：引出主角行動

#### 【承 - 發展階段】(場景 3-5)

**場景 3 (7秒)**
- 情境：畫好蛇身體
- 角色：小明滿意作品
- 目的：展示初步成果

**場景 4 (6秒)**
- 情境：覺得需要改進
- 角色：小明思考創意
- 目的：醞釀錯誤決定

**場景 5 (7秒)**
- 情境：添加蛇腳
- 角色：小明自以為完美
- 目的：執行錯誤決定

#### 【轉 - 轉折階段】(場景 6-8)

**場景 6 (7秒)**
- 情境：老師檢查作業
- 角色：小明展示作品
- 目的：準備揭示錯誤

**場景 7 (8秒)**
- 情境：老師指出錯誤
- 角色：小明驚訝
- 目的：揭示真相

**場景 8 (8秒)**
- 情境：恍然大悟
- 角色：小明尷尬
- 目的：理解錯誤

#### 【合 - 結尾階段】(場景 9-10)

**場景 9 (8秒)**
- 情境：老師教導
- 角色：小明學習
- 目的：獲得教訓

**場景 10 (12秒)**
- 情境：成語卡片
- 內容：總結寓意
- 目的：教育總結

## 三、時間分配優化

### 標準時間分配

```python
# 可以在 config/config.yaml 中調整
story:
  total_duration: 80  # 總時長
  default_scene_duration: 8  # 默認場景時長

# 或者在故事模板中調整
structure:
  起:
    duration_seconds: 15
    scene_count: 2
  承:
    duration_seconds: 20
    scene_count: 3
  轉:
    duration_seconds: 25
    scene_count: 3
  合:
    duration_seconds: 20
    scene_count: 2
```

### 自定義時間分配

如果需要調整某個場景的時長，可以在生成後修改 JSON：

```python
# 修改場景時長
story_data['scenes'][0]['duration_seconds'] = 10  # 第一個場景改為10秒

# 重新計算總時長
total = sum(scene['duration_seconds'] for scene in story_data['scenes'])
story_data['metadata']['total_duration'] = total
```

## 四、自定義故事內容

### 修改故事大綱

可以直接編輯生成的 JSON 文件：

```json
{
  "story_title": "小明的美術作業",  // 可修改標題
  "story_outline": "...",  // 可修改大綱
  "moral": "...",  // 可修改寓意
  "scenes": [...]  // 可修改每個場景
}
```

### 調整場景描述

```json
{
  "scene_number": 1,
  "phase": "起",
  "scene_description": "教室裡...",  // 場景描述
  "character_actions": "小明坐在...",  // 角色動作
  "subtitle": "今天我們要畫一幅動物畫",  // 字幕
  "duration_seconds": 8,  // 時長
  "detailed_description": "明亮的教室..."  // 詳細描述（用於生成圖片）
}
```

### 更換角色

```python
# 使用不同角色組合
result = generator.generate_animation(
    idiom_id='idiom_001',
    protagonist_id='xiaoming',  # 主角
    supporting_character_ids=['yeye']  # 配角換成爺爺
)
```

這樣可以創造不同的故事版本，例如：
- 版本1: 小明 + 王老師 + 小麗（學校場景）
- 版本2: 小明 + 爺爺（家庭場景）

## 五、進階功能

### 1. 批量生成多個成語

```python
# 批量生成前3個成語
results = generator.batch_generate(
    idiom_ids=['idiom_001', 'idiom_002', 'idiom_003']
)

# 查看結果
for result in results:
    if result['success']:
        print(f"✓ {result['idiom']['idiom']}")
    else:
        print(f"✗ {result['idiom_id']}: {result['error']}")
```

### 2. 只生成圖片不生成視頻

```python
result = generator.generate_animation(
    idiom_id='idiom_001',
    generate_video=False  # 只生成圖片
)

# 圖片保存在 output/images/
```

### 3. 修改提示詞模板

編輯 `config/prompt_templates.yaml` 可以自定義：

```yaml
# 修改動畫風格
image_generation:
  character_base:
    style: "現代2D動畫風格，參考日本動漫..."
    quality_tags: "高質量，細節豐富..."

# 修改故事生成提示
text_generation:
  story_generation:
    system_prompt: "你是一個專業的兒童故事編劇..."
```

## 六、輸出文件

### 故事 JSON 結構

生成的故事會保存為 JSON 格式，包含：

```json
{
  "story_title": "故事標題",
  "story_outline": "故事大綱",
  "moral": "寓意",
  "scenes": [
    {
      "scene_number": 1,
      "phase": "起/承/轉/合",
      "scene_description": "場景描述",
      "character_actions": "角色動作",
      "subtitle": "字幕文字",
      "duration_seconds": 8,
      "detailed_description": "詳細描述"
    }
  ],
  "metadata": {
    "idiom": "畫蛇添足",
    "pinyin": "huà shé tiān zú",
    "meaning": "含義",
    "total_duration": 78,
    "scene_count": 10,
    "characters": [...]
  }
}
```

### 使用 JSON 生成視頻

```python
# 讀取已保存的故事 JSON
import json
with open('output/畫蛇添足_story.json', 'r', encoding='utf-8') as f:
    story_data = json.load(f)

# 生成圖片
from src.generators.image_generator import ImageGenerator
# ... 初始化 ...
image_paths = image_generator.generate_all_scenes(story_data, characters)

# 生成視頻
from src.generators.video_generator import VideoGenerator
# ... 初始化 ...
video_path = video_generator.create_video_from_images(
    image_paths=image_paths,
    output_filename='畫蛇添足.mp4',
    scene_durations=[s['duration_seconds'] for s in story_data['scenes']],
    subtitles=[s.get('subtitle', '') for s in story_data['scenes']]
)
```

## 七、常見問題

### Q1: 如何讓故事更長？

**方法 1**: 增加場景數量
```python
# 在故事模板中增加場景數
structure:
  起:
    scene_count: 3  # 從 2 增加到 3
```

**方法 2**: 增加每個場景的時長
```json
{
  "duration_seconds": 10  // 從 8 秒增加到 10 秒
}
```

### Q2: 如何創建不同風格的故事？

修改提示詞模板：
```yaml
# config/prompt_templates.yaml
image_generation:
  character_base:
    style: "水彩畫風格"  # 改變風格
```

或修改故事生成提示：
```yaml
text_generation:
  story_generation:
    system_prompt: "你是一個擅長編寫幽默故事的編劇..."
```

### Q3: 如何保存中間結果？

```python
import json

# 保存故事結構
with open('story.json', 'w', encoding='utf-8') as f:
    json.dump(story_data, f, ensure_ascii=False, indent=2)

# 讀取並繼續
with open('story.json', 'r', encoding='utf-8') as f:
    story_data = json.load(f)
```

## 八、最佳實踐

1. **先生成故事結構，滿意後再生成圖片和視頻**
   ```python
   result = generator.generate_animation(idiom_id, generate_video=False)
   # 檢查 story_structure 是否滿意
   # 滿意後再生成圖片和視頻
   ```

2. **保存中間結果**
   ```python
   # 每個階段都保存 JSON
   # 方便調整和重用
   ```

3. **批量生成時使用 try-except**
   ```python
   for idiom_id in idiom_ids:
       try:
           result = generator.generate_animation(idiom_id)
       except Exception as e:
           print(f"Error: {e}")
           continue
   ```

4. **測試不同角色組合**
   ```python
   # 嘗試不同的角色搭配
   # 創造不同風格的故事
   ```

## 九、示例輸出

運行 `python demo_story_generation.py` 後，您會看到：

```
======================================================================
  故事基本信息
======================================================================

成語: 畫蛇添足
拼音: huà shé tiān zú
含義: 比喻做了多餘的事，反而不恰當
總時長: 78 秒
場景數: 10 個
角色: 小明, 小麗, 王老師

======================================================================
  故事內容
======================================================================

標題: 小明的美術作業

大綱:
  小明在美術課上畫了一條漂亮的蛇...

寓意:
  做事要恰到好處，過度追求完美反而會畫蛇添足...

======================================================================
  詳細分鏡表
======================================================================

【場景 1】- 起階段
┌──────────────────────────────────────────────────────────────────┐
│ 時長: 8 秒                                                       │
├──────────────────────────────────────────────────────────────────┤
│ 場景描述:
│   教室裡，陽光透過窗戶灑進來，黑板上寫著「美術課」...│
├──────────────────────────────────────────────────────────────────┤
│ 角色動作:
│   小明坐在課桌前，雙手撐著下巴，專注地聽講...│
├──────────────────────────────────────────────────────────────────┤
│ 字幕:
│   今天我們要畫一幅動物畫                                         │
└──────────────────────────────────────────────────────────────────┘
...
```

---

**需要幫助？**
- 查看 README.md 了解更多信息
- 檢查 .env 文件中的 API Key 設置
- 運行 `python -m src.main --help` 查看命令幫助