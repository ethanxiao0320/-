"""
高考错题管理系统 - Flask Web 应用
简单易用的高中生错题收集和试卷生成系统
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from models import db, SUBJECTS, DIFFICULTY_LEVELS
from database import DatabaseService
from exam_generator import ExamGenerator
import os
from datetime import datetime
import json

# 初始化 Flask 应用
app = Flask(__name__)

# 配置数据库 - 支持Heroku
if os.environ.get('DATABASE_URL'):
    # Heroku环境
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # 本地开发
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam_system.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False

# 初始化数据库
db.init_app(app)
CORS(app)

# 初始化服务
exam_gen = ExamGenerator()

# 创建数据库表
with app.app_context():
    db.create_all()


# ==================== 首页和通用路由 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html', subjects=SUBJECTS)


@app.route('/api/subjects')
def get_subjects():
    """获取所有科目"""
    return jsonify({'subjects': SUBJECTS, 'difficulties': DIFFICULTY_LEVELS})


# ==================== 学生管理 ====================

@app.route('/api/student/create', methods=['POST'])
def create_student():
    """创建或获取学生"""
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': '学生名字不能为空'}), 400
    
    student = DatabaseService.create_student(name)
    return jsonify({
        'success': True,
        'student': student.to_dict()
    })


@app.route('/api/student/<int:student_id>')
def get_student(student_id):
    """获取学生信息"""
    student = DatabaseService.get_student(student_id)
    if not student:
        return jsonify({'error': '学生不存在'}), 404
    
    return jsonify(student.to_dict())


@app.route('/api/students')
def list_students():
    """列出所有学生"""
    students = DatabaseService.list_students()
    return jsonify({
        'students': [s.to_dict() for s in students]
    })


# ==================== 错题管理 ====================

@app.route('/api/question/add', methods=['POST'])
def add_wrong_question():
    """添加错题"""
    data = request.json
    student_id = data.get('student_id')
    
    # 验证必需字段
    required_fields = ['subject', 'difficulty', 'question_content', 'knowledge_point', 'correct_answer']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} 不能为空'}), 400
    
    # 验证科目和难度
    if data['subject'] not in SUBJECTS:
        return jsonify({'error': '无效的科目'}), 400
    if data['difficulty'] not in DIFFICULTY_LEVELS:
        return jsonify({'error': '无效的难度'}), 400
    
    try:
        question = DatabaseService.add_wrong_question(student_id, data)
        return jsonify({
            'success': True,
            'question': question.to_dict(),
            'message': '错题已保存'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/questions/<int:student_id>')
def get_questions(student_id):
    """获取学生的错题列表"""
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty')
    
    questions = DatabaseService.get_student_wrong_questions(student_id, subject, difficulty)
    
    return jsonify({
        'total': len(questions),
        'questions': [q.to_dict() for q in questions]
    })


@app.route('/api/question/<int:question_id>', methods=['PUT'])
def update_question(question_id):
    """更新错题（标记复习等）"""
    data = request.json
    
    question = DatabaseService.update_wrong_question(question_id, data)
    if not question:
        return jsonify({'error': '错题不存在'}), 404
    
    return jsonify({
        'success': True,
        'question': question.to_dict()
    })


@app.route('/api/question/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """删除错题"""
    if DatabaseService.delete_wrong_question(question_id):
        return jsonify({'success': True, 'message': '错题已删除'})
    return jsonify({'error': '错题不存在'}), 404


# ==================== 试卷生成 ====================

@app.route('/api/exam/generate', methods=['POST'])
def generate_exam():
    """生成试卷"""
    data = request.json
    student_id = data.get('student_id')
    exam_type = data.get('type', 'normal')  # normal, focused, mixed
    subject = data.get('subject')
    difficulty = data.get('difficulty')
    question_count = data.get('question_count', 10)
    
    # 获取错题
    questions = DatabaseService.get_student_wrong_questions(student_id, subject, difficulty)
    
    if not questions:
        return jsonify({'error': '没有错题可用于生成试卷'}), 400
    
    try:
        # 根据类型生成试卷
        if exam_type == 'focused':
            result = exam_gen.generate_focused_exam(questions)
        elif exam_type == 'mixed':
            result = exam_gen.generate_mixed_exam(questions, question_count)
        else:
            result = exam_gen.generate_exam(questions, subject, difficulty, question_count)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # 保存试卷
        exam_data = {
            'name': data.get('name', f'试卷-{datetime.now().strftime("%Y%m%d%H%M%S")}'),
            'subject': subject or '综合',
            'total_questions': result['exam_info']['total_questions'],
            'total_score': result['exam_info']['total_score'],
            'difficulty_distribution': result['exam_info'].get('difficulty_distribution'),
            'question_ids': [q.id for q in result['questions']]
        }
        
        exam = DatabaseService.save_generated_exam(student_id, exam_data)
        
        return jsonify({
            'success': True,
            'exam': {
                'id': exam.id,
                'name': exam.name,
                'total_questions': exam.total_questions,
                'total_score': exam.total_score,
                'difficulty_distribution': exam.difficulty_distribution
            },
            'questions': [
                {
                    'id': q.id,
                    'subject': q.subject,
                    'difficulty': q.difficulty,
                    'question_type': q.question_type,
                    'content': q.question_content,
                    'knowledge_point': q.knowledge_point,
                    'answer': q.correct_answer,
                    'explanation': q.explanation
                }
                for q in result['questions']
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/exams/<int:student_id>')
def get_exams(student_id):
    """获取学生生成的试卷列表"""
    exams = DatabaseService.get_student_exams(student_id)
    return jsonify({
        'total': len(exams),
        'exams': [e.to_dict() for e in exams]
    })


# ==================== 统计和分析 ====================

@app.route('/api/stats/<int:student_id>')
def get_stats(student_id):
    """获取学生学习统计"""
    stats = DatabaseService.get_student_stats(student_id)
    if not stats:
        return jsonify({'error': '统计不存在'}), 404
    
    return jsonify(stats)


@app.route('/api/stats/<int:student_id>/subjects')
def get_subject_stats(student_id):
    """获取各科目统计"""
    stats = DatabaseService.get_subject_statistics(student_id)
    return jsonify(stats)


@app.route('/api/stats/<int:student_id>/knowledge-points')
def get_knowledge_stats(student_id):
    """获取知识点统计"""
    stats = DatabaseService.get_knowledge_point_statistics(student_id)
    return jsonify(stats)


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': '页面不存在'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': '服务器错误'}), 500


if __name__ == '__main__':
    # 支持Heroku环境
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
