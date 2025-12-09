# 脚本说明

## generate_test_data.py

数据生成脚本，用于创建测试用户、图片任务和标注数据。

### 使用方法

```bash
cd backend
python scripts/generate_test_data.py
```

### 生成内容

1. **测试用户**：
   - 1个管理员：`admin` / `admin123`
   - 5个标注员：`annotator1-5` / `123`

2. **测试图片任务**：
   - 5个图片任务，包含不同的分类选项和奖励金额

3. **测试标注**：
   - 为前3个图片创建标注数据
   - 模拟冲突场景（部分图片会有不同标注，触发人工审核）

### 注意事项

- 脚本使用 `get_or_create`，可以安全地多次运行
- 如果数据已存在，会跳过创建
- 所有操作在事务中执行，确保数据一致性

## export_schema.sql

数据库 Schema SQL 导出文件，包含所有表的创建语句。

### 用途

- 用于文档说明
- 用于数据库设计审查
- 用于在其他环境中快速创建数据库结构

### 表结构说明

1. **api_user**: 用户表（扩展自 Django AbstractUser）
2. **api_image**: 图片任务表
3. **api_annotation**: 标注表
4. **api_payment**: 支付记录表

### 索引说明

- 所有外键都有索引
- `api_image` 有复合索引 `(status, assigned_count)` 用于任务分发优化
- `api_annotation` 有唯一约束 `(user_id, image_id)` 防止重复标注

## test_api.py

API 测试脚本，用于验证系统功能是否正常。

### 使用方法

```bash
# 确保后端服务器正在运行
cd backend
python manage.py runserver

# 在另一个终端运行测试
python scripts/test_api.py
```

### 测试内容

1. 标注员登录测试
2. 获取任务测试
3. 获取统计信息测试
4. 管理员登录测试
5. 管理员接口测试

### 依赖

需要安装 `requests` 库：
```bash
pip install requests
```

### 注意事项

- 测试前需要先运行数据生成脚本创建测试用户
- 确保后端服务器在 `http://localhost:8000` 运行

