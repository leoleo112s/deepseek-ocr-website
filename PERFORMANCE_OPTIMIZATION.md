# DeepSeek-OCR 性能优化指南（macOS 版）

## 📊 性能现状

在 macOS CPU 模式下运行 DeepSeek-OCR 时：
- **单图推理时间**: 1-5 分钟
- **首次推理**: 会更慢（模型加载和预热）
- **后续推理**: 会快一些
- **PDF 多页**: 每页约 2-3 分钟

这是**正常现象**，因为：
1. DeepSeek-OCR 是一个大型视觉-语言模型
2. macOS 没有 NVIDIA GPU，只能用 CPU
3. CPU 计算能力远低于 GPU

---

## 🚀 优化建议

### 1. 使用最小的分辨率模式

在前端选择分辨率时，优先使用 **Tiny (512×512)**：

| 模式 | 分辨率 | CPU推理时间 | 适用场景 |
|------|--------|------------|----------|
| **Tiny** | 512×512 | 1-2分钟 | ⭐ **清晰文档、简单图片（推荐）** |
| Small | 640×640 | 2-3分钟 | 普通文档 |
| Base | 1024×1024 | 3-5分钟 | 复杂文档 |
| Large | 1280×1280 | 5-10分钟 | 高精度需求（不推荐CPU使用） |
| Gundam | 动态 | 变动 | 特殊场景 |

**建议**：在 macOS CPU 模式下，始终使用 **Tiny 模式**。

---

### 2. 预处理图片

在上传前优化图片可以显著提升速度：

#### 方法 A：使用预览应用压缩

```bash
# 使用 macOS 预览应用
1. 双击打开图片
2. 菜单栏：工具 → 调整大小
3. 宽度设置为 800-1200 像素
4. 保存
```

#### 方法 B：使用命令行工具

```bash
# 安装 ImageMagick（如果没有）
brew install imagemagick

# 压缩图片到 1200px 宽度
magick convert input.png -resize 1200x output.png

# 批量处理
for img in *.png; do
  magick convert "$img" -resize 1200x "optimized_$img"
done
```

#### 方法 C：使用 Python 脚本

```python
from PIL import Image

def optimize_image(input_path, output_path, max_width=1200):
    """压缩图片到指定宽度"""
    img = Image.open(input_path)

    # 计算新尺寸
    if img.width > max_width:
        ratio = max_width / img.width
        new_size = (max_width, int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # 保存
    img.save(output_path, quality=85, optimize=True)
    print(f"✅ 优化完成: {output_path}")

# 使用示例
optimize_image("large_screenshot.png", "optimized.png")
```

---

### 3. 避免处理大型 PDF

- ❌ **不推荐**: 10+ 页的 PDF（需要 20-30 分钟）
- ⚠️ **谨慎**: 5-10 页的 PDF（需要 10-15 分钟）
- ✅ **推荐**: 1-3 页的 PDF（5-10 分钟）

**建议**: 如果有多页 PDF，可以：
1. 提取关键页面单独处理
2. 使用 PDF 分割工具拆分后分批处理

```bash
# 使用预览应用导出单页
# 打开 PDF → 选中要导出的页 → 文件 → 导出为 PDF
```

---

### 4. 关闭其他占用 CPU 的程序

在运行 OCR 推理时：
- ✅ 关闭浏览器多余标签页
- ✅ 关闭视频播放、编译任务
- ✅ 暂停其他 AI 应用（如 ChatGPT 桌面版）
- ✅ 使用活动监视器查看 CPU 占用

```bash
# 打开活动监视器
open -a "Activity Monitor"
```

---

### 5. 优化模型配置（高级）

编辑 `backend/config.yaml`：

```yaml
# 当前配置（已优化）
model:
  load_params:
    torch_dtype: "float32"  # CPU 模式最优
    device: "cpu"
    attn_implementation: "eager"  # 兼容性最好
```

**不推荐的配置**：
- ❌ `torch_dtype: "float16"` - CPU 不支持，会更慢
- ❌ `torch_dtype: "bfloat16"` - CPU 不支持
- ❌ `attn_implementation: "flash_attention_2"` - 需要 GPU

