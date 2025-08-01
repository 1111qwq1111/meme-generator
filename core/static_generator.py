#!/usr/bin/env python3
"""
静态资源预生成器
用于预生成meme信息，加速启动和更新过程
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib
import importlib.util
import pkgutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from meme_generator.config import meme_config
from meme_generator.manager import _memes, get_memes, get_meme_keys
from meme_generator.log import logger


class StaticMemeGenerator:
    """静态meme信息生成器"""
    
    def __init__(self, output_dir: str = "static_cache"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 缓存文件路径
        self.meme_list_file = self.output_dir / "meme_list.json"
        self.meme_info_file = self.output_dir / "meme_info.json"
        self.meme_keywords_file = self.output_dir / "meme_keywords.json"
        self.cache_meta_file = self.output_dir / "cache_meta.json"
        self.preview_dir = self.output_dir / "previews"
        self.preview_dir.mkdir(exist_ok=True)
    
    def calculate_directory_hash(self, directory: Path) -> str:
        """计算目录的哈希值，用于检测变化"""
        if not directory.exists():
            return ""
        
        hash_md5 = hashlib.md5()
        for file_path in sorted(directory.rglob("*.py")):
            if file_path.is_file():
                hash_md5.update(str(file_path.relative_to(directory)).encode())
                hash_md5.update(str(file_path.stat().st_mtime).encode())
        
        return hash_md5.hexdigest()
    
    def get_current_state_hash(self) -> Dict[str, str]:
        """获取当前所有meme目录的状态哈希"""
        state = {}
        
        # 内置memes目录
        builtin_dir = Path(__file__).parent / "meme_generator" / "memes"
        if builtin_dir.exists():
            state["builtin"] = self.calculate_directory_hash(builtin_dir)
        
        # 额外的meme目录
        for i, meme_dir in enumerate(meme_config.meme.meme_dirs):
            if Path(meme_dir).exists():
                state[f"extra_{i}"] = self.calculate_directory_hash(Path(meme_dir))
        
        return state
    
    def load_cache_meta(self) -> Dict[str, Any]:
        """加载缓存元数据"""
        if self.cache_meta_file.exists():
            try:
                with open(self.cache_meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
        return {}
    
    def save_cache_meta(self, meta: Dict[str, Any]):
        """保存缓存元数据"""
        try:
            with open(self.cache_meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")
    
    def is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not all([
            self.meme_list_file.exists(),
            self.meme_info_file.exists(),
            self.meme_keywords_file.exists(),
            self.cache_meta_file.exists()
        ]):
            return False
        
        cache_meta = self.load_cache_meta()
        current_state = self.get_current_state_hash()
        
        return cache_meta.get("state_hash") == current_state
    
    def load_meme_modules(self):
        """加载所有meme模块"""
        logger.info("🔄 开始加载meme模块...")
        
        # 清空现有的memes
        _memes.clear()
        
        # 加载内置memes
        if meme_config.meme.load_builtin_memes:
            builtin_dir = Path(__file__).parent / "meme_generator" / "memes"
            if builtin_dir.exists():
                self._load_memes_from_directory(builtin_dir, "meme_generator.memes")
        
        # 加载额外的meme目录
        for meme_dir in meme_config.meme.meme_dirs:
            if Path(meme_dir).exists():
                self._load_memes_from_directory(Path(meme_dir))
        
        logger.info(f"✅ 加载完成，共加载 {len(_memes)} 个meme")
    
    def _load_memes_from_directory(self, dir_path: Path, module_prefix: str = None):
        """从目录加载memes"""
        if module_prefix:
            # 使用importlib加载内置模块
            for path in dir_path.iterdir():
                if path.is_dir() and not path.name.startswith("_"):
                    try:
                        importlib.import_module(f"{module_prefix}.{path.name}")
                    except Exception as e:
                        logger.warning(f"加载模块 {module_prefix}.{path.name} 失败: {e}")
        else:
            # 使用pkgutil加载外部模块
            try:
                for module_info in pkgutil.iter_modules([str(dir_path)]):
                    if module_info.name.startswith("_"):
                        continue
                    
                    module_spec = module_info.module_finder.find_spec(module_info.name, None)
                    if not module_spec or not module_spec.origin or not module_spec.loader:
                        continue
                    
                    try:
                        module = importlib.util.module_from_spec(module_spec)
                        module_spec.loader.exec_module(module)
                    except Exception as e:
                        logger.warning(f"加载模块 {module_spec.origin} 失败: {e}")
            except Exception as e:
                logger.warning(f"扫描目录 {dir_path} 失败: {e}")
    
    def generate_meme_list(self) -> List[str]:
        """生成meme列表"""
        return sorted(get_meme_keys())
    
    def generate_meme_info(self) -> Dict[str, Dict[str, Any]]:
        """生成详细的meme信息"""
        meme_info = {}
        
        for meme in get_memes():
            try:
                # 基本信息
                info = {
                    "key": meme.key,
                    "keywords": meme.keywords,
                    "shortcuts": [
                        {
                            "key": shortcut.key,
                            "humanized": shortcut.humanized,
                            "args": shortcut.args
                        } for shortcut in meme.shortcuts
                    ],
                    "tags": list(meme.tags),
                    "date_created": meme.date_created.isoformat(),
                    "date_modified": meme.date_modified.isoformat(),
                    "params": {
                        "min_images": meme.params_type.min_images,
                        "max_images": meme.params_type.max_images,
                        "min_texts": meme.params_type.min_texts,
                        "max_texts": meme.params_type.max_texts,
                        "default_texts": meme.params_type.default_texts,
                    }
                }
                
                # 参数类型信息
                if meme.params_type.args_type:
                    args_type = meme.params_type.args_type
                    info["args_type"] = {
                        "parser_options": [
                            {
                                "names": option.names,
                                "help_text": option.help_text,
                                "default": option.default,
                                "action": str(option.action) if option.action else None
                            } for option in args_type.parser_options
                        ]
                    }
                
                meme_info[meme.key] = info
                
            except Exception as e:
                logger.warning(f"生成meme {meme.key} 信息失败: {e}")
        
        return meme_info
    
    def generate_meme_keywords(self) -> Dict[str, List[str]]:
        """生成关键词映射"""
        keyword_map = {}
        
        for meme in get_memes():
            for keyword in meme.keywords:
                if keyword not in keyword_map:
                    keyword_map[keyword] = []
                keyword_map[keyword].append(meme.key)
        
        return keyword_map
    
    def generate_previews(self, max_workers: int = 4) -> Dict[str, str]:
        """生成预览图（并行处理）"""
        logger.info("🖼️  开始生成预览图...")
        preview_info = {}
        
        def generate_single_preview(meme_key: str) -> tuple[str, Optional[str]]:
            """生成单个预览图"""
            try:
                from meme_generator.manager import get_meme
                import filetype
                
                meme = get_meme(meme_key)
                result = meme.generate_preview()
                content = result.getvalue()
                
                # 确定文件扩展名
                ext = filetype.guess_extension(content) or "jpg"
                preview_file = self.preview_dir / f"{meme_key}.{ext}"
                
                # 保存预览图
                with open(preview_file, 'wb') as f:
                    f.write(content)
                
                return meme_key, str(preview_file.relative_to(self.output_dir))
                
            except Exception as e:
                logger.warning(f"生成 {meme_key} 预览图失败: {e}")
                return meme_key, None
        
        # 并行生成预览图
        meme_keys = list(get_meme_keys())
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_key = {
                executor.submit(generate_single_preview, key): key 
                for key in meme_keys
            }
            
            completed = 0
            for future in as_completed(future_to_key):
                meme_key, preview_path = future.result()
                if preview_path:
                    preview_info[meme_key] = preview_path
                
                completed += 1
                if completed % 10 == 0:
                    logger.info(f"预览图生成进度: {completed}/{len(meme_keys)}")
        
        logger.info(f"✅ 预览图生成完成，成功生成 {len(preview_info)} 个预览图")
        return preview_info
    
    def generate_static_cache(self, include_previews: bool = True):
        """生成所有静态缓存"""
        logger.info("🚀 开始生成静态缓存...")
        start_time = time.time()
        
        # 加载所有meme模块
        self.load_meme_modules()
        
        # 生成各种缓存文件
        logger.info("📝 生成meme列表...")
        meme_list = self.generate_meme_list()
        with open(self.meme_list_file, 'w', encoding='utf-8') as f:
            json.dump(meme_list, f, ensure_ascii=False, indent=2)
        
        logger.info("📋 生成meme详细信息...")
        meme_info = self.generate_meme_info()
        with open(self.meme_info_file, 'w', encoding='utf-8') as f:
            json.dump(meme_info, f, ensure_ascii=False, indent=2)
        
        logger.info("🔍 生成关键词映射...")
        meme_keywords = self.generate_meme_keywords()
        with open(self.meme_keywords_file, 'w', encoding='utf-8') as f:
            json.dump(meme_keywords, f, ensure_ascii=False, indent=2)
        
        # 生成预览图
        preview_info = {}
        if include_previews:
            preview_info = self.generate_previews()
        
        # 保存缓存元数据
        cache_meta = {
            "generated_at": datetime.now().isoformat(),
            "state_hash": self.get_current_state_hash(),
            "meme_count": len(meme_list),
            "preview_count": len(preview_info),
            "include_previews": include_previews
        }
        self.save_cache_meta(cache_meta)
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ 静态缓存生成完成！")
        logger.info(f"📊 统计信息:")
        logger.info(f"   - meme数量: {len(meme_list)}")
        logger.info(f"   - 预览图数量: {len(preview_info)}")
        logger.info(f"   - 生成时间: {elapsed_time:.2f}秒")
        logger.info(f"   - 缓存目录: {self.output_dir.absolute()}")
    
    def load_static_cache(self) -> Dict[str, Any]:
        """加载静态缓存"""
        if not self.is_cache_valid():
            logger.warning("静态缓存无效或不存在")
            return {}
        
        try:
            cache_data = {}
            
            # 加载meme列表
            with open(self.meme_list_file, 'r', encoding='utf-8') as f:
                cache_data["meme_list"] = json.load(f)
            
            # 加载meme信息
            with open(self.meme_info_file, 'r', encoding='utf-8') as f:
                cache_data["meme_info"] = json.load(f)
            
            # 加载关键词映射
            with open(self.meme_keywords_file, 'r', encoding='utf-8') as f:
                cache_data["meme_keywords"] = json.load(f)
            
            # 加载元数据
            cache_data["meta"] = self.load_cache_meta()
            
            logger.info(f"✅ 静态缓存加载成功，包含 {len(cache_data['meme_list'])} 个meme")
            return cache_data
            
        except Exception as e:
            logger.error(f"加载静态缓存失败: {e}")
            return {}


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="meme-generator 静态资源生成器")
    parser.add_argument("--output-dir", default="static_cache", help="输出目录")
    parser.add_argument("--no-previews", action="store_true", help="不生成预览图")
    parser.add_argument("--check-cache", action="store_true", help="检查缓存状态")
    parser.add_argument("--force", action="store_true", help="强制重新生成")
    
    args = parser.parse_args()
    
    generator = StaticMemeGenerator(args.output_dir)
    
    if args.check_cache:
        is_valid = generator.is_cache_valid()
        print(f"缓存状态: {'有效' if is_valid else '无效'}")
        if is_valid:
            meta = generator.load_cache_meta()
            print(f"生成时间: {meta.get('generated_at', '未知')}")
            print(f"meme数量: {meta.get('meme_count', '未知')}")
            print(f"预览图数量: {meta.get('preview_count', '未知')}")
        return
    
    if not args.force and generator.is_cache_valid():
        print("✅ 缓存已是最新，无需重新生成")
        print("使用 --force 参数强制重新生成")
        return
    
    # 生成静态缓存
    generator.generate_static_cache(include_previews=not args.no_previews)


if __name__ == "__main__":
    main()