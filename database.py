"""数据库操作模块"""

from models import db, Student, WrongQuestion, GeneratedExam, LearningStats
from collections import defaultdict
from datetime import datetime


class DatabaseService:
    """
    数据库服务类
    处理所有数据库操作
    """
    
    # ==================== 学生相关操作 ====================
    
    @staticmethod
    def create_student(name):
        """
        创建学生
        
        Args:
            name: 学生名字
        
        Returns:
            Student: 学生对象
        """
        existing = Student.query.filter_by(name=name).first()
        if existing:
            return existing
        
        student = Student(name=name)
        db.session.add(student)
        db.session.commit()
        
        # 同时创建学习统计记录
        stats = LearningStats(student_id=student.id)
        db.session.add(stats)
        db.session.commit()
        
        return student
    
    @staticmethod
    def get_student(student_id):
        """
        获取学生信息
        """
        return Student.query.get(student_id)
    
    @staticmethod
    def get_student_by_name(name):
        """
        按名字获取学生
        """
        return Student.query.filter_by(name=name).first()
    
    @staticmethod
    def list_students():
        """
        列出所有学生
        """
        return Student.query.all()
    
    # ==================== 错题相关操作 ====================
    
    @staticmethod
    def add_wrong_question(student_id, question_data):
        """
        添加错题
        
        Args:
            student_id: 学生ID
            question_data: 题目数据字典
        
        Returns:
            WrongQuestion: 错题对象
        """
        question = WrongQuestion(
            student_id=student_id,
            subject=question_data['subject'],
            difficulty=question_data['difficulty'],
            question_type=question_data.get('question_type', '解答题'),
            question_content=question_data['question_content'],
            knowledge_point=question_data['knowledge_point'],
            correct_answer=question_data['correct_answer'],
            student_answer=question_data.get('student_answer'),
            explanation=question_data.get('explanation')
        )
        db.session.add(question)
        db.session.commit()
        
        # 更新学生统计
        DatabaseService._update_student_stats(student_id)
        
        return question
    
    @staticmethod
    def get_student_wrong_questions(student_id, subject=None, difficulty=None):
        """
        获取学生的错题
        
        Args:
            student_id: 学生ID
            subject: 科目过滤（可选）
            difficulty: 难度过滤（可选）
        
        Returns:
            list: 错题列表
        """
        query = WrongQuestion.query.filter_by(student_id=student_id)
        
        if subject:
            query = query.filter_by(subject=subject)
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty)
        
        return query.all()
    
    @staticmethod
    def update_wrong_question(question_id, updates):
        """
        更新错题（标记为掌握、添加笔记等）
        
        Args:
            question_id: 错题ID
            updates: 更新数据
        """
        question = WrongQuestion.query.get(question_id)
        if not question:
            return None
        
        if 'times_reviewed' in updates:
            question.times_reviewed = updates['times_reviewed']
            question.last_reviewed = datetime.utcnow()
        
        if 'explanation' in updates:
            question.explanation = updates['explanation']
        
        db.session.commit()
        DatabaseService._update_student_stats(question.student_id)
        
        return question
    
    @staticmethod
    def delete_wrong_question(question_id):
        """
        删除错题
        """
        question = WrongQuestion.query.get(question_id)
        if question:
            student_id = question.student_id
            db.session.delete(question)
            db.session.commit()
            DatabaseService._update_student_stats(student_id)
            return True
        return False
    
    # ==================== 试卷相关操作 ====================
    
    @staticmethod
    def save_generated_exam(student_id, exam_data):
        """
        保存生成的试卷
        
        Args:
            student_id: 学生ID
            exam_data: 试卷数据
        
        Returns:
            GeneratedExam: 试卷对象
        """
        exam = GeneratedExam(
            student_id=student_id,
            name=exam_data['name'],
            subject=exam_data.get('subject', '综合'),
            total_questions=exam_data['total_questions'],
            total_score=exam_data['total_score'],
            difficulty_distribution=exam_data.get('difficulty_distribution'),
            question_ids=exam_data.get('question_ids')
        )
        db.session.add(exam)
        db.session.commit()
        
        return exam
    
    @staticmethod
    def get_student_exams(student_id):
        """
        获取学生生成的所有试卷
        """
        return GeneratedExam.query.filter_by(student_id=student_id).all()
    
    # ==================== 统计相关操作 ====================
    
    @staticmethod
    def _update_student_stats(student_id):
        """
        更新学生学习统计
        """
        wrong_questions = WrongQuestion.query.filter_by(student_id=student_id).all()
        stats = LearningStats.query.filter_by(student_id=student_id).first()
        
        if not stats:
            stats = LearningStats(student_id=student_id)
            db.session.add(stats)
        
        # 统计基本数据
        stats.total_wrong_questions = len(wrong_questions)
        stats.total_reviews = sum(q.times_reviewed for q in wrong_questions)
        stats.mastered_questions = sum(1 for q in wrong_questions if q.times_reviewed >= 3)
        
        # 统计薄弱科目
        subject_count = defaultdict(int)
        for q in wrong_questions:
            subject_count[q.subject] += 1
        stats.weak_subjects = dict(sorted(subject_count.items(), key=lambda x: x[1], reverse=True))
        
        # 统计薄弱知识点
        knowledge_count = defaultdict(int)
        for q in wrong_questions:
            knowledge_count[q.knowledge_point] += 1
        stats.weak_knowledge_points = dict(sorted(knowledge_count.items(), key=lambda x: x[1], reverse=True)[:10])
        
        db.session.commit()
    
    @staticmethod
    def get_student_stats(student_id):
        """
        获取学生统计数据
        """
        stats = LearningStats.query.filter_by(student_id=student_id).first()
        return stats.to_dict() if stats else None
    
    @staticmethod
    def get_subject_statistics(student_id):
        """
        获取各科目错题统计
        """
        questions = WrongQuestion.query.filter_by(student_id=student_id).all()
        
        subject_stats = defaultdict(lambda: {'count': 0, 'difficulties': defaultdict(int)})
        
        for q in questions:
            subject_stats[q.subject]['count'] += 1
            subject_stats[q.subject]['difficulties'][q.difficulty] += 1
        
        return dict(subject_stats)
    
    @staticmethod
    def get_knowledge_point_statistics(student_id):
        """
        获取各知识点错题统计
        """
        questions = WrongQuestion.query.filter_by(student_id=student_id).all()
        
        kp_stats = defaultdict(int)
        for q in questions:
            kp_stats[q.knowledge_point] += 1
        
        # 按错题数排序
        return dict(sorted(kp_stats.items(), key=lambda x: x[1], reverse=True))
