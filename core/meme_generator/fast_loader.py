"""
快速加载器
使用预生成的静态缓存快速加载meme信息，避免重复扫描和加载
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .config import meme_config
from .log import logger
from .manager import _memes, add_meme
from .meme import Meme, MemeParamsType, MemeArgsType, CommandShortcut


class FastMemeLoader:
    """快速meme加载器"""
    
    def __init__(self, cache_dir: str = "static_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_data: Dict[str, Any] = {}
        self.loaded = False
    
    def is_cache_available(self) -> bool:
        """检查缓存是否可用"""
        required_files = [
            self.cache_dir / "meme_list.json",
            self.cache_dir / "meme_info.json", 
            self.cache_dir / "meme_keywords.json",
            self.cache_dir / "cache_meta.json"
        ]
        return all(f.exists() for f in required_files)
    
    def load_cache(self) -> bool:
        """加载静态缓存"""
        if not self.is_cache_available():
            logger.warning("静态缓存不可用，将使用标准加载方式")
            return False
        
        try:
            start_time = time.time()
            
            # 加载meme列表
            with open(self.cache_dir / "meme_list.json", 'r', encoding='utf-8') as f:
                self.cache_data["meme_list"] = json.load(f)
            
            # 加载meme详细信息
            with open(self.cache_dir / "meme_info.json", 'r', encoding='utf-8') as f:
                self.cache_data["meme_info"] = json.load(f)
            
            # 加载关键词映射
            with open(self.cache_dir / "meme_keywords.json", 'r', encoding='utf-8') as f:
                self.cache_data["meme_keywords"] = json.load(f)
            
            # 加载元数据
            with open(self.cache_dir / "cache_meta.json", 'r', encoding='utf-8') as f:
                self.cache_data["meta"] = json.load(f)
            
            elapsed_time = time.time() - start_time
            logger.info(f"⚡ 静态缓存加载完成，耗时 {elapsed_time:.3f}秒")
            logger.info(f"📊 加载了 {len(self.cache_data['meme_list'])} 个meme")
            
            self.loaded = True
            return True
            
        except Exception as e:
            logger.error(f"加载静态缓存失败: {e}")
            return False
    
    def get_meme_list(self) -> List[str]:
        """获取meme列表"""
        if not self.loaded:
            return []
        return self.cache_data.get("meme_list", [])
    
    def get_meme_info(self, meme_key: str) -> Optional[Dict[str, Any]]:
        """获取meme详细信息"""
        if not self.loaded:
            return None
        return self.cache_data.get("meme_info", {}).get(meme_key)
    
    def get_meme_keywords(self) -> Dict[str, List[str]]:
        """获取关键词映射"""
        if not self.loaded:
            return {}
        return self.cache_data.get("meme_keywords", {})
    
    def search_meme_by_keyword(self, keyword: str) -> List[str]:
        """通过关键词搜索meme"""
        keywords_map = self.get_meme_keywords()
        return keywords_map.get(keyword, [])
    
    def get_cache_meta(self) -> Dict[str, Any]:
        """获取缓存元数据"""
        if not self.loaded:
            return {}
        return self.cache_data.get("meta", {})
    
    def create_lazy_meme_objects(self):
        """创建延迟加载的meme对象"""
        if not self.loaded:
            return
        
        logger.info("🔄 创建延迟加载的meme对象...")
        
        for meme_key in self.get_meme_list():
            if meme_key in _memes:
                continue  # 已存在，跳过
            
            info = self.get_meme_info(meme_key)
            if not info:
                continue
            
            try:
                # 创建延迟加载的meme对象
                lazy_meme = LazyMeme(meme_key, info, self.cache_dir)
                _memes[meme_key] = lazy_meme
                
            except Exception as e:
                logger.warning(f"创建延迟meme对象 {meme_key} 失败: {e}")
        
        logger.info(f"✅ 创建了 {len(_memes)} 个延迟加载的meme对象")


class LazyMeme(Meme):
    """延迟加载的meme对象"""
    
    def __init__(self, key: str, info: Dict[str, Any], cache_dir: Path):
        self.key = key
        self.info = info
        self.cache_dir = cache_dir
        self._actual_meme: Optional[Meme] = None
        self._loaded = False
        
        # 从缓存信息构建基本属性
        self.keywords = info.get("keywords", [])
        self.tags = set(info.get("tags", []))
        
        # 构建shortcuts
        self.shortcuts = []
        for shortcut_info in info.get("shortcuts", []):
            self.shortcuts.append(CommandShortcut(
                key=shortcut_info["key"],
                humanized=shortcut_info.get("humanized"),
                args=shortcut_info.get("args", [])
            ))
        
        # 构建日期
        try:
            self.date_created = datetime.fromisoformat(info["date_created"])
            self.date_modified = datetime.fromisoformat(info["date_modified"])
        except:
            self.date_created = datetime.now()
            self.date_modified = datetime.now()
        
        # 构建参数类型
        params = info.get("params", {})
        args_type = None
        if "args_type" in info:
            # 这里可以进一步实现args_type的延迟加载
            # 暂时设为None，在实际需要时再加载
            pass
        
        self.params_type = MemeParamsType(
            min_images=params.get("min_images", 0),
            max_images=params.get("max_images", 0),
            min_texts=params.get("min_texts", 0),
            max_texts=params.get("max_texts", 0),
            default_texts=params.get("default_texts", []),
            args_type=args_type
        )
        
        # 延迟加载的函数
        self.function = self._lazy_function
    
    def _load_actual_meme(self):
        """加载实际的meme对象"""
        if self._loaded:
            return
        
        try:
            # 这里需要动态导入实际的meme模块
            # 由于我们无法确定模块路径，这里使用标准的加载方式
            from .manager import load_meme, load_memes
            
            # 尝试从内置memes加载
            builtin_path = Path(__file__).parent / "memes" / self.key
            if builtin_path.exists():
                load_meme(f"meme_generator.memes.{self.key}")
            else:
                # 从额外目录加载
                for meme_dir in meme_config.meme.meme_dirs:
                    meme_path = Path(meme_dir) / self.key
                    if meme_path.exists():
                        load_memes(meme_dir)
                        break
            
            # 获取实际加载的meme对象
            from .manager import get_meme
            self._actual_meme = get_meme(self.key)
            self._loaded = True
            
        except Exception as e:
            logger.error(f"延迟加载meme {self.key} 失败: {e}")
            raise
    
    def _lazy_function(self, images, texts, args):
        """延迟加载的函数包装器"""
        self._load_actual_meme()
        if self._actual_meme:
            return self._actual_meme.function(images, texts, args)
        else:
            raise RuntimeError(f"无法加载meme {self.key}")
    
    def generate_preview(self):
        """生成预览图"""
        # 首先尝试从缓存加载预览图
        preview_path = self.cache_dir / "previews" / f"{self.key}.jpg"
        if not preview_path.exists():
            preview_path = self.cache_dir / "previews" / f"{self.key}.png"
        if not preview_path.exists():
            preview_path = self.cache_dir / "previews" / f"{self.key}.gif"
        
        if preview_path.exists():
            # 返回缓存的预览图
            with open(preview_path, 'rb') as f:
                from io import BytesIO
                return BytesIO(f.read())
        
        # 如果没有缓存，则动态生成
        self._load_actual_meme()
        if self._actual_meme:
            return self._actual_meme.generate_preview()
        else:
            raise RuntimeError(f"无法生成meme {self.key} 的预览图")
    
    def __call__(self, images, texts, args):
        """调用meme生成函数"""
        return self._lazy_function(images, texts, args)


# 全局快速加载器实例
_fast_loader: Optional[FastMemeLoader] = None


def get_fast_loader() -> FastMemeLoader:
    """获取快速加载器实例"""
    global _fast_loader
    if _fast_loader is None:
        # 查找缓存目录
        cache_dir = "static_cache"
        
        # 尝试在不同位置查找缓存
        possible_paths = [
            Path.cwd() / cache_dir,
            Path(__file__).parent.parent / cache_dir,
            Path(__file__).parent.parent.parent / cache_dir,
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "cache_meta.json").exists():
                cache_dir = str(path)
                break
        
        _fast_loader = FastMemeLoader(cache_dir)
    
    return _fast_loader


def enable_fast_loading() -> bool:
    """启用快速加载模式"""
    loader = get_fast_loader()
    
    if loader.load_cache():
        # 创建延迟加载的meme对象
        loader.create_lazy_meme_objects()
        logger.info("⚡ 快速加载模式已启用")
        return True
    else:
        logger.warning("快速加载模式启用失败，将使用标准加载方式")
        return False


def is_fast_loading_available() -> bool:
    """检查快速加载是否可用"""
    loader = get_fast_loader()
    return loader.is_cache_available()