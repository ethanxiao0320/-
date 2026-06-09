from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 科目列表
SUBJECTS = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '地理', '政治']

# 难度等级
DIFFICULTY_LEVELS = ['简单', '中等', '困难']


class Student(db.Model):
    """学生模型"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    wrong_questions = db.relationship('WrongQuestion', backref='student', lazy=True, cascade='all, delete-orphan')
    generated_exams = db.relationship('GeneratedExam', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }


class Question(db.Model):
    """题库中的标准题目"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    subject = db.Column(db.String(20), nullable=False, index=True)
    difficulty = db.Column(db.String(10), nullable=False, index=True)
    question_type = db.Column(db.String(20), nullable=False)
    
    # 题目内容
    content = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    knowledge_point = db.Column(db.String(100), nullable=False, index=True)
    
    # 来源信息
    source = db.Column(db.String(50), default='自定义')  # 学科网、自定义等
    external_id = db.Column(db.String(100), unique=True, nullable=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 使用统计
    usage_count = db.Column(db.Integer, default=0)  # 被使用次数
    last_used = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'question_type': self.question_type,
            'content': self.content,
            'answer': self.answer,
            'explanation': self.explanation,
            'knowledge_point': self.knowledge_point,
            'source': self.source
        }


class WrongQuestion(db.Model):
    """错题模型"""
    __tablename__ = 'wrong_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # 题目基本信息
    subject = db.Column(db.String(20), nullable=False)  # 科目
    difficulty = db.Column(db.String(10), nullable=False)  # 难度：简单、中等、困难
    question_type = db.Column(db.String(20), nullable=False)  # 题型：选择题、填空题、解答题等
    
    # 题目内容
    question_content = db.Column(db.Text, nullable=False)  # 题目描述
    knowledge_point = db.Column(db.String(100), nullable=False)  # 知识点
    
    # 答题信息
    correct_answer = db.Column(db.Text, nullable=False)  # 正确答案
    student_answer = db.Column(db.Text, nullable=True)  # 学生的错误答案
    explanation = db.Column(db.Text, nullable=True)  # 解题思路/详解
    
    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    times_reviewed = db.Column(db.Integer, default=0)  # 复习次数
    last_reviewed = db.Column(db.DateTime, nullable=True)  # 最后复习时间
    
    # 相似题目推荐
    similar_questions_shown = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'question_type': self.question_type,
            'question_content': self.question_content,
            'knowledge_point': self.knowledge_point,
            'correct_answer': self.correct_answer,
            'student_answer': self.student_answer,
            'explanation': self.explanation,
            'created_at': self.created_at.isoformat(),
            'times_reviewed': self.times_reviewed
        }


class GeneratedExam(db.Model):
    """生成的试卷模型"""
    __tablename__ = 'generated_exams'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    # 试卷基本信息
    name = db.Column(db.String(100), nullable=False)  # 试卷名称
    subject = db.Column(db.String(20), nullable=False)  # 科目
    total_questions = db.Column(db.Integer, default=0)  # 总题数
    total_score = db.Column(db.Integer, default=0)  # 满分
    
    # 生成配置
    difficulty_distribution = db.Column(db.JSON, nullable=True)  # 难度分布
    question_ids = db.Column(db.JSON, nullable=True)  # 包含的题目ID列表
    
    # 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'total_questions': self.total_questions,
            'total_score': self.total_score,
            'difficulty_distribution': self.difficulty_distribution,
            'created_at': self.created_at.isoformat()
        }


class LearningStats(db.Model):
    """学习统计模型"""
    __tablename__ = 'learning_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, unique=True)
    
    total_wrong_questions = db.Column(db.Integer, default=0)  # 总错题数
    total_reviews = db.Column(db.Integer, default=0)  # 总复习次数
    mastered_questions = db.Column(db.Integer, default=0)  # 掌握的题目数
    
    weak_subjects = db.Column(db.JSON, nullable=True)  # 弱科统计
    weak_knowledge_points = db.Column(db.JSON, nullable=True)  # 弱知识点统计
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'total_wrong_questions': self.total_wrong_questions,
            'total_reviews': self.total_reviews,
            'mastered_questions': self.mastered_questions,
            'weak_subjects': self.weak_subjects,
            'weak_knowledge_points': self.weak_knowledge_points
        }
