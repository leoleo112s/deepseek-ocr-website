# macOS FlashAttention2 修复指南

## 问题描述
在 macOS 上运行 DeepSeek-OCR 时，可能会遇到 FlashAttention2 错误，因为该库不支持 macOS 系统。

## 解决方案

### 方案一：修改模型配置文件（推荐）

如果代码修改后仍然报错，需要直接修改模型目录中的配置文件：

1. 打开模型配置文件：
   ```bash
   open /Users/towns/models/DeepSeek-OCR/config.json
   ```

2. 查找并修改以下字段（如果存在）：
   ```json
   {
     "_attn_implementation": "flash_attention_2"
   }
   ```

   改为：
   ```json
   {
     "_attn_implementation": "eager"
   }
   ```

3. 或者直接删除 `_attn_implementation` 字段

4. 保存文件后重新启动后端

### 方案二：使用命令行修改（快速）

在终端执行以下命令：

```bash
# 备份原配置文件
cp /Users/towns/models/DeepSeek-OCR/config.json /Users/towns/models/DeepSeek-OCR/config.json.backup

# 修改配置（将 flash_attention_2 替换为 eager）
sed -i '' 's/"flash_attention_2"/"eager"/g' /Users/towns/models/DeepSeek-OCR/config.json

# 验证修改
grep "attn_implementation" /Users/towns/models/DeepSeek-OCR/config.json
```

### 方案三：Python 脚本自动修改

创建一个临时脚本 `fix_model_config.py`：

```python
import json

config_path = "/Users/towns/models/DeepSeek-OCR/config.json"

# 读取配置
with open(config_path, 'r') as f:
    config = json.load(f)

# 备份
with open(config_path + '.backup', 'w') as f:
    json.dump(config, f, indent=2)

# 修改 attention 实现
if '_attn_implementation' in config:
    print(f"原配置: _attn_implementation = {config['_attn_implementation']}")
    config['_attn_implementation'] = 'eager'
    print(f"新配置: _attn_implementation = {config['_attn_implementation']}")

# 保存修改
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print("✅ 配置文件已修复！")
```

运行脚本：
```bash
python fix_model_config.py
```

## 验证修复

修复后，重新启动后端应该看到：

```
🔧 覆盖模型配置: _attn_implementation=eager
🤖 加载模型...
✅ 模型加载成功！
```

## 其他注意事项

- macOS 系统使用 CPU 模式，推理速度会比 GPU 慢
- 确保 `backend/config.yaml` 中设置：
  - `device: "cpu"`
  - `torch_dtype: "float32"`
  - `attn_implementation: "eager"`
