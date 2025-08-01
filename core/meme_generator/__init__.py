import os
from pathlib import Path

from meme_generator.config import meme_config as config
from meme_generator.manager import add_meme as add_meme
from meme_generator.manager import get_meme as get_meme
from meme_generator.manager import get_meme_keys as get_meme_keys
from meme_generator.manager import get_memes as get_memes
from meme_generator.manager import load_meme as load_meme
from meme_generator.manager import load_memes as load_memes
from meme_generator.meme import CommandShortcut as CommandShortcut
from meme_generator.meme import Meme as Meme
from meme_generator.meme import MemeArgsModel as MemeArgsModel
from meme_generator.meme import MemeArgsType as MemeArgsType
from meme_generator.meme import MemeParamsType as MemeParamsType
from meme_generator.meme import ParserArg as ParserArg
from meme_generator.meme import ParserOption as ParserOption
from meme_generator.version import __version__ as __version__

# 检查是否启用快速加载模式
_fast_loading_enabled = False
_use_fast_loading = os.getenv("MEME_FAST_LOADING", "true").lower() in ("true", "1", "yes")

if _use_fast_loading:
    try:
        from meme_generator.fast_loader import enable_fast_loading, is_fast_loading_available
        
        if is_fast_loading_available():
            _fast_loading_enabled = enable_fast_loading()
        
    except ImportError:
        pass  # 快速加载器不可用

# 如果快速加载失败或未启用，使用标准加载方式
if not _fast_loading_enabled:
    if config.meme.load_builtin_memes:
        builtin_dir = Path(__file__).parent / "memes"
        for path in builtin_dir.iterdir():
            if path.is_dir() and not path.name.startswith("_"):
                load_meme(f"meme_generator.memes.{path.name}")

    for meme_dir in config.meme.meme_dirs:
        load_memes(meme_dir)
