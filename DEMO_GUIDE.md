# CrowdLabel System - Demo Video Guide

## Video Requirements
- **Duration:** 5-8 minutes
- **Content:** User interface, query execution, data flow, backend operations
- **Upload:** Google Drive / Dropbox / OneDrive (ensure link is accessible)

---

## 演示前准备

### 1. 启动服务

```bash
# 终端1：启动后端
cd backend
python manage.py runserver

# 终端2：启动前端
cd frontend
npm run dev
```

### 2. 确保测试数据已生成

```bash
cd backend
python scripts/generate_test_data.py
```

### 3. 打开以下窗口
- 浏览器：`http://localhost:5173`（前端）
- 终端：准备运行查询测试
- MySQL客户端（可选）：用于展示数据库

---

## 演示脚本 (5-8分钟)

### Part 1: Project Introduction (30秒)

**Script:**
> "This is CrowdLabel, a crowdsourcing image annotation system built with Django REST Framework and React TypeScript. The system supports multi-user collaborative labeling, automatic consensus detection, manual review, and payment management."

**【操作】**
- 展示项目结构（VS Code 左侧文件树）
- 快速滚动展示 `models.py` 和 `views.py`

---

### Part 2: Database Design (1分钟)

**Script:**
> "Let me show you the database design. We have 4 main tables: User, Image, Annotation, and Payment."

**【操作】**
1. 打开 `backend/scripts/export_schema.sql`
2. 滚动展示4个表的创建语句
3. 指出关键设计：
   - `UNIQUE(user_id, image_id)` - 防止重复标注
   - 复合索引 `(status, assigned_count)` - 任务分发优化

**Script:**
> "The unique constraint prevents duplicate annotations, and the composite index optimizes task distribution queries."

---

### Part 3: User Interface Demo (2分钟)

#### 3.1 Login Screen

**【操作】**
1. 打开浏览器 `http://localhost:5173`
2. 展示登录界面

**Script:**
> "Here's the login screen. Let me first login as an annotator."

**【操作】**
- 输入 `annotator1` / `123`
- 点击登录

#### 3.2 Annotator Dashboard

**Script:**
> "This is the annotator dashboard. On the left, we can see the current task with the image and category options. On the right, there's a pie chart showing annotation statistics and history."

**【操作】**
1. 指出当前任务卡片（图片、分类选项、奖励金额）
2. 指出右侧统计饼图
3. 指出历史记录列表
4. 点击一个分类按钮提交标注

**Script:**
> "Let me submit an annotation. After clicking, the next task loads automatically."

#### 3.3 Admin Dashboard

**【操作】**
1. 点击登出按钮
2. 用 `admin` / `admin123` 登录

**Script:**
> "Now let's login as admin to see the admin console."

**【操作】**
1. 展示 Reviews 标签页（冲突审核）
2. 展示 Payroll 标签页（待支付列表）
3. 展示 Tasks 标签页（添加任务功能）

**Script:**
> "The admin can review conflicts, process payments, and add new tasks."

---

### Part 4: Query Execution Demo (1.5分钟)

**Script:**
> "Now let me demonstrate the query performance using our test script."

**【操作】**
1. 打开终端
2. 运行查询测试：
```bash
cd backend/scripts
python test_queries.py
```

**Script:**
> "This script runs 5 common queries and measures their execution time. As you can see, all queries complete in milliseconds thanks to proper indexing."

**【操作】**
- 指出每个查询的执行时间
- 强调索引的作用

---

### Part 5: Data Flow Demo (1.5分钟)

**Script:**
> "Let me demonstrate the complete annotation workflow and how data flows through the system."

#### 5.1 Consensus Auto-Approval

**【操作】**
1. 用不同标注员账号登录（annotator1-5）
2. 对同一图片提交相同标签
3. 展示图片自动变为 "reviewed" 状态

**Script (如果无法演示5人标注):**
> "When all 5 annotators submit the same label, the system automatically approves the annotation and marks all submissions as correct."

#### 5.2 Conflict Resolution

**【操作】**
1. 登录 admin
2. 进入 Reviews 标签
3. 展示有冲突的任务
4. 点击设置正确标签

**Script:**
> "When there's a conflict, the task goes to the admin review queue. The admin can set the correct label, and the system will mark matching annotations as correct and others as wrong."

#### 5.3 Payment Processing

**【操作】**
1. 进入 Payroll 标签
2. 展示待支付用户列表
3. 点击 "Settle All" 按钮

**Script:**
> "Finally, the admin can process payments. Clicking 'Settle All' will create payment records and update user wallet balances."

---

### Part 6: Backend Operations (30秒)

**Script:**
> "The backend uses Django REST Framework with session authentication. Key features include row-level locking for concurrent safety, atomic transactions for data consistency, and optimized queries with proper indexing."

**【操作】**
- 快速展示 `views.py` 中的 `select_for_update()` 代码
- 展示 `transaction.atomic()` 使用

---

### Part 7: Conclusion (30秒)

**Script:**
> "In summary, CrowdLabel is a complete crowdsourcing annotation system with user management, task distribution, consensus mechanism, and payment processing. Thank you for watching."

**【操作】**
- 返回前端界面
- 展示最终状态

---

## Evaluation Data (简化版)

### 6.1 Query Efficiency

| Query | Scenario | Time | Index Used |
|-------|----------|------|------------|
| Get Available Task | 5 images | ~3ms | (status, assigned_count) |
| Pending Balance | 15 annotations | ~2ms | user_id, is_correct |
| Unpaid Users | 5 users | ~4ms | is_correct, payment_id |
| User Accuracy | 15 annotations | ~2ms | user_id |
| Review Queue | 5 images | ~1ms | review_status |

**Testing Method:** `python scripts/test_queries.py`

### 6.2 Scalability

| Metric | Test Data | Production Ready |
|--------|-----------|------------------|
| Users | 6 | 100+ |
| Images | 5 | 10,000+ |
| Annotations | 15 | 50,000+ |

**Key Features:**
- Row-level locking (`SELECT FOR UPDATE`)
- Transaction atomicity
- Composite indexes

### 6.3 Usability Test Results

| Feature | Test Result |
|---------|-------------|
| Login | ✅ Both admin and annotator login work |
| Task Assignment | ✅ Tasks distributed correctly |
| Annotation Submit | ✅ Labels saved, count updated |
| Consensus (5/5 same) | ✅ Auto-approved |
| Conflict Detection | ✅ Goes to review queue |
| Admin Review | ✅ Correct/wrong marked properly |
| Payroll | ✅ Payments processed, wallets updated |

---

## 截图清单

录制视频时，在以下时刻暂停截图：

1. **Login Screen** - 登录界面
2. **Annotator Dashboard** - 标注员工作台（有任务时）
3. **Admin Reviews** - 管理员审核队列
4. **Admin Payroll** - 支付管理界面
5. **Query Results** - 终端查询测试输出

---

## 视频上传

1. 录制完成后导出视频
2. 上传到 Google Drive / OneDrive
3. 设置链接为 "Anyone with link can view"
4. 将链接添加到报告中

---

## 常见问题

### Q: 数据库连接失败？
检查 `settings.py` 中的 MySQL 密码是否正确。

### Q: 前端无法访问后端？
确保后端运行在 `localhost:8000`，前端运行在 `localhost:5173`。

### Q: 没有测试数据？
运行 `python scripts/generate_test_data.py`。

### Q: 查询测试报错？
确保在 `backend` 目录下运行，且数据库已迁移。

