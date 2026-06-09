# 高考错题管理系统

帮助高中生管理错题和智能生成试卷的系统。

## 功能

✅ 错题上传与管理
✅ 按科目和难度分类
✅ 智能试卷生成
✅ 学习进度追踪

## 快速开始

### 环境要求
- Python 3.8+
- Flask
- SQLite3

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行系统

```bash
python app.py
```

访问 http://localhost:5000

## 项目结构

```
.
├── app.py                 # Flask 主应用
���── models.py              # 数据模型
├── database.py            # 数据库操作
├── exam_generator.py      # 试卷生成引擎
├── templates/             # HTML 模板
│   ├── index.html
│   ├── upload.html
│   ├── exam.html
│   └── stats.html
├── static/                # 静态文件
│   └── style.css
├── requirements.txt       # 依赖列表
└── README.md
```

## 使用说明

1. **上传错题**：选择科目、难度，输入题目和解答
2. **生成试卷**：系统根据错题生成针对性试卷
3. **查看统计**：了解学习进度和薄弱知识点
