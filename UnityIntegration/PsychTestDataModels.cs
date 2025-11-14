using System;
using System.Collections.Generic;
using UnityEngine;

namespace PsychTestSystem
{
    /// <summary>
    /// JWT令牌响应
    /// </summary>
    [Serializable]
    public class TokenResponse
    {
        public string access_token;
        public string token_type;
    }
    
    /// <summary>
    /// 学生验证请求
    /// </summary>
    [Serializable]
    public class StudentValidationRequest
    {
        public string student_id;
    }
    
    /// <summary>
    /// 学生验证响应
    /// </summary>
    [Serializable]
    public class StudentValidationResult
    {
        public bool exists;
        public StudentInfo student_info;
    }
    
    /// <summary>
    /// 学生信息
    /// </summary>
    [Serializable]
    public class StudentInfo
    {
        public string student_id;
        public string name;
        public string class_name;
        public string gender;
    }
    
    /// <summary>
    /// 问卷得分
    /// </summary>
    [Serializable]
    public class QuestionnaireScores
    {
        public int anxiety;      // 焦虑
        public int depression;   // 抑郁
        public int stress;       // 压力
        
        // 为了与API兼容，提供中文属性名
        public int 焦虑
        {
            get => anxiety;
            set => anxiety = value;
        }
        
        public int 抑郁
        {
            get => depression;
            set => depression = value;
        }
        
        public int 压力
        {
            get => stress;
            set => stress = value;
        }
    }
    
    /// <summary>
    /// 生理数据
    /// </summary>
    [Serializable]
    public class PhysiologicalData
    {
        public float heart_rate;    // 心率
        public float eeg_alpha;     // 脑电alpha
        
        // 为了与API兼容，提供中文属性名
        public float 心率
        {
            get => heart_rate;
            set => heart_rate = value;
        }
        
        public float 脑电alpha
        {
            get => eeg_alpha;
            set => eeg_alpha = value;
        }
    }
    
    /// <summary>
    /// 客户端检测数据
    /// </summary>
    [Serializable]
    public class ClientTestData
    {
        public string student_id;
        public string name;
        public string gender;
        public int age;
        public string class_name;
        public string test_time;
        public QuestionnaireScores questionnaire_scores;
        public PhysiologicalData physiological_data_summary;
        public string ai_summary;
        public string report_file_path;
        
        /// <summary>
        /// 构造函数
        /// </summary>
        public ClientTestData()
        {
            questionnaire_scores = new QuestionnaireScores();
            physiological_data_summary = new PhysiologicalData();
            test_time = DateTime.Now.ToString("yyyy-MM-ddTHH:mm:ss");
        }
        
        /// <summary>
        /// 设置检测时间
        /// </summary>
        /// <param name="dateTime">检测时间</param>
        public void SetTestTime(DateTime dateTime)
        {
            test_time = dateTime.ToString("yyyy-MM-ddTHH:mm:ss");
        }
        
        /// <summary>
        /// 设置问卷得分
        /// </summary>
        /// <param name="anxiety">焦虑得分</param>
        /// <param name="depression">抑郁得分</param>
        /// <param name="stress">压力得分</param>
        public void SetQuestionnaireScores(int anxiety, int depression, int stress)
        {
            questionnaire_scores.anxiety = anxiety;
            questionnaire_scores.depression = depression;
            questionnaire_scores.stress = stress;
        }
        
        /// <summary>
        /// 设置生理数据
        /// </summary>
        /// <param name="heartRate">心率</param>
        /// <param name="eegAlpha">脑电alpha</param>
        public void SetPhysiologicalData(float heartRate, float eegAlpha)
        {
            physiological_data_summary.heart_rate = heartRate;
            physiological_data_summary.eeg_alpha = eegAlpha;
        }
    }
    
    /// <summary>
    /// 检测数据上传结果
    /// </summary>
    [Serializable]
    public class TestDataUploadResult
    {
        public int id;
        public int student_fk_id;
        public string test_time;
        public string ai_summary;
        public string report_file_path;
        public bool is_abnormal;
        public string status;
        public StudentDetail student;
        public List<ScoreDetail> scores;
        public List<PhysiologicalDataDetail> physiological_data;
    }
    
