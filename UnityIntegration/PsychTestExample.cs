using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UI;

namespace PsychTestSystem
{
    /// <summary>
    /// 心理检测系统使用示例
    /// 展示如何在Unity中使用PsychTestAPIClient发送数据
    /// </summary>
    public class PsychTestExample : MonoBehaviour
    {
        [Header("UI组件")]
        [SerializeField] private Button authenticateButton;
        [SerializeField] private Button validateStudentButton;
        [SerializeField] private Button uploadTestDataButton;
        [SerializeField] private Button getStatusButton;
        [SerializeField] private InputField studentIdInput;
        [SerializeField] private InputField studentNameInput;
        [SerializeField] private InputField classNameInput;
        [SerializeField] private Dropdown genderDropdown;
        [SerializeField] private InputField ageInput;
        [SerializeField] private InputField anxietyScoreInput;
        [SerializeField] private InputField depressionScoreInput;
        [SerializeField] private InputField stressScoreInput;
        [SerializeField] private InputField heartRateInput;
        [SerializeField] private InputField eegAlphaInput;
        [SerializeField] private InputField aiSummaryInput;
        [SerializeField] private Text statusText;
        [SerializeField] private Text resultText;
        
        [Header("API客户端")]
        [SerializeField] private PsychTestAPIClient apiClient;
        
        private void Start()
        {
            // 初始化UI
            InitializeUI();
            
            // 订阅API客户端事件
            SubscribeToEvents();
            
            // 设置默认值
            SetDefaultValues();
        }
        
        private void InitializeUI()
        {
            // 绑定按钮事件
            if (authenticateButton != null)
                authenticateButton.onClick.AddListener(OnAuthenticateClicked);
            
            if (validateStudentButton != null)
                validateStudentButton.onClick.AddListener(OnValidateStudentClicked);
            
            if (uploadTestDataButton != null)
                uploadTestDataButton.onClick.AddListener(OnUploadTestDataClicked);
            
            if (getStatusButton != null)
                getStatusButton.onClick.AddListener(OnGetStatusClicked);
            
            // 初始化性别下拉框
            if (genderDropdown != null)
            {
                genderDropdown.ClearOptions();
                genderDropdown.AddOptions(new System.Collections.Generic.List<string> { "男", "女" });
            }
        }
        
        private void SubscribeToEvents()
        {
            if (apiClient != null)
            {
                apiClient.OnAuthenticationResult += OnAuthenticationResult;
                apiClient.OnStudentValidationResult += OnStudentValidationResult;
                apiClient.OnTestDataUploadResult += OnTestDataUploadResult;
                apiClient.OnTestStatusResult += OnTestStatusResult;
                apiClient.OnError += OnError;
            }
        }
        
        private void SetDefaultValues()
        {
            if (studentIdInput != null) studentIdInput.text = "U001";
            if (studentNameInput != null) studentNameInput.text = "张三";
            if (classNameInput != null) classNameInput.text = "计算机1班";
            if (ageInput != null) ageInput.text = "20";
            if (anxietyScoreInput != null) anxietyScoreInput.text = "8";
            if (depressionScoreInput != null) depressionScoreInput.text = "4";
            if (stressScoreInput != null) stressScoreInput.text = "12";
            if (heartRateInput != null) heartRateInput.text = "85";
            if (eegAlphaInput != null) eegAlphaInput.text = "13.2";
            if (aiSummaryInput != null) aiSummaryInput.text = "检测出高焦虑风险，建议进一步评估";
        }
        
        #region 按钮事件处理
        
        private void OnAuthenticateClicked()
        {
            UpdateStatus("正在进行身份验证...");
            apiClient?.Authenticate();
        }
        
        private void OnValidateStudentClicked()
        {
            string studentId = studentIdInput?.text;
            if (string.IsNullOrEmpty(studentId))
            {
                UpdateStatus("请输入学号");
                return;
            }
            
            UpdateStatus($"正在验证学号: {studentId}");
            apiClient?.ValidateStudent(studentId);
        }
        
        private void OnUploadTestDataClicked()
        {
            // 验证输入数据
            if (!ValidateInputData())
                return;
            
            // 创建检测数据
            ClientTestData testData = CreateTestData();
            
            // 创建示例PDF数据（实际使用中应该是真实的PDF文件）
            byte[] pdfData = CreateSamplePDFData();
            
            UpdateStatus("正在上传检测数据...");
            apiClient?.UploadTestData(testData, pdfData);
        }
        
