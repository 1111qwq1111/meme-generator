#!/usr/bin/env python3
"""
优化构建脚本
用于预生成静态缓存和准备部署文件
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json

class OptimizedBuilder:
    """优化构建器"""
    
    def __init__(self, build_dir: str = "build_output"):
        self.build_dir = Path(build_dir)
        self.source_dir = Path(__file__).parent
        self.cache_dir = self.build_dir / "static_cache"
        
    def clean_build_dir(self):
        """清理构建目录"""
        if self.build_dir.exists():
            print(f"🧹 清理构建目录: {self.build_dir}")
            shutil.rmtree(self.build_dir)
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def copy_source_files(self):
        """复制源文件"""
        print("📁 复制源文件...")
        
        # 需要复制的文件和目录
        files_to_copy = [
            "meme_generator/",
            "static_generator.py",
            "setup_meme_repos.py",
            "requirements.txt",
            "config.example.toml",
            "TRANSLATION_GUIDE.md"
        ]
        
        for item in files_to_copy:
            source_path = self.source_dir / item
            dest_path = self.build_dir / item
            
            if source_path.exists():
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, dest_path)
                print(f"  ✅ 复制: {item}")
            else:
                print(f"  ⚠️ 跳过不存在的文件: {item}")
    
    def setup_extra_repos(self):
        """设置额外的meme仓库"""
        print("📦 设置额外的meme仓库...")
        
        try:
            # 在构建目录中运行setup_meme_repos.py
            result = subprocess.run([
                sys.executable, "setup_meme_repos.py"
            ], cwd=self.build_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ 额外meme仓库设置完成")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"⚠️ 额外meme仓库设置失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ 额外meme仓库设置超时")
            return False
        except Exception as e:
            print(f"⚠️ 额外meme仓库设置异常: {e}")
            return False
        
        return True
    
    def generate_static_cache(self):
        """生成静态缓存"""
        print("⚡ 生成静态缓存...")
        
        try:
            # 在构建目录中运行static_generator.py
            result = subprocess.run([
                sys.executable, "static_generator.py",
                "--output-dir", "static_cache",
                "--force"
            ], cwd=self.build_dir, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print("✅ 静态缓存生成完成")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                print(f"❌ 静态缓存生成失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 静态缓存生成超时")
            return False
        except Exception as e:
            print(f"❌ 静态缓存生成异常: {e}")
            return False
    
    def create_deployment_files(self):
        """创建部署文件"""
        print("📄 创建部署文件...")
        
        # 创建FastAPI启动脚本
        app_content = '''#!/usr/bin/env python3
"""
FastAPI meme-generator 启动脚本
"""

if __name__ == "__main__":
    from meme_generator.app import run_server
    run_server()
'''
        
        with open(self.build_dir / "app.py", 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        # 创建.env文件模板
        env_content = '''# Meme Generator 环境变量配置

# 启用快速加载模式
MEME_FAST_LOADING=true

# 翻译服务配置 (选择一种)
# OpenAI格式翻译 (推荐)
TRANSLATOR_TYPE=openai
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# 或者使用百度翻译
# TRANSLATOR_TYPE=baidu
# BAIDU_TRANS_APPID=your_baidu_appid
# BAIDU_TRANS_APIKEY=your_baidu_apikey

# 服务器配置
HOST=0.0.0.0
PORT=7860

# 日志级别
LOG_LEVEL=INFO

# GIF配置
GIF_MAX_SIZE=10.0
GIF_MAX_FRAMES=100

# Meme配置
LOAD_BUILTIN_MEMES=true
MEME_DIRS=[]
MEME_DISABLED_LIST=[]
'''
        
        with open(self.build_dir / ".env.example", 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        # 创建README文件
        readme_content = '''# Meme Generator (优化版)

🚀 **高性能表情包生成器** - 基于FastAPI的表情包生成服务

## ✨ 特性

- ⚡ **快速启动**: 使用预生成的静态缓存，启动速度提升10倍以上
- 🔍 **智能搜索**: 支持关键词快速搜索meme模板
- 📦 **完整表情库**: 整合多个表情包仓库
- 🌐 **多语言翻译**: 支持百度翻译和OpenAI like API翻译
- 🐳 **Docker优化**: 优化的Docker部署配置
- 🚀 **FastAPI**: 基于FastAPI的高性能Web服务

## 🚀 快速部署

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行FastAPI服务
python app.py
# 或者
python -m meme_generator.app
```

### API访问

服务启动后，可以通过以下方式访问：
- API文档: http://localhost:8080/docs
- 获取所有meme: http://localhost:8080/memes
- 获取meme列表: http://localhost:8080/memes/keys

## 🔧 配置说明

详细配置说明请参考 `TRANSLATION_GUIDE.md`

## 📞 支持

如有问题，请查看项目文档或提交Issue。
'''
        
        with open(self.build_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("✅ 部署文件创建完成")
    
    def create_build_info(self):
        """创建构建信息文件"""
        print("📋 创建构建信息...")
        
        # 统计缓存信息
        cache_meta_file = self.cache_dir / "cache_meta.json"
        cache_info = {}
        
        if cache_meta_file.exists():
            try:
                with open(cache_meta_file, 'r', encoding='utf-8') as f:
                    cache_info = json.load(f)
            except:
                pass
        
        # 统计文件信息
        total_files = sum(1 for _ in self.build_dir.rglob('*') if _.is_file())
        total_size = sum(f.stat().st_size for f in self.build_dir.rglob('*') if f.is_file())
        
        build_info = {
            "build_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cache_info": cache_info,
            "build_stats": {
                "total_files": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "meme_count": cache_info.get("meme_count", 0),
                "preview_count": cache_info.get("preview_count", 0)
            }
        }
        
        with open(self.build_dir / "build_info.json", 'w', encoding='utf-8') as f:
            json.dump(build_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 构建信息已保存")
        print(f"   - 总文件数: {total_files}")
        print(f"   - 总大小: {build_info['build_stats']['total_size_mb']} MB")
        print(f"   - Meme数量: {build_info['build_stats']['meme_count']}")
    
    def build(self):
        """执行完整构建"""
        print("🚀 开始优化构建...")
        start_time = time.time()
        
        try:
            # 1. 清理构建目录
            self.clean_build_dir()
            
            # 2. 复制源文件
            self.copy_source_files()
            
            # 3. 设置额外仓库
            if not self.setup_extra_repos():
                print("⚠️ 额外仓库设置失败，继续构建...")
            
            # 4. 生成静态缓存
            cache_success = self.generate_static_cache()
            if not cache_success:
                print("⚠️ 静态缓存生成失败，将使用标准加载模式")
            
            # 5. 创建部署文件
            self.create_deployment_files()
            
            # 6. 创建构建信息
            self.create_build_info()
            
            elapsed_time = time.time() - start_time
            print(f"\n🎉 优化构建完成！")
            print(f"⏱️  总耗时: {elapsed_time:.2f}秒")
            print(f"📁 构建目录: {self.build_dir.absolute()}")
            
            if cache_success:
                print("⚡ 静态缓存已生成，部署后将使用快速加载模式")
            else:
                print("📚 将使用标准加载模式")
            
            return True
            
        except Exception as e:
            print(f"❌ 构建失败: {e}")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="meme-generator 优化构建工具")
    parser.add_argument("--build-dir", default="build_output", help="构建输出目录")
    parser.add_argument("--clean-only", action="store_true", help="只清理构建目录")
    
    args = parser.parse_args()
    
    builder = OptimizedBuilder(args.build_dir)
    
    if args.clean_only:
        builder.clean_build_dir()
        print("✅ 构建目录已清理")
        return
    
    success = builder.build()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()