using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

namespace PsychTestSystem
{
    /// <summary>
    /// 心理检测系统工具类
    /// 提供常用的辅助功能
    /// </summary>
    public static class PsychTestUtils
    {
        /// <summary>
        /// 验证学号格式
        /// </summary>
        /// <param name="studentId">学号</param>
        /// <returns>是否有效</returns>
        public static bool ValidateStudentId(string studentId)
        {
            if (string.IsNullOrEmpty(studentId))
                return false;
            
            // 学号长度检查（根据实际需求调整）
            if (studentId.Length < 3 || studentId.Length > 20)
                return false;
            
            // 学号格式检查（可以根据实际规则调整）
            // 这里假设学号以字母开头，后跟数字
            if (!char.IsLetter(studentId[0]))
                return false;
            
            return true;
        }
        
        /// <summary>
        /// 验证姓名格式
        /// </summary>
        /// <param name="name">姓名</param>
        /// <returns>是否有效</returns>
        public static bool ValidateName(string name)
        {
            if (string.IsNullOrEmpty(name))
                return false;
            
            // 姓名长度检查
            if (name.Length < 2 || name.Length > 20)
                return false;
            
            // 检查是否包含非法字符
            foreach (char c in name)
            {
                if (!char.IsLetter(c) && c != '·' && c != ' ')
                    return false;
            }
            
            return true;
        }
        
        /// <summary>
        /// 验证年龄
        /// </summary>
        /// <param name="age">年龄</param>
        /// <returns>是否有效</returns>
        public static bool ValidateAge(int age)
        {
            return age >= 1 && age <= 100;
        }
        
        /// <summary>
        /// 验证问卷得分
        /// </summary>
        /// <param name="score">得分</param>
        /// <param name="maxScore">最大得分</param>
        /// <returns>是否有效</returns>
        public static bool ValidateQuestionnaireScore(int score, int maxScore = 30)
        {
            return score >= 0 && score <= maxScore;
        }
        
        /// <summary>
        /// 验证生理数据
        /// </summary>
        /// <param name="value">数值</param>
        /// <param name="minValue">最小值</param>
        /// <param name="maxValue">最大值</param>
        /// <returns>是否有效</returns>
        public static bool ValidatePhysiologicalData(float value, float minValue, float maxValue)
        {
            return value >= minValue && value <= maxValue;
        }
        
        /// <summary>
        /// 验证心率
        /// </summary>
        /// <param name="heartRate">心率</param>
        /// <returns>是否有效</returns>
        public static bool ValidateHeartRate(float heartRate)
        {
            return ValidatePhysiologicalData(heartRate, 40f, 200f);
        }
        
        /// <summary>
        /// 验证脑电alpha值
        /// </summary>
        /// <param name="eegAlpha">脑电alpha值</param>
        /// <returns>是否有效</returns>
        public static bool ValidateEEGAlpha(float eegAlpha)
        {
            return ValidatePhysiologicalData(eegAlpha, 1f, 50f);
        }
        
        /// <summary>
        /// 生成安全的文件名
        /// </summary>
        /// <param name="originalName">原始文件名</param>
        /// <returns>安全的文件名</returns>
        public static string GenerateSafeFileName(string originalName)
        {
            if (string.IsNullOrEmpty(originalName))
                return "unnamed_file";
            
            // 移除或替换非法字符
            char[] invalidChars = Path.GetInvalidFileNameChars();
            string safeName = originalName;
            
            foreach (char c in invalidChars)
            {
                safeName = safeName.Replace(c, '_');
            }
            
            // 限制长度
            if (safeName.Length > 100)
            {
                safeName = safeName.Substring(0, 100);
            }
            
            return safeName;
        }
        
        /// <summary>
        /// 生成报告文件名
        /// </summary>
        /// <param name="studentName">学生姓名</param>
        /// <param name="studentId">学号</param>
        /// <param name="extension">文件扩展名</param>
        /// <returns>报告文件名</returns>
        public static string GenerateReportFileName(string studentName, string studentId, string extension = "pdf")
        {
            string safeName = GenerateSafeFileName(studentName);
            string safeId = GenerateSafeFileName(studentId);
            string timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            
            return $"{safeName}_{safeId}_{timestamp}.{extension}";
        }
        
        /// <summary>
        /// 格式化时间戳
        /// </summary>
        /// <param name="dateTime">时间</param>
        /// <returns>格式化的时间字符串</returns>
        public static string FormatTimestamp(DateTime dateTime)
        {
            return dateTime.ToString("yyyy-MM-ddTHH:mm:ss");
        }
        
        /// <summary>
        /// 解析时间戳
        /// </summary>
        /// <param name="timestamp">时间戳字符串</param>
        /// <returns>DateTime对象</returns>
        public static DateTime ParseTimestamp(string timestamp)
        {
            if (DateTime.TryParse(timestamp, out DateTime result))
            {
                return result;
            }
            
            return DateTime.Now;
        }
        
        /// <summary>
        /// 计算文件大小（MB）
        /// </summary>
        /// <param name="bytes">字节数</param>
        /// <returns>MB大小</returns>
        public static float CalculateFileSizeMB(byte[] bytes)
        {
            if (bytes == null)
                return 0f;
            
            return bytes.Length / (1024f * 1024f);
        }
        
