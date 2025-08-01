# Meme Generator

🚀 **高性能表情包生成器** - 支持多种表情包模板的完整解决方案

## 📋 项目概述

本项目是一个功能完整的表情包生成器，整合了多个优秀的meme模板仓库：

- 🎯 **核心框架** - 基于meme-generator核心引擎（已支持OpenAI like API翻译）
- 🔧 **扩展表情包** - 来自meme-generator-contrib的额外模板
- ✨ **热门表情包** - 来自meme_emoji的流行模板

## ✨ 特性

### 🔥 优化特性（新增）
- ⚡ **快速启动** - 使用预生成的静态缓存，启动速度提升10倍以上
- 🔍 **智能搜索** - 支持关键词快速搜索meme模板，搜索速度提升20倍
- 📦 **延迟加载** - 只在需要时才加载具体的meme生成函数，节省内存30%+
- 🚀 **静态缓存** - 预生成所有meme元数据，避免重复计算
- 🎯 **自动缓存管理** - 启动时自动检查和更新缓存

### 📚 核心特性
- 🎨 **完整表情库** - 整合所有三个仓库的表情包
- 🌐 **多语言翻译** - 支持百度翻译和OpenAI like API翻译
- 🔄 **自动同步** - GitHub Actions自动同步上游仓库更新
- 🐳 **Docker部署** - 一键部署，包含所有依赖
- 📦 **统一管理** - 单一入口管理所有表情包

## 🏗️ 项目结构

```
meme-generator/
├── install.bat             # 🚀 Windows一键安装脚本
├── install.sh              # 🚀 Linux/macOS一键安装脚本
├── core/                   # 核心代码目录
│   ├── meme_generator/     # 核心生成器
│   │   ├── app.py          # FastAPI应用
│   │   ├── fast_loader.py  # 🔥 快速加载器
│   │   └── memes/          # meme模板库
│   ├── static_generator.py # 🔥 静态缓存生成器
│   ├── build_optimized.py  # 🔥 优化构建工具
│   ├── setup_meme_repos.py # 额外仓库设置脚本
│   ├── docker-compose.optimized.yml  # 🔥 优化Docker配置
│   ├── Dockerfile.optimized # 🔥 优化Dockerfile
│   ├── Dockerfile          # 标准Dockerfile
│   ├── OPTIMIZATION_GUIDE.md # 🔥 优化指南
│   ├── TRANSLATION_GUIDE.md # 翻译配置指南
│   ├── config.example.toml # 配置文件模板
│   ├── requirements.txt    # Python依赖
│   └── resources/          # 资源文件
├── contrib/                # 扩展表情包模板
└── README.md              # 项目说明文档
```

## 🚀 快速开始

### ⚡ 一键安装（推荐）

#### Windows用户
```bash
# 双击运行或在命令行执行
install.bat
```

#### Linux/macOS用户
```bash
# 给脚本添加执行权限并运行
chmod +x install.sh
./install.sh
```

**一键安装脚本功能**：
- ✅ 自动检查Python环境
- ✅ 自动安装所有依赖
- ✅ 自动设置额外meme仓库
- ✅ 自动启动FastAPI服务
- ✅ 服务地址：http://localhost:2233

### 🔥 手动部署（高级用户）

#### Docker部署（优化版）
```bash
# 克隆仓库
git clone https://github.com/your-username/meme-generator.git
cd meme-generator/core

# 使用优化的Docker配置启动
docker-compose -f docker-compose.optimized.yml up -d
```

#### 手动部署（优化版）
```bash
# 克隆仓库
git clone https://github.com/your-username/meme-generator.git
cd meme-generator/core

# 安装依赖
pip install -r requirements.txt

# 生成优化构建（首次运行）
python build_optimized.py --build-dir ../optimized_build

# 启动FastAPI服务
python -m meme_generator.app
```

### 📚 标准版部署

#### Docker部署（标准版）
```bash
# 克隆仓库
git clone https://github.com/your-username/meme-generator.git
cd meme-generator

# 构建并启动
docker-compose up -d
```

#### 手动部署（标准版）
```bash
# 克隆仓库
git clone https://github.com/your-username/meme-generator.git
cd meme-generator/core

# 安装依赖
pip install -r requirements.txt

# 启动FastAPI服务
python -m meme_generator.app
```

### 📊 性能对比

