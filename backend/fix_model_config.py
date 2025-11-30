#!/usr/bin/env python3
"""
自动修复 DeepSeek-OCR 模型配置，禁用 FlashAttention2
适用于 macOS 系统
"""

import json
import os
import sys
from pathlib import Path

def fix_model_config(model_path: str):
    """修复模型配置文件，禁用 FlashAttention2"""

    config_file = Path(model_path) / "config.json"

    # 检查配置文件是否存在
    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        print(f"请检查模型路径是否正确: {model_path}")
        return False

    print(f"📂 找到配置文件: {config_file}")

    try:
        # 读取配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print(f"✅ 成功读取配置文件")

        # 备份原配置
        backup_file = config_file.with_suffix('.json.backup')
        if not backup_file.exists():
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"💾 已备份原配置到: {backup_file}")
        else:
            print(f"ℹ️  备份文件已存在，跳过备份")

        # 检查并修改 attention 相关配置
        modified = False
        changes = []

        # 处理各种可能的 attention 配置字段
        attn_fields = [
            '_attn_implementation',
            'attn_implementation',
            '_flash_attn_2_enabled',
            'use_flash_attention_2'
        ]

        for field in attn_fields:
            if field in config:
                old_value = config[field]
                if old_value in ['flash_attention_2', True]:
                    if field in ['_flash_attn_2_enabled', 'use_flash_attention_2']:
                        config[field] = False
                        changes.append(f"  {field}: {old_value} → False")
                    else:
                        config[field] = 'eager'
                        changes.append(f"  {field}: {old_value} → eager")
                    modified = True

        if modified:
            print(f"\n🔧 检测到需要修改的配置:")
            for change in changes:
                print(change)

            # 保存修改后的配置
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"\n✅ 配置文件已成功修复！")
            print(f"✅ FlashAttention2 已禁用，使用 eager 模式")
            return True
        else:
            print(f"\nℹ️  配置文件无需修改，未发现 FlashAttention2 配置")
            return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 DeepSeek-OCR macOS 配置修复工具")
    print("=" * 60)
    print()

    # 从 config.yaml 读取模型路径
    try:
        from config_loader import get_config
        config = get_config()
        model_config = config.get_model_config()

        if model_config['source'] == 'local':
            model_path = model_config['model_path']
            print(f"📍 从配置文件读取模型路径: {model_path}")
        else:
            print(f"⚠️  当前配置使用的是 {model_config['source']} 模型源")
            print(f"此脚本仅适用于本地模型，请修改 config.yaml 中的 model.source 为 'local'")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  无法从配置文件读取模型路径: {e}")
        print(f"请手动指定模型路径")

        # 默认 macOS 路径
        model_path = "/Users/towns/models/DeepSeek-OCR/"
        print(f"使用默认路径: {model_path}")

    # 检查模型路径
    if not os.path.exists(model_path):
        print(f"\n❌ 模型路径不存在: {model_path}")
        print(f"\n请确认模型文件已下载到正确位置")
        sys.exit(1)

    print()

    # 执行修复
    success = fix_model_config(model_path)

    print()
    print("=" * 60)
    if success:
        print("✅ 修复完成！现在可以启动后端了：")
        print()
        print("  cd backend")
        print("  python main.py")
    else:
        print("❌ 修复失败，请查看上面的错误信息")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