        private void OnGetStatusClicked()
        {
            string studentId = studentIdInput?.text;
            if (string.IsNullOrEmpty(studentId))
            {
                UpdateStatus("请输入学号");
                return;
            }
            
            UpdateStatus($"正在查询学号 {studentId} 的检测状态...");
            apiClient?.GetStudentTestStatus(studentId);
        }
        
        #endregion
        
        #region 数据验证和创建
        
        private bool ValidateInputData()
        {
            if (string.IsNullOrEmpty(studentIdInput?.text))
            {
                UpdateStatus("请输入学号");
                return false;
            }
            
            if (string.IsNullOrEmpty(studentNameInput?.text))
            {
                UpdateStatus("请输入学生姓名");
                return false;
            }
            
            if (string.IsNullOrEmpty(classNameInput?.text))
            {
                UpdateStatus("请输入班级名称");
                return false;
            }
            
            if (!int.TryParse(ageInput?.text, out int age) || age <= 0)
            {
                UpdateStatus("请输入有效的年龄");
                return false;
            }
            
            if (!int.TryParse(anxietyScoreInput?.text, out int anxiety) || anxiety < 0)
            {
                UpdateStatus("请输入有效的焦虑得分");
                return false;
            }
            
            if (!int.TryParse(depressionScoreInput?.text, out int depression) || depression < 0)
            {
                UpdateStatus("请输入有效的抑郁得分");
                return false;
            }
            
            if (!int.TryParse(stressScoreInput?.text, out int stress) || stress < 0)
            {
                UpdateStatus("请输入有效的压力得分");
                return false;
            }
            
            if (!float.TryParse(heartRateInput?.text, out float heartRate) || heartRate <= 0)
            {
                UpdateStatus("请输入有效的心率");
                return false;
            }
            
            if (!float.TryParse(eegAlphaInput?.text, out float eegAlpha) || eegAlpha <= 0)
            {
                UpdateStatus("请输入有效的脑电alpha值");
                return false;
            }
            
            if (string.IsNullOrEmpty(aiSummaryInput?.text))
            {
                UpdateStatus("请输入AI总结");
                return false;
            }
            
            return true;
        }
        
        private ClientTestData CreateTestData()
        {
            ClientTestData testData = new ClientTestData();
            
            // 基本信息
            testData.student_id = studentIdInput.text;
            testData.name = studentNameInput.text;
            testData.gender = genderDropdown?.options[genderDropdown.value].text ?? "男";
            testData.age = int.Parse(ageInput.text);
            testData.class_name = classNameInput.text;
            
            // 设置检测时间
            testData.SetTestTime(DateTime.Now);
            
            // 问卷得分
            int anxiety = int.Parse(anxietyScoreInput.text);
            int depression = int.Parse(depressionScoreInput.text);
            int stress = int.Parse(stressScoreInput.text);
            testData.SetQuestionnaireScores(anxiety, depression, stress);
            
            // 生理数据
            float heartRate = float.Parse(heartRateInput.text);
            float eegAlpha = float.Parse(eegAlphaInput.text);
            testData.SetPhysiologicalData(heartRate, eegAlpha);
            
            // AI总结
            testData.ai_summary = aiSummaryInput.text;
            
            // 报告文件路径
            testData.report_file_path = $"reports/{testData.name}_{testData.student_id}_{DateTime.Now:yyyyMMdd_HHmmss}.pdf";
            
            return testData;
        }
        
        private byte[] CreateSamplePDFData()
        {
            // 这里创建一个简单的PDF文件内容作为示例
            // 实际使用中，你应该使用真实的PDF文件
            string pdfContent = @"%PDF-1.4
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
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(心理检测报告) Tj
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
297
%%EOF";
            
            return System.Text.Encoding.UTF8.GetBytes(pdfContent);
        }
        
        #endregion
        
        #region API事件回调
        
        private void OnAuthenticationResult(bool success)
        {
            if (success)
            {
                UpdateStatus("身份验证成功");
                UpdateResult("已获得访问令牌，可以开始使用API");
            }
            else
            {
                UpdateStatus("身份验证失败");
                UpdateResult("请检查用户名和密码配置");
            }
        }
        