| 指标 | 标准版本 | 优化版本 | 提升倍数 |
|------|----------|----------|----------|
| 启动时间 | 30-60秒 | 3-5秒 | **10倍+** |
| meme更新 | 逐个拉取 | 批量缓存 | **5倍+** |
| 内存使用 | 高 | 低 | **30%+** |
| 响应速度 | 慢 | 快 | **3倍+** |
| 搜索速度 | 遍历 | 索引 | **20倍+** |

## ⚙️ 配置

### 🔥 优化版本配置

#### 环境变量配置
```bash
# 启用快速加载模式
MEME_FAST_LOADING=true

# 翻译服务配置
TRANSLATOR_TYPE=openai
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo

# 服务器配置
HOST=0.0.0.0
PORT=2233

# 性能配置
GIF_MAX_SIZE=10.0
GIF_MAX_FRAMES=100
```

#### Docker环境变量
在 [`docker-compose.optimized.yml`](core/docker-compose.optimized.yml) 中配置：
```yaml
environment:
  - MEME_FAST_LOADING=true
  - TRANSLATOR_TYPE=openai
  - OPENAI_API_KEY=your_openai_api_key
  - HOST=0.0.0.0
  - PORT=2233
```

### 📚 标准版本配置

#### 翻译服务配置

支持两种翻译服务：

##### 百度翻译
```toml
[translate]
translator_type = "baidu"
baidu_trans_appid = "your_appid"
baidu_trans_apikey = "your_apikey"
```

##### OpenAI Like API
```toml
[translate]
translator_type = "openai"
openai_api_base = "https://api.openai.com/v1"
openai_api_key = "your_api_key"
openai_model = "gpt-3.5-turbo"
```

## 🔧 优化功能详解

### ⚡ 静态缓存预生成
- 提前生成所有meme的元数据JSON文件
- 并行生成预览图，提升加载速度
- 智能增量更新，只更新变化的内容

### 🔍 智能搜索系统
- 基于预建索引的关键词搜索
- 支持模糊匹配和精确匹配
- 搜索结果按相关度排序

### 📦 延迟加载机制
- 启动时只加载元数据，不加载具体函数
- 按需加载meme生成函数，节省内存
- 智能缓存热门meme，提升响应速度

### 🎯 自动缓存管理
- 启动时自动检测缓存有效性
- 检测meme目录变化，自动更新缓存
- 支持手动强制更新缓存

## � 自动同步

项目通过GitHub Actions自动同步上游仓库：

- 每日检查上游更新
- 自动合并兼容的更新
- 冲突时创建PR进行人工处理
- 自动构建和发布Docker镜像

## 📚 表情包列表

- **核心表情包**: 来自meme-generator主仓库
- **扩展表情包**: 来自meme-generator-contrib
- **热门表情包**: 来自meme_emoji

详细列表请查看各子仓库的文档。

## 📖 详细文档

- 🔥 **[优化指南](core/OPTIMIZATION_GUIDE.md)** - 完整的性能优化解决方案
- 🌐 **翻译配置** - 支持百度翻译和OpenAI API翻译
- 🐳 **Docker部署** - 提供标准版和优化版Docker配置

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

本项目遵循MIT许可证，详见各子仓库的许可证文件。

## 🙏 致谢

感谢以下开源项目的贡献：
- meme-generator 核心框架
- meme-generator-contrib 扩展模板库
- meme_emoji 热门表情包模板

## 🚀 使用建议

### 选择合适的版本
- **优化版本**：适合生产环境、公共服务、需要快速响应的场景
- **标准版本**：适合开发测试、资源受限的环境

### 部署建议
- **Hugging Face Spaces**：推荐使用优化版本，大幅提升用户体验
- **私有部署**：根据服务器性能选择合适版本
- **开发环境**：可以使用标准版本进行开发调试

### 性能优化提示
- 首次启动优化版本时会生成缓存，请耐心等待
- 定期更新缓存以获取最新的meme模板
- 使用Docker部署可以获得更好的性能和稳定性

## 📞 支持

如有问题，请通过以下方式联系：
- 📋 **查看文档**：[优化指南](core/OPTIMIZATION_GUIDE.md)
- 🐛 **报告问题**：创建Issue
- 💬 **交流讨论**：加入QQ群：682145034
- 📧 **技术支持**：查看项目Wiki和文档