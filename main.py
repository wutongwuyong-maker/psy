import os
import csv
import json
import random
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ================== 可调参数 ==================
OUTPUT_DIR = r"D:\testcase"   # 输出根目录
PDF_SUBDIR = "pdfs"           # PDF 子目录
COUNT = 100                    # 生成份数

CSV_PATH = os.path.join(OUTPUT_DIR, "files.csv")


# ================== 工具函数 ==================
def log(msg: str):
    print(f"[creat_testcase] {msg}")


def gen_student_id(used):
    """生成不重复学号：STU001000 ~ STU999999"""
    while True:
        n = random.randint(000000, 100)
        sid = f"STU{n:06d}"
        if sid not in used:
            used.add(sid)
            return sid


def random_name():
    surnames = list("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳唐罗")
    given = "一二三四五六七八九十子文宇涵晨阳浩杰磊楠琪雪婷颖丽博凯明瑞轩泽霖桐晗瑶昕晨可欣梓萱子墨奕辰浩然雨桐子涵诗涵思宇"
    return random.choice(surnames) + "".join(random.sample(given, k=random.choice([1, 2])))


def random_class():
    grade = random.randint(1, 12)
    clazz = random.randint(1, 15)
    return f"{grade}年级{clazz}班"


def now_str():
    """PDF 用的人类可读时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso():
    """test_data 用的 ISO 时间：2025-11-10T15:29:19"""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def pick_ai_summary():
    """同时作为 ai_summary 和 AI_feedback 内容"""
    return random.choice([
        "整体心理状态良好，可保持当前学习与生活节奏。",
        "存在一定紧张和焦虑，建议适当安排休息与放松活动。",
        "情绪波动稍明显，建议与老师或家长多沟通，及时疏导。",
        "部分量表得分偏高，建议进一步关注情绪变化并考虑专业支持。",
        "状态整体稳定，能较好应对学习与人际压力。"
    ])


def score_to_level(score: int, max_score: int) -> str:
    if max_score <= 0:
        return "正常"
    ratio = score / max_score
    if ratio >= 0.7:
        return "高分"
    elif ratio <= 0.3:
        return "低分"
    else:
        return "正常"


def gen_questionnaire_scores():
    """生成四个问卷模块"""
    modules = {
        "学习焦虑": 15,
        "对人焦虑": 10,
        "孤独倾向": 10,
        "自责倾向": 10,
    }

    result = {}

    for name, max_score in modules.items():
        score = random.randint(0, max_score)
        level = score_to_level(score, max_score)

        if name == "学习焦虑":
            fb_high = "对学习和考试结果有较强担忧，建议调整备考节奏并寻求老师帮助。"
            fb_normal = "对学习有一定紧张感，但整体在可接受范围内。"
            fb_low = "学习焦虑水平较低，能较为平和地面对考试与作业。"
        elif name == "对人焦虑":
            fb_high = "在人际交往中较为紧张，较在意他人评价，建议循序渐进增进互动。"
            fb_normal = "在社交场合会有些紧张，但基本可以适应。"
            fb_low = "在人际相处中比较放松，自我感受积极。"
        elif name == "孤独倾向":
            fb_high = "有较强孤立感，建议多参加班级活动并主动与同伴互动。"
            fb_normal = "偶尔感到孤单，但整体社交状况尚可。"
            fb_low = "孤独感较少，能够较好融入集体生活。"
        else:  # 自责倾向
            fb_high = "容易把问题都归因于自己，建议学习更客观地看待成功和失败。"
            fb_normal = "遇到问题时能兼顾自我反思和外部因素。"
            fb_low = "自我评价较为积极，能正确面对挫折与失误。"

        if level == "高分":
            fb = fb_high
        elif level == "低分":
            fb = fb_low
        else:
            fb = fb_normal

        result[name] = {
            "score": score,
            "max_score": max_score,
            "level": level,
            "questionnaire_feedback": fb,
        }

    return result


def random_physiological_summary():
    return {
        "心率": random.randint(50, 120),
        "脑电alpha": round(random.uniform(5.0, 15.0), 1),
    }


def ensure_dir(path):
    if not os.path.isdir(path):
        log(f"目录不存在，正在创建：{path}")
        os.makedirs(path, exist_ok=True)
    else:
        log(f"目录已存在：{path}")


# ================== 生成 PDF ==================
def make_pdf(report_path, data):
    """
    data: {
      name, student_id, class_name, gender, age,
      gen_time, test_time,
      questionnaire_scores, physiological_data_summary,
      ai_summary
    }
    """
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    c = canvas.Canvas(report_path, pagesize=A4)
    c.setFont('STSong-Light', 12)

    width, height = A4
    x, y = 50, height - 60
    gap = 20

    def line(txt, g=gap):
        nonlocal y
        c.drawString(x, y, txt)
        y -= g

    # 标题
    c.setFont('STSong-Light', 16)
    line("=== 学生检测报告 ===", 28)
    c.setFont('STSong-Light', 12)

    # 基本信息
    line(f"学生姓名: {data['name']}")
    line(f"性别: {data['gender']}")
    line(f"年龄: {data['age']}")
    line(f"学号: {data['student_id']}")
    line(f"班级: {data['class_name']}")
    line(f"报告生成时间: {data['gen_time']}")
    line("")  # 空行

    # 检测记录
    line("--- 检测记录 1 ---", 24)
    line(f"检测时间: {data['test_time']}")
    line(f"AI 综合反馈: {data['ai_summary']}")
    line("问卷得分:")

    qs = data["questionnaire_scores"]
    for dim, v in qs.items():
        line(f"* {dim}: {v['score']}/{v['max_score']}（{v['level']}）")

    line("  生理数据:")
    phys = data["physiological_data_summary"]
    for k, v in phys.items():
        line(f"* {k}: {v}")

    c.showPage()
    c.save()


# ================== 主流程 ==================
def main():
    log(f"脚本启动，输出目录：{OUTPUT_DIR}")
    ensure_dir(OUTPUT_DIR)

    pdf_dir = os.path.join(OUTPUT_DIR, PDF_SUBDIR)
    ensure_dir(pdf_dir)

    log(f"CSV 将写入：{CSV_PATH}")

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=["file_path", "test_data"])
        writer.writeheader()

        used_ids = set()

        for i in range(COUNT):
            log(f"生成第 {i + 1}/{COUNT} 份测试数据")

            student_id = gen_student_id(used_ids)
            name = random_name()
            class_name = random_class()
            gender = random.choice(["男", "女"])
            age = random.randint(6, 18)   # 只用于 PDF 显示，不进 test_data

            gen_time = now_str()
            test_time = now_iso()
            ai_summary = pick_ai_summary()  # 兼作 ai_summary + AI_feedback

            questionnaire_scores = gen_questionnaire_scores()
            phys_summary = random_physiological_summary()

            # ---- 生成 PDF ----
            pdf_name = f"{student_id}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_name)
            log(f"  生成 PDF：{pdf_path}")

            make_pdf(pdf_path, {
                "name": name,
                "gender": gender,
                "age": age,
                "student_id": student_id,
                "class_name": class_name,
                "gen_time": gen_time,
                "test_time": test_time,
                "questionnaire_scores": questionnaire_scores,
                "physiological_data_summary": phys_summary,
                "ai_summary": ai_summary,
            })

            # ---- 生成 test_data（不再包含 age，避免 Student(age=...) 报错）----
            relative_pdf_path = f"{PDF_SUBDIR}/{pdf_name}"

            test_data_obj = {
                "student_id": student_id,
                "name": name,
                "gender": gender,
                # "age": age,  # ❌ 不发给后端，避免 'age' is an invalid keyword argument for Student
                "class_name": class_name,
                "test_time": test_time,
                "questionnaire_scores": questionnaire_scores,
                "physiological_data_summary": phys_summary,
                # 你要求保留的两个字段：
                "ai_summary": ai_summary,
                "report_file_path": relative_pdf_path,
                # 新字段：和 ai_summary 内容一致
                "AI_feedback": ai_summary,
            }

            writer.writerow({
                "file_path": relative_pdf_path,
                "test_data": json.dumps(test_data_obj, ensure_ascii=False)
            })

    log(f"已生成 {COUNT} 份 PDF 到：{pdf_dir}")
    log(f"已写入 CSV：{CSV_PATH}")
    log("完成。")


if __name__ == "__main__":
    main()