        private void OnStudentValidationResult(StudentValidationResult result)
        {
            if (result.exists)
            {
                UpdateStatus($"学号 {result.student_info.student_id} 验证成功");
                UpdateResult($"学生信息: {result.student_info.name}, 班级: {result.student_info.class_name}, 性别: {result.student_info.gender}");
            }
            else
            {
                UpdateStatus($"学号不存在");
                UpdateResult("该学号在系统中不存在，请检查学号是否正确");
            }
        }
        
        private void OnTestDataUploadResult(TestDataUploadResult result)
        {
            UpdateStatus("检测数据上传成功");
            UpdateResult($"记录ID: {result.id}, 状态: {result.status}, 是否异常: {(result.is_abnormal ? "是" : "否")}");
        }
        
        private void OnTestStatusResult(TestStatusResult result)
        {
            UpdateStatus($"学号 {result.student_id} 检测状态查询成功");
            UpdateResult($"状态: {result.status}, 是否异常: {(result.is_abnormal ? "是" : "否")}, 检测次数: {result.test_record_count}");
        }
        
        private void OnError(string errorMessage)
        {
            UpdateStatus("操作失败");
            UpdateResult($"错误: {errorMessage}");
        }
        
        #endregion
        
        #region UI更新方法
        
        private void UpdateStatus(string message)
        {
            if (statusText != null)
            {
                statusText.text = $"[{DateTime.Now:HH:mm:ss}] {message}";
            }
            
            Debug.Log($"[PsychTestExample] {message}");
        }
        
        private void UpdateResult(string message)
        {
            if (resultText != null)
            {
                resultText.text = message;
            }
            
            Debug.Log($"[PsychTestExample] {message}");
        }
        
        #endregion
        
        private void OnDestroy()
        {
            // 取消订阅事件
            if (apiClient != null)
            {
                apiClient.OnAuthenticationResult -= OnAuthenticationResult;
                apiClient.OnStudentValidationResult -= OnStudentValidationResult;
                apiClient.OnTestDataUploadResult -= OnTestDataUploadResult;
                apiClient.OnTestStatusResult -= OnTestStatusResult;
                apiClient.OnError -= OnError;
            }
        }
        
        #region 公共方法（供外部调用）
        
        /// <summary>
        /// 快速上传检测数据（无需UI）
        /// </summary>
        /// <param name="studentId">学号</param>
        /// <param name="studentName">学生姓名</param>
        /// <param name="className">班级</param>
        /// <param name="gender">性别</param>
        /// <param name="age">年龄</param>
        /// <param name="anxietyScore">焦虑得分</param>
        /// <param name="depressionScore">抑郁得分</param>
        /// <param name="stressScore">压力得分</param>
        /// <param name="heartRate">心率</param>
        /// <param name="eegAlpha">脑电alpha</param>
        /// <param name="aiSummary">AI总结</param>
        /// <param name="pdfData">PDF文件数据</param>
        public void QuickUploadTestData(string studentId, string studentName, string className, 
            string gender, int age, int anxietyScore, int depressionScore, int stressScore,
            float heartRate, float eegAlpha, string aiSummary, byte[] pdfData)
        {
            ClientTestData testData = new ClientTestData();
            testData.student_id = studentId;
            testData.name = studentName;
            testData.gender = gender;
            testData.age = age;
            testData.class_name = className;
            testData.SetTestTime(DateTime.Now);
            testData.SetQuestionnaireScores(anxietyScore, depressionScore, stressScore);
            testData.SetPhysiologicalData(heartRate, eegAlpha);
            testData.ai_summary = aiSummary;
            testData.report_file_path = $"reports/{studentName}_{studentId}_{DateTime.Now:yyyyMMdd_HHmmss}.pdf";
            
            apiClient?.UploadTestData(testData, pdfData);
        }
        
        /// <summary>
        /// 快速验证学号（无需UI）
        /// </summary>
        /// <param name="studentId">学号</param>
        public void QuickValidateStudent(string studentId)
        {
            apiClient?.ValidateStudent(studentId);
        }
        
        /// <summary>
        /// 快速查询检测状态（无需UI）
        /// </summary>
        /// <param name="studentId">学号</param>
        public void QuickGetTestStatus(string studentId)
        {
            apiClient?.GetStudentTestStatus(studentId);
        }
        
        #endregion
    }
}



