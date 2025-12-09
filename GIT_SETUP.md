# Git 仓库设置指南

## 初始化 Git 仓库

如果项目还没有 Git 仓库，按以下步骤初始化：

```bash
# 在项目根目录执行
git init

# 添加所有文件
git add .

# 提交初始版本
git commit -m "Initial commit: CrowdLabel System"

# 添加远程仓库（替换为你的 GitHub 仓库地址）
git remote add origin https://github.com/your-username/crowdlabel-system.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 提交说明

### 需要提交的文件

✅ **必须提交：**
- 所有源代码文件（前端和后端）
- `README.md` - 项目说明文档
- `requirements.txt` - Python 依赖
- `package.json` - Node.js 依赖
- `backend/scripts/export_schema.sql` - 数据库 Schema SQL
- `backend/scripts/generate_test_data.py` - 数据生成脚本
- `backend/api/migrations/` - 数据库迁移文件
- `.gitignore` - Git 忽略规则

❌ **不需要提交：**
- `node_modules/` - 前端依赖（通过 package.json 安装）
- `__pycache__/` - Python 缓存文件
- `.env` - 环境变量文件（包含敏感信息）
- `*.sql` - 数据库 dump 文件（太大且可能包含敏感数据）
- `*.log` - 日志文件
- IDE 配置文件（`.vscode/`, `.idea/`）

### 数据库相关

**提交内容：**
- ✅ `backend/scripts/export_schema.sql` - 数据库 Schema（建表脚本）
- ✅ `backend/api/migrations/` - Django 迁移文件
- ✅ `backend/scripts/generate_test_data.py` - 数据生成脚本

**不提交：**
- ❌ 完整的数据库 dump 文件（.sql 文件太大）
- ❌ 包含真实数据的数据库文件

**说明：**
- Schema SQL 文件用于展示数据库结构设计
- 迁移文件用于在其他环境重建数据库
- 数据生成脚本用于演示和测试

## GitHub 仓库设置建议

1. **仓库名称**：`crowdlabel-system` 或 `ds5003-crowdlabel`
2. **描述**：Database Systems Course Project - CrowdLabel System
3. **可见性**：根据课程要求设置（Private 或 Public）
4. **README**：使用项目根目录的 README.md
5. **Topics**：添加标签如 `django`, `react`, `database`, `crowdsourcing`

## 提交前检查清单

- [ ] 所有源代码已提交
- [ ] README.md 完整且准确
- [ ] .gitignore 已配置
- [ ] 数据库 Schema SQL 文件已提交
- [ ] 数据生成脚本已提交
- [ ] 敏感信息已从代码中移除（密码、密钥等）
- [ ] 代码可以正常运行（测试过）