        /// <summary>
        /// 检查文件大小是否超出限制
        /// </summary>
        /// <param name="bytes">文件字节数组</param>
        /// <param name="maxSizeMB">最大大小（MB）</param>
        /// <returns>是否超出限制</returns>
        public static bool IsFileSizeExceeded(byte[] bytes, float maxSizeMB)
        {
            float fileSizeMB = CalculateFileSizeMB(bytes);
            return fileSizeMB > maxSizeMB;
        }
        
        /// <summary>
        /// 创建示例PDF内容
        /// </summary>
        /// <param name="studentName">学生姓名</param>
        /// <param name="studentId">学号</param>
        /// <param name="testTime">检测时间</param>
        /// <returns>PDF字节数组</returns>
        public static byte[] CreateSamplePDFContent(string studentName, string studentId, DateTime testTime)
        {
            string pdfContent = $@"%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length {100 + studentName.Length + studentId.Length}
>>
stream
BT
/F1 12 Tf
72 720 Td
(心理检测报告) Tj
0 -20 Td
(学生姓名: {studentName}) Tj
0 -20 Td
(学号: {studentId}) Tj
0 -20 Td
(检测时间: {testTime:yyyy-MM-dd HH:mm:ss}) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000204 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
{300 + studentName.Length + studentId.Length}
%%EOF";
            
            return Encoding.UTF8.GetBytes(pdfContent);
        }
        
        /// <summary>
        /// 验证检测数据的完整性
        /// </summary>
        /// <param name="testData">检测数据</param>
        /// <returns>验证结果</returns>
        public static ValidationResult ValidateTestData(ClientTestData testData)
        {
            var result = new ValidationResult();
            
            // 验证基本信息
            if (!ValidateStudentId(testData.student_id))
            {
                result.AddError("学号格式不正确");
            }
            
            if (!ValidateName(testData.name))
            {
                result.AddError("姓名格式不正确");
            }
            
            if (!ValidateAge(testData.age))
            {
                result.AddError("年龄必须在1-100之间");
            }
            
            // 验证问卷得分
            if (testData.questionnaire_scores != null)
            {
                if (!ValidateQuestionnaireScore(testData.questionnaire_scores.anxiety))
                {
                    result.AddError("焦虑得分必须在0-30之间");
                }
                
                if (!ValidateQuestionnaireScore(testData.questionnaire_scores.depression))
                {
                    result.AddError("抑郁得分必须在0-30之间");
                }
                
                if (!ValidateQuestionnaireScore(testData.questionnaire_scores.stress))
                {
                    result.AddError("压力得分必须在0-30之间");
                }
            }
            
            // 验证生理数据
            if (testData.physiological_data_summary != null)
            {
                if (!ValidateHeartRate(testData.physiological_data_summary.heart_rate))
                {
                    result.AddError("心率必须在40-200之间");
                }
                
                if (!ValidateEEGAlpha(testData.physiological_data_summary.eeg_alpha))
                {
                    result.AddError("脑电alpha值必须在1-50之间");
                }
            }
            
            // 验证AI总结
            if (string.IsNullOrEmpty(testData.ai_summary))
            {
                result.AddError("AI总结不能为空");
            }
            else if (testData.ai_summary.Length > 1000)
            {
                result.AddError("AI总结长度不能超过1000字符");
            }
            
            return result;
        }
        
        /// <summary>
        /// 获取性别显示文本
        /// </summary>
        /// <param name="gender">性别枚举</param>
        /// <returns>显示文本</returns>
        public static string GetGenderDisplayText(Gender gender)
        {
            switch (gender)
            {
                case Gender.Male:
                    return "男";
                case Gender.Female:
                    return "女";
                default:
                    return "未知";
            }
        }
        
        /// <summary>
        /// 获取检测状态显示文本
        /// </summary>
        /// <param name="status">状态字符串</param>
        /// <returns>显示文本</returns>
        public static string GetTestStatusDisplayText(string status)
        {
            switch (status?.ToLower())
            {
                case "not_started":
                    return "未开始";
                case "in_progress":
                    return "进行中";
                case "completed":
                    return "已完成";
                case "pending":
                    return "待处理";
                case "processing":
                    return "处理中";
                case "failed":
                    return "失败";
                default:
                    return "未知状态";
            }
        }
        
        /// <summary>
        /// 格式化文件大小
        /// </summary>
        /// <param name="bytes">字节数</param>
        /// <returns>格式化的文件大小字符串</returns>
        public static string FormatFileSize(long bytes)
        {
            string[] sizes = { "B", "KB", "MB", "GB" };
            double len = bytes;
            int order = 0;
            
            while (len >= 1024 && order < sizes.Length - 1)
            {
                order++;
                len = len / 1024;
            }
            
            return $"{len:0.##} {sizes[order]}";
        }
    }
    
    /// <summary>
    /// 验证结果类
    /// </summary>
    public class ValidationResult
    {
        private List<string> errors = new List<string>();
        private List<string> warnings = new List<string>();
        
        public bool IsValid => errors.Count == 0;
        public IReadOnlyList<string> Errors => errors.AsReadOnly();
        public IReadOnlyList<string> Warnings => warnings.AsReadOnly();
        
        public void AddError(string error)
        {
            if (!string.IsNullOrEmpty(error))
                errors.Add(error);
        }
        
        public void AddWarning(string warning)
        {
            if (!string.IsNullOrEmpty(warning))
                warnings.Add(warning);
        }
        
        public string GetErrorSummary()
        {
            if (errors.Count == 0)
                return "验证通过";
            
            return string.Join("; ", errors);
        }
        
        public string GetWarningSummary()
        {
            if (warnings.Count == 0)
                return "";
            
            return string.Join("; ", warnings);
        }
    }
}



