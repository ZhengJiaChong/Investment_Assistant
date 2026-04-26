# Git 上传指南

## 📋 项目已优化，准备上传到 GitHub

### ✅ 已完成的优化：

1. **创建 `.gitignore` 文件**
   - 排除 IDE 缓存、临时文件、生成的图片
   - 排除旧的 Python 脚本和参考项目
   - 保留必要的目录结构

2. **优化前端 `.gitignore`**
   - 排除 node_modules、构建产物
   - 排除未使用的目录和文件

3. **创建 `.gitkeep` 文件**
   - 保留 `image_show/` 和 `backend/image_show/` 目录结构

4. **创建数据库初始化脚本 `init_db.py`**
   - 方便从 Excel 恢复数据库

5. **更新 `README.md`**
   - 提供完整的项目说明和安装指南

## 🚀 上传步骤：

### 1. 初始化 Git 仓库（如果还没有）

```bash
cd j:\agent\CASE-ChatBI投资助手
git init
```

### 2. 添加所有文件

```bash
git add .
```

### 3. 查看将要上传的文件

```bash
git status
```

你会看到：
- ✅ 后端核心代码（backend/）
- ✅ 前端核心代码（stock-vue-frontend/）
- ✅ 数据库文件（gold_data.db）
- ✅ Excel 数据备份（stock_history_data.xlsx）
- ✅ 配置文件（faq.txt, .gitignore）
- ✅ 文档（README.md）
- ❌ 旧脚本（已被 .gitignore 排除）
- ❌ 生成的图片（已被 .gitignore 排除）
- ❌ node_modules（已被 .gitignore 排除）

### 4. 提交更改

```bash
git commit -m "Initial commit: ChatBI 投资助手 (LangChain + Vue 3)"
```

### 5. 关联远程仓库

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### 6. 推送到 GitHub

```bash
git push -u origin main
```

或者如果使用 master 分支：

```bash
git push -u origin master
```

## 📦 项目大小预估：

- ✅ **核心代码**: ~500 KB
- ✅ **数据库**: ~1 MB
- ✅ **Excel 数据**: ~313 KB
- ✅ **总计**: ~2 MB（非常轻量！）

## ⚠️ 注意事项：

1. **不要上传 API Key**
   - `.env` 文件已在 `.gitignore` 中排除
   - 在 GitHub 上使用环境变量或 Secrets

2. **数据库文件**
   - `gold_data.db` 已包含在项目中
   - 如果需要从 Excel 恢复，运行 `python init_db.py`

3. **图片目录**
   - `image_show/` 目录结构已保留
   - 实际图片在使用时自动生成

4. **前端依赖**
   - `node_modules/` 不需要上传
   - 其他人运行 `npm install` 即可安装

## 🎉 完成！

现在你的项目已经准备就绪，可以安全地上传到 GitHub 了！