    /// <summary>
    /// 学生详细信息
    /// </summary>
    [Serializable]
    public class StudentDetail
    {
        public int id;
        public string student_id;
        public string name;
        public string class_name;
        public string gender;
        public string created_at;
    }
    
    /// <summary>
    /// 得分详情
    /// </summary>
    [Serializable]
    public class ScoreDetail
    {
        public int id;
        public string module_name;
        public int score;
    }
    
    /// <summary>
    /// 生理数据详情
    /// </summary>
    [Serializable]
    public class PhysiologicalDataDetail
    {
        public int id;
        public string data_key;
        public float data_value;
    }
    
    /// <summary>
    /// 检测状态结果
    /// </summary>
    [Serializable]
    public class TestStatusResult
    {
        public string student_id;
        public string status;
        public bool is_abnormal;
        public string latest_test_time;
        public int test_record_count;
    }
    
    /// <summary>
    /// 学生模型（用于API响应）
    /// </summary>
    [Serializable]
    public class Student
    {
        public int id;
        public string student_id;
        public string name;
        public string class_name;
        public string gender;
        public string created_at;
    }
    
    /// <summary>
    /// 检测记录详情
    /// </summary>
    [Serializable]
    public class TestRecordDetail
    {
        public int id;
        public int student_fk_id;
        public string test_time;
        public string ai_summary;
        public string report_file_path;
        public bool is_abnormal;
        public string status;
        public StudentDetail student;
        public List<ScoreDetail> scores;
        public List<PhysiologicalDataDetail> physiological_data;
    }
    
    /// <summary>
    /// 仪表板统计数据
    /// </summary>
    [Serializable]
    public class DashboardStats
    {
        public int total_students;
        public int total_records;
        public int abnormal_count;
        public int today_records;
    }
    
    /// <summary>
    /// 趋势数据
    /// </summary>
    [Serializable]
    public class TrendData
    {
        public List<string> dates;
        public List<int> values;
    }
    
    /// <summary>
    /// 得分统计
    /// </summary>
    [Serializable]
    public class ScoreStats
    {
        public ScoreDistribution anxiety;    // 焦虑
        public ScoreDistribution depression; // 抑郁
        public ScoreDistribution stress;     // 压力
        
        // 为了与API兼容，提供中文属性名
        public ScoreDistribution 焦虑
        {
            get => anxiety;
            set => anxiety = value;
        }
        
        public ScoreDistribution 抑郁
        {
            get => depression;
            set => depression = value;
        }
        
        public ScoreDistribution 压力
        {
            get => stress;
            set => stress = value;
        }
    }
    
    /// <summary>
    /// 得分分布
    /// </summary>
    [Serializable]
    public class ScoreDistribution
    {
        public int range_0_10;
        public int range_11_15;
        public int range_16_20;
        public int range_21_25;
        public int range_26_30;
        
        // 为了与API兼容，提供中文属性名
        public int range_0_10_zh
        {
            get => range_0_10;
            set => range_0_10 = value;
        }
        
        public int range_11_15_zh
        {
            get => range_11_15;
            set => range_11_15 = value;
        }
        
        public int range_16_20_zh
        {
            get => range_16_20;
            set => range_16_20 = value;
        }
        
        public int range_21_25_zh
        {
            get => range_21_25;
            set => range_21_25 = value;
        }
        
        public int range_26_30_zh
        {
            get => range_26_30;
            set => range_26_30 = value;
        }
    }
    
    /// <summary>
    /// 班级分布
    /// </summary>
    [Serializable]
    public class ClassDistribution
    {
        // 使用Dictionary<string, int>来表示班级名称和人数
        // 在Unity中，我们可以使用SerializableDictionary或者简单的字符串表示
        public string class_data; // JSON字符串格式的班级分布数据
    }
    
    /// <summary>
    /// API错误响应
    /// </summary>
    [Serializable]
    public class APIError
    {
        public string detail;
        public int status_code;
    }
    
    /// <summary>
    /// 检测状态枚举
    /// </summary>
    public enum TestStatus
    {
        NotStarted,     // 未开始
        InProgress,     // 进行中
        Completed,      // 已完成
        Pending,        // 待处理
        Processing,     // 处理中
        Failed          // 失败
    }
    
    /// <summary>
    /// 性别枚举
    /// </summary>
    public enum Gender
    {
        Male,   // 男
        Female  // 女
    }
}