---

### 6. 使用缓存机制

相同的图片会产生相同的结果，可以：
1. 保存已处理的结果
2. 检查 `backend/outputs/` 目录的历史输出
3. 避免重复处理相同图片

---

### 7. 考虑使用云端 GPU（推荐）

如果经常需要处理大量 OCR，建议：

#### 选项 A：租用 GPU 服务器
- **Vast.ai**: 按小时租用 GPU ($0.2-0.5/小时)
- **RunPod**: GPU 云端环境
- **Paperspace**: 免费 GPU 额度

#### 选项 B：使用 Google Colab
```python
# 在 Colab 中运行 DeepSeek-OCR
# 免费提供 T4 GPU，速度提升 10-50 倍
```

#### 选项 C：使用 Hugging Face Spaces
- 可以部署为在线服务
- 免费配额包含 CPU/GPU

---

## ⏱️ 预期推理时间参考

### 单张图片（Tiny 模式）

| 图片尺寸 | 预期时间 |
|---------|---------|
| 800×600 | 1-2 分钟 |
| 1920×1080 | 2-3 分钟 |
| 3840×2160 (4K) | 4-6 分钟 |

### PDF 文档（Tiny 模式）

| 页数 | 预期时间 |
|------|---------|
| 1 页 | 2-3 分钟 |
| 3 页 | 6-9 分钟 |
| 5 页 | 10-15 分钟 |
| 10 页 | 20-30 分钟 |

---

## 🔍 监控推理进度

现在后端会显示详细的进度信息：

```
⏳ CPU 模式推理中，这可能需要 1-5 分钟，请耐心等待...
💡 提示：首次推理会更慢，后续推理会快一些
⏰ 推理开始时间: 12:34:56
⏱️  推理完成，耗时: 127.45 秒
```

在终端可以看到：
- 推理开始时间
- 推理进度
- 推理完成耗时

---

## ❓ 常见问题

### Q: 为什么第一次推理特别慢？
**A**: 模型首次加载需要初始化所有参数，后续推理会利用缓存，速度会快一些。

### Q: 能否加速到秒级？
**A**: 在 CPU 上不太可能。要达到秒级响应，需要：
- NVIDIA GPU（RTX 3060 或更高）
- 或使用量化模型（精度会下降）

### Q: 推理卡住了怎么办？
**A**:
1. 等待 5-10 分钟（可能只是慢）
2. 检查终端是否有错误信息
3. 重启后端服务
4. 检查 `backend/outputs/` 是否有部分输出

### Q: 有更快的替代方案吗？
**A**:
- 使用云端 API（如 Google Vision API、Azure OCR）
- 部署到有 GPU 的服务器
- 使用更轻量的 OCR 模型（如 PaddleOCR、EasyOCR）

---

## 📌 最佳实践总结

✅ **DO（推荐）**:
1. 使用 Tiny 模式
2. 压缩图片到 800-1200px
3. 单次只处理 1-3 页
4. 关闭其他占用 CPU 的程序
5. 耐心等待，不要中断推理

❌ **DON'T（不推荐）**:
1. 不要使用 Large/Gundam 模式
2. 不要上传 4K 超高清图片
3. 不要处理 10+ 页的 PDF
4. 不要在推理时运行其他重度应用
5. 不要频繁中断和重启

---

## 💡 未来优化方向

如果需要进一步优化，可以考虑：
1. **模型量化**: 将模型量化为 INT8（精度略降，速度提升 2-3 倍）
2. **批处理**: 一次处理多张图片（需修改代码）
3. **异步队列**: 建立任务队列系统
4. **Apple Silicon 优化**: 使用 MPS 后端（需要 PyTorch 支持）

---

**总结**: macOS CPU 模式下，DeepSeek-OCR 推理较慢是正常现象。通过优化图片大小、使用 Tiny 模式、避免大文件，可以获得可接受的性能。如需高性能，建议使用 GPU 服务器或云端服务。
