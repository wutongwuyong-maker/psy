import os
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd

from psy_admin_fastapi.models import Student, Test, Score, PhysiologicalData

# 报告存储目录配置
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# 注册中文字体
try:
    # 尝试使用系统中文字体
    pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
    pdfmetrics.registerFont(TTFont('SimHei', 'C:/Windows/Fonts/simhei.ttf'))
    chinese_font = 'SimSun'
except:
    try:
        # 如果系统字体不可用，尝试使用reportlab自带的中文字体
        from reportlab.lib.fonts import addMapping
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
        chinese_font = 'STSong-Light'
    except:
        # 如果都没有，使用默认字体（可能会有中文显示问题）
        chinese_font = 'Helvetica'

def generate_report_content(db: Session, student_id: str) -> str:
    """生成学生检测报告的文本内容"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    tests = db.query(Test).join(Student).filter(Student.id == student.id).all()
    if not tests:
        return "该学生暂无检测记录"

    # 构建报告内容框架
    content = [
        "=== 学生检测报告 ===",
        f"学生姓名: {student.name}",
        f"学号: {student.student_id}",
        f"班级: {student.class_name}",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # 添加每条检测记录的详细信息
    for idx, test in enumerate(tests, 1):
        content.extend([
            f"--- 检测记录 {idx} ---",
            f"检测时间: {test.test_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"AI评估总结: {test.ai_summary or '无'}",
            f"是否异常: {'是' if test.is_abnormal else '否'}",
        ])

        # 添加问卷得分
        scores = db.query(Score).filter(Score.test_fk_id == test.id).all()
        if scores:
            content.append("问卷得分:")
            content.extend([f"- {s.module_name}: {s.score}" for s in scores])

        # 添加生理数据
        phys_data = db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == test.id).all()
        if phys_data:
            content.append("生理数据:")
            content.extend([f"- {d.data_key}: {d.data_value}" for d in phys_data])

        content.append("")  # 空行分隔

    return "\n".join(content)

def generate_pdf_report(content: str, student_id: str, student_name: str = "Student") -> str:
    """生成PDF格式报告文件"""
    # 注意：避免在此函数内创建新的数据库会话。
    # 文件命名按学号生成，若需要姓名请在调用方查询并传入后再调整此处逻辑。
    
    # 使用 {姓名}_{学号}.pdf 格式
    safe_name = "".join(c for c in student_name if c.isalnum() or c in (" ", "-", "_"))
    filename = f"{safe_name}_{student_id}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)

    # 创建PDF文档
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    margin = 50
    y_pos = height - margin

    # 设置中文字体和内容
    c.setFont(chinese_font, 12)
    for line in content.split("\n"):
        if y_pos < margin:
            c.showPage()
            c.setFont(chinese_font, 12)
            y_pos = height - margin
        c.drawString(margin, y_pos, line)
        y_pos -= 15  # 行间距

    c.save()
    return filepath

def generate_excel_report(db: Session, student_id: str) -> str:
    """生成Excel格式报告文件"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    tests = db.query(Test).join(Student).filter(Student.id == student.id).all()
    if not tests:
        raise ValueError("No test records")

    # 整理数据为DataFrame
    data = []
    for test in tests:
        # 基础信息行
        base_info = {
            "学生姓名": student.name,
            "学号": student.student_id,
            "班级": student.class_name,
            "检测时间": test.test_time.strftime("%Y-%m-%d %H:%M:%S"),
            "AI总结": test.ai_summary or "无",
            "是否异常": "是" if test.is_abnormal else "否",
            "数据类型": None,
            "项目名称": None,
            "数值": None
        }

        # 添加问卷得分数据
        for score in db.query(Score).filter(Score.test_fk_id == test.id).all():
            row = base_info.copy()
            row.update({
                "数据类型": "问卷得分",
                "项目名称": score.module_name,
                "数值": score.score
            })
            data.append(row)

        # 添加生理数据
        for phys in db.query(PhysiologicalData).filter(PhysiologicalData.test_fk_id == test.id).all():
            row = base_info.copy()
            row.update({
                "数据类型": "生理数据",
                "项目名称": phys.data_key,
                "数值": phys.data_value
            })
            data.append(row)

    # 生成Excel文件
    df = pd.DataFrame(data)
    # 使用 {姓名}_{学号}.xlsx 格式
    safe_name = "".join(c for c in student.name if c.isalnum() or c in (" ", "-", "_"))
    filename = f"{safe_name}_{student_id}.xlsx"
    filepath = os.path.join(REPORT_DIR, filename)
    df.to_excel(filepath, index=False)

    return filepath
