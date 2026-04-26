# 环境变量配置指南

## 📋 需要的 API Key

### 1. OpenRouter API Key
- 注册地址: https://openrouter.ai/
- 获取免费的 `tencent/hy3-preview:free` 模型访问权限

### 2. Tavily API Key（可选，用于联网搜索）
- 注册地址: https://tavily.com/
- 获取免费的搜索 API Key

## 🔧 配置方法

### 方法一：使用 `.env` 文件（推荐）

1. 复制模板文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API Key：
```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-dev-xxxxxxxxxxxxxxxxxxxx
```

### 方法二：Windows 系统环境变量

**临时设置（当前命令行窗口有效）：**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
set TAVILY_API_KEY=tvly-dev-xxxxxxxxxxxxxxxxxxxx
```

**永久设置：**
1. 右键"此电脑" → "属性" → "高级系统设置"
2. 点击"环境变量"
3. 在"系统变量"或"用户变量"中点击"新建"
4. 添加变量名和变量值
5. 重启命令行窗口生效

### 方法三：Linux/Mac 环境变量

**临时设置：**
```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"
export TAVILY_API_KEY="tvly-dev-xxxxxxxxxxxxxxxxxxxx"
```

**永久设置（添加到 ~/.bashrc 或 ~/.zshrc）：**
```bash
echo 'export OPENROUTER_API_KEY="sk-or-v1-xxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
echo 'export TAVILY_API_KEY="tvly-dev-xxxxxxxxxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

## ✅ 验证配置

### Windows：
```cmd
echo %OPENROUTER_API_KEY%
echo %TAVILY_API_KEY%
```

### Linux/Mac：
```bash
echo $OPENROUTER_API_KEY
echo $TAVILY_API_KEY
```

## 🚀 启动项目

配置完成后，正常启动后端即可：

```bash
cd backend
python -m app.main
```

## ⚠️ 安全提醒

1. **不要将 `.env` 文件上传到 Git**（已在 `.gitignore` 中排除）
2. **不要将 API Key 硬编码在代码中**
3. **定期更换 API Key**
4. **不要在公共场合分享 API Key**
