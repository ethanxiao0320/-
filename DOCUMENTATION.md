"""完整项目使用说明和快速开始指南"""

# 高考错题管理系统 - 完整文档

## 📦 项目概述

这是一个**智能高考错题管理和试卷生成系统**，专为中国高中生设计，包含以下核心功能：

✅ 错题上传和管理  
✅ 智能相似题目推荐  
✅ 自动试卷生成  
✅ 学习进度追踪  
✅ 题库导入（支持学科网等）  

---

## 🚀 快速开始

### 1. 环境配置

```bash
# 克隆仓库
git clone https://github.com/ethanxiao0320/-
cd exam-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

访问 `http://localhost:5000` 即可使用

---

## 📚 功能说明

### 一、学生管理
- 创建学生账户（支持同名登录）
- 查看个人统计数据

### 二、错题上传
**必填字段：**
- 科目：语文、数学、英语、物理、化学、生物、历史、地理、政治
- 难度：简单、中等、困难
- 知识点：如"导数基础"、"成语辨析"等
- 题目内容：完整的题目描述
- 正确答案：标准答案

**可选字段：**
- 题型：选择题、填空题、解答题等
- 解题思路：详细的解题步骤

### 三、相似题目推荐 ⭐
上传错题后，系统自动从题库中推荐相似题目进行针对性训练

**相似度计算权重：**
```
知识点相似度: 40%
难度相似度:   30%
题型相似度:   20%
内容相似度:   10%
```

### 四、试卷生成
**3种试卷类型：**

1. **标准试卷** - 综合难度，均衡出题
2. **重点突破** - 针对薄弱知识点，难度递进
3. **混合试卷** - 按比例混合（简单:中等:困难 = 2:3:5）

### 五、题库管理
**导入题库：**
```python
# 从学科网导入
POST /api/library/import/xuekewang
{
    "subject": "数学",
    "grade": 3
}

# 导入自定义题库
POST /api/library/import/custom
{
    "questions": [
        {
            "subject": "数学",
            "difficulty": "中等",
            "question_type": "解答题",
            "content": "题目内容",
            "answer": "标准答案",
            "knowledge_point": "导数基础",
            "explanation": "解题思路"
        }
    ]
}
```

---

## 🔧 API 接口详解

### 学生管理
```
POST   /api/student/create              # 创建学生
GET    /api/student/<id>                # 获取学生信息
GET    /api/students                    # 列出所有学生
```

### 错题管理
```
POST   /api/question/add                # 添加错题
GET    /api/questions/<student_id>      # 获取错题列表
PUT    /api/question/<id>               # 更新错题（标记复习）
DELETE /api/question/<id>               # 删除错题
```

### 相似题目和推荐
```
GET    /api/similar-questions/<id>      # 获取相似题目（5道）
GET    /api/practice-questions/<id>     # 获取针对性练习题
POST   /api/generate-similar-exam/<id>  # 生成相似题目试卷
```

### 试卷生成
```
POST   /api/exam/generate               # 生成试卷
GET    /api/exams/<student_id>          # 获取试卷列表
```

### 统计分析
```
GET    /api/stats/<student_id>          # 获取学习统计
GET    /api/stats/<student_id>/subjects # 各科目统计
GET    /api/stats/<student_id>/knowledge-points  # 知识点统计
```

### 题库
```
POST   /api/library/import/xuekewang    # 从学科网导入
POST   /api/library/import/custom       # 导入自定义题库
GET    /api/library/stats               # 题库统计
GET    /api/library/search              # 搜索题库
GET    /api/questions/browse            # 浏览题库
GET    /api/questions/<id>              # 获取题目详情
```

---

## 📊 数据模型

### Student（学生）
```
- id: 主键
- name: 学生名字（唯一）
- created_at: 创建时间
```

### WrongQuestion（错题）
```
- id: 主键
- student_id: 关联学生
- subject: 科目
- difficulty: 难度
- question_type: 题型
- question_content: 题目内容
- knowledge_point: 知识点
- correct_answer: 正确答案
- student_answer: 学生答案（可选）
- explanation: 解析
- times_reviewed: 复习次数
- last_reviewed: 最后复习时间
```

### Question（题库题目）
```
- id: 主键
- subject: 科目
- difficulty: 难度
- question_type: 题型
- content: 题目内容
- answer: 标准答案
- knowledge_point: 知识点
- explanation: 解析
- source: 来源（学科网/自定义）
- external_id: 外���ID
- usage_count: 被使用次数
```

### GeneratedExam（生成的试卷）
```
- id: 主键
- student_id: 关联学生
- name: 试卷名称
- subject: 科目
- total_questions: 题目数
- total_score: 满分
- difficulty_distribution: 难度分布
- question_ids: 包含的题目ID
- created_at: 创建时间
```

### LearningStats（学习统计）
```
- id: 主键
- student_id: 关联学生
- total_wrong_questions: 总错题数
- total_reviews: 总复习次数
- mastered_questions: 已掌握题目数
- weak_subjects: 薄弱科目
- weak_knowledge_points: 薄弱知识点
```

---

## 💡 使用建议

### 📝 有效的错题记录方法

1. **及时上传** - 做错题目后立即上传
2. **完整填写** - 不要遗漏知识点字段
3. **定期复习** - 系统会根据复习次数提示掌握进度
4. **利用推荐** - 做完相似题目后标记复习

### 🎯 针对性训练流程

```
1. 上传错题 → 
2. 查看相似题目（自动推荐） → 
3. 做相似题目进行巩固 → 
4. 生成针对该知识点的试卷 → 
5. 复习3次后标记为已掌握
```

### 📈 掌握进度指标

- **未掌握**：复习 0-1 次
- **巩固中**：复习 2 次
- **已掌握**：复习 3 次以上

系统会自动计算各科目���知识点的掌握进度。

---

## 🔌 扩展功能

### 集成其他题库源

在 `question_bank.py` 中添加新的导入函数：

```python
@staticmethod
def import_from_gaokaojuan(subject, grade=3):
    """从高考圈导入题目"""
    # 实现逻辑
    pass
```

### 自定义相似度算法

修改 `_calculate_similarity()` 方法的权重：

```python
# 调整权重以适应您的需求
scores.append(('knowledge_point', kp_similarity, 0.5))  # 提高知识点权重
```

---

## 📞 常见问题

**Q: 题库为空怎么办？**  
A: 使用 `/api/library/import/custom` 导入自己的题库，或使用 `/api/library/import/xuekewang` 从学科网导入。

**Q: 相似题目推荐不准确？**  
A: 确保：
   - 错题的"知识点"字段填写准确
   - 题库中有充足的题目
   - 可以调整 `question_bank.py` 中的相似度权重

**Q: 如何导出数据？**  
A: 使用任何数据库工具连接到 `exam_system.db` 即可。

**Q: 支持多学生吗？**  
A: 支持。每个学生都有独立的错题库和学习统计。

---

## 🛠️ 技术栈

- **后端**：Flask（轻量级Web框架）
- **数据库**：SQLite3（无需额外配置）
- **前端**：HTML5 + CSS3 + JavaScript（原生，无框架）
- **ORM**：SQLAlchemy

---

## 📄 许可证

MIT License - 可自由使用和修改

---

## 🎓 祝你高考加油！🚀

**更新时间**：2026年6月  
**版本**：1.0
