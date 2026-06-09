"""试卷生成引擎 - 根据错题智能生成试卷"""

import random
from collections import defaultdict
from models import WrongQuestion, DIFFICULTY_LEVELS, SUBJECTS
from datetime import datetime


class ExamGenerator:
    """
    智能试卷生成器
    根据学生的错题记录生成针对性的练习试卷
    """
    
    def __init__(self):
        self.difficulty_score = {'简单': 5, '中等': 10, '困难': 15}
        self.question_type_score = {'选择题': 3, '填空题': 5, '解答题': 10}
    
    def generate_exam(
        self,
        wrong_questions,
        subject=None,
        difficulty=None,
        question_count=10,
        focus_on_weak_points=True
    ):
        """
        生成试卷
        
        Args:
            wrong_questions: 错题列表
            subject: 指定科目（可选）
            difficulty: 指定难度（可选）
            question_count: 题目数量
            focus_on_weak_points: 是否重点关注薄弱知识点
        
        Returns:
            dict: 试卷信息
        """
        # 筛选错题
        filtered_questions = self._filter_questions(
            wrong_questions,
            subject,
            difficulty
        )
        
        if not filtered_questions:
            return {'error': '没有可用的错题'}
        
        # 按重要程度排序
        if focus_on_weak_points:
            sorted_questions = self._sort_by_importance(filtered_questions)
        else:
            sorted_questions = self._sort_randomly(filtered_questions)
        
        # 选择题目
        selected_questions = sorted_questions[:min(question_count, len(sorted_questions))]
        
        # 计算试卷信息
        exam_info = self._calculate_exam_info(selected_questions)
        
        return {
            'questions': selected_questions,
            'exam_info': exam_info
        }
    
    def generate_focused_exam(self, wrong_questions, knowledge_point=None):
        """
        生成针对特定知识点的试卷
        
        Args:
            wrong_questions: 错题列表
            knowledge_point: 知识点
        
        Returns:
            dict: 试卷信息
        """
        if knowledge_point:
            filtered = [
                q for q in wrong_questions
                if q.knowledge_point == knowledge_point
            ]
        else:
            # 找出错最多的知识点
            knowledge_stats = defaultdict(int)
            for q in wrong_questions:
                knowledge_stats[q.knowledge_point] += 1
            
            most_common = max(knowledge_stats, key=knowledge_stats.get)
            filtered = [
                q for q in wrong_questions
                if q.knowledge_point == most_common
            ]
        
        return self.generate_exam(
            filtered,
            question_count=min(5, len(filtered)),
            focus_on_weak_points=True
        )
    
    def generate_mixed_exam(self, wrong_questions, question_count=20):
        """
        生成混合难度的试卷
        
        Args:
            wrong_questions: 错题列表
            question_count: 题目数量
        
        Returns:
            dict: 试卷信息
        """
        simple = [q for q in wrong_questions if q.difficulty == '简单']
        medium = [q for q in wrong_questions if q.difficulty == '中等']
        hard = [q for q in wrong_questions if q.difficulty == '困难']
        
        # 按比例混合：简单:中等:困难 = 2:3:5
        simple_count = int(question_count * 0.2)
        medium_count = int(question_count * 0.3)
        hard_count = question_count - simple_count - medium_count
        
        selected = []
        selected.extend(random.sample(simple, min(simple_count, len(simple))))
        selected.extend(random.sample(medium, min(medium_count, len(medium))))
        selected.extend(random.sample(hard, min(hard_count, len(hard))))
        
        return {
            'questions': selected,
            'exam_info': self._calculate_exam_info(selected)
        }
    
    def _filter_questions(self, questions, subject=None, difficulty=None):
        """筛选错题"""
        filtered = questions
        
        if subject:
            filtered = [q for q in filtered if q.subject == subject]
        
        if difficulty:
            filtered = [q for q in filtered if q.difficulty == difficulty]
        
        return filtered
    
    def _sort_by_importance(self, questions):
        """
        按重要程度排序
        优先级：复习次数少 > 错误频率高 > 难度高
        """
        def importance_score(q):
            # 复习次数少的优先级最高
            review_score = -q.times_reviewed * 10
            # 难度高的优先级高
            difficulty_score = self.difficulty_score.get(q.difficulty, 0)
            # 最近复习过的优先级低
            recency_score = (datetime.utcnow() - q.last_reviewed).days if q.last_reviewed else 0
            
            return review_score + difficulty_score + recency_score
        
        return sorted(questions, key=importance_score, reverse=True)
    
    def _sort_randomly(self, questions):
        """随机排序"""
        return random.sample(questions, len(questions))
    
    def _calculate_exam_info(self, questions):
        """
        计算试卷统计信息
        """
        if not questions:
            return {}
        
        # 统计信息
        total_score = 0
        difficulty_dist = defaultdict(int)
        subject_dist = defaultdict(int)
        question_type_dist = defaultdict(int)
        
        for q in questions:
            total_score += self.difficulty_score.get(q.difficulty, 0)
            difficulty_dist[q.difficulty] += 1
            subject_dist[q.subject] += 1
            question_type_dist[q.question_type] += 1
        
        return {
            'total_questions': len(questions),
            'total_score': total_score,
            'difficulty_distribution': dict(difficulty_dist),
            'subject_distribution': dict(subject_dist),
            'question_type_distribution': dict(question_type_dist)
        }
