using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace PsychTestSystem
{
    /// <summary>
    /// 心理检测系统API客户端
    /// 用于Unity与心理检测管理系统进行数据交互
    /// </summary>
    public class PsychTestAPIClient : MonoBehaviour
    {
        [Header("API配置")]
        [SerializeField] private string baseURL = "http://localhost:8002";
        [SerializeField] private string adminUsername = "admin";
        [SerializeField] private string adminPassword = "password";
        
        [Header("调试选项")]
        [SerializeField] private bool enableDebugLogs = true;
        
        private string accessToken;
        private bool isAuthenticated = false;
        
        // 事件回调
        public System.Action<bool> OnAuthenticationResult;
        public System.Action<StudentValidationResult> OnStudentValidationResult;
        public System.Action<TestDataUploadResult> OnTestDataUploadResult;
        public System.Action<TestStatusResult> OnTestStatusResult;
        public System.Action<string> OnError;
        
        private void Start()
        {
            // 自动进行身份验证
            Authenticate();
        }
        
        /// <summary>
        /// 进行身份验证获取JWT令牌
        /// </summary>
        public void Authenticate()
        {
            StartCoroutine(AuthenticateCoroutine());
        }
        
        private IEnumerator AuthenticateCoroutine()
        {
            string url = $"{baseURL}/token";
            
            // 准备表单数据
            WWWForm form = new WWWForm();
            form.AddField("username", adminUsername);
            form.AddField("password", adminPassword);
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, form))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        TokenResponse tokenResponse = JsonUtility.FromJson<TokenResponse>(request.downloadHandler.text);
                        accessToken = tokenResponse.access_token;
                        isAuthenticated = true;
                        
                        LogDebug($"身份验证成功，获得访问令牌");
                        OnAuthenticationResult?.Invoke(true);
                    }
                    catch (Exception e)
                    {
                        LogError($"解析令牌响应失败: {e.Message}");
                        OnError?.Invoke($"解析令牌响应失败: {e.Message}");
                        OnAuthenticationResult?.Invoke(false);
                    }
                }
                else
                {
                    LogError($"身份验证失败: {request.error}");
                    OnError?.Invoke($"身份验证失败: {request.error}");
                    OnAuthenticationResult?.Invoke(false);
                }
            }
        }
        
        /// <summary>
        /// 验证学生学号是否存在
        /// </summary>
        /// <param name="studentId">学号</param>
        public void ValidateStudent(string studentId)
        {
            if (!isAuthenticated)
            {
                LogError("未进行身份验证，请先调用Authenticate()");
                OnError?.Invoke("未进行身份验证");
                return;
            }
            
            StartCoroutine(ValidateStudentCoroutine(studentId));
        }
        
        private IEnumerator ValidateStudentCoroutine(string studentId)
        {
            string url = $"{baseURL}/api/client/validate-student";
            
            StudentValidationRequest requestData = new StudentValidationRequest
            {
                student_id = studentId
            };
            
            string jsonData = JsonUtility.ToJson(requestData);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
            {
                request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(jsonData));
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        StudentValidationResult result = JsonUtility.FromJson<StudentValidationResult>(request.downloadHandler.text);
                        LogDebug($"学生验证结果: 学号{studentId} {(result.exists ? "存在" : "不存在")}");
                        OnStudentValidationResult?.Invoke(result);
                    }
                    catch (Exception e)
                    {
                        LogError($"解析学生验证响应失败: {e.Message}");
                        OnError?.Invoke($"解析学生验证响应失败: {e.Message}");
                    }
                }
                else
                {
                    LogError($"学生验证失败: {request.error}");
                    OnError?.Invoke($"学生验证失败: {request.error}");
                }
            }
        }
        
        /// <summary>
        /// 上传检测数据
        /// </summary>
        /// <param name="testData">检测数据</param>
        /// <param name="pdfBytes">PDF文件字节数组</param>
        public void UploadTestData(ClientTestData testData, byte[] pdfBytes)
        {
            if (!isAuthenticated)
            {
                LogError("未进行身份验证，请先调用Authenticate()");
                OnError?.Invoke("未进行身份验证");
                return;
            }
            
            StartCoroutine(UploadTestDataCoroutine(testData, pdfBytes));
        }
        
        private IEnumerator UploadTestDataCoroutine(ClientTestData testData, byte[] pdfBytes)
        {
            string url = $"{baseURL}/api/client/upload-test-data";
            
            // 创建multipart/form-data请求
            List<IMultipartFormSection> formData = new List<IMultipartFormSection>();
            
            // 添加PDF文件
            formData.Add(new MultipartFormFileSection("pdf_file", pdfBytes, "test_report.pdf", "application/pdf"));
            
            // 添加JSON数据
            string jsonData = JsonUtility.ToJson(testData);
            formData.Add(new MultipartFormDataSection("test_data", jsonData));
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, formData))
            {
                request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        TestDataUploadResult result = JsonUtility.FromJson<TestDataUploadResult>(request.downloadHandler.text);
                        LogDebug($"检测数据上传成功，记录ID: {result.id}");
                        OnTestDataUploadResult?.Invoke(result);
                    }
                    catch (Exception e)
                    {
                        LogError($"解析上传响应失败: {e.Message}");
                        OnError?.Invoke($"解析上传响应失败: {e.Message}");
                    }
                }
                else
                {
                    LogError($"检测数据上传失败: {request.error}");
                    OnError?.Invoke($"检测数据上传失败: {request.error}");
                }
            }
        }
        
        /// <summary>
        /// 查询学生检测状态
        /// </summary>
        /// <param name="studentId">学号</param>
        public void GetStudentTestStatus(string studentId)
        {
            if (!isAuthenticated)
            {
                LogError("未进行身份验证，请先调用Authenticate()");
                OnError?.Invoke("未进行身份验证");
                return;
            }
            
            StartCoroutine(GetStudentTestStatusCoroutine(studentId));
        }
        
        private IEnumerator GetStudentTestStatusCoroutine(string studentId)
        {
            string url = $"{baseURL}/api/client/test-status/{studentId}";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        TestStatusResult result = JsonUtility.FromJson<TestStatusResult>(request.downloadHandler.text);
                        LogDebug($"学生{studentId}检测状态: {result.status}");
                        OnTestStatusResult?.Invoke(result);
                    }
                    catch (Exception e)
                    {
                        LogError($"解析状态查询响应失败: {e.Message}");
                        OnError?.Invoke($"解析状态查询响应失败: {e.Message}");
                    }
                }
                else
                {
                    LogError($"查询检测状态失败: {request.error}");
                    OnError?.Invoke($"查询检测状态失败: {request.error}");
                }
            }
        }
        
        /// <summary>
        /// 获取学生列表
        /// </summary>
        /// <param name="skip">跳过记录数</param>
        /// <param name="limit">限制记录数</param>
        public void GetStudents(int skip = 0, int limit = 100)
        {
            if (!isAuthenticated)
            {
                LogError("未进行身份验证，请先调用Authenticate()");
                OnError?.Invoke("未进行身份验证");
                return;
            }
            
            StartCoroutine(GetStudentsCoroutine(skip, limit));
        }
        
        private IEnumerator GetStudentsCoroutine(int skip, int limit)
        {
            string url = $"{baseURL}/api/students?skip={skip}&limit={limit}";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.SetRequestHeader("Authorization", $"Bearer {accessToken}");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        // 解析学生列表
                        string jsonResponse = request.downloadHandler.text;
                        LogDebug($"获取学生列表成功，数据长度: {jsonResponse.Length}");
                        // 这里可以根据需要进一步处理学生列表数据
                    }
                    catch (Exception e)
                    {
                        LogError($"解析学生列表响应失败: {e.Message}");
                        OnError?.Invoke($"解析学生列表响应失败: {e.Message}");
                    }
                }
                else
                {
                    LogError($"获取学生列表失败: {request.error}");
                    OnError?.Invoke($"获取学生列表失败: {request.error}");
                }
            }
        }
        
        private void LogDebug(string message)
        {
            if (enableDebugLogs)
            {
                Debug.Log($"[PsychTestAPIClient] {message}");
            }
        }
        
        private void LogError(string message)
        {
            Debug.LogError($"[PsychTestAPIClient] {message}");
        }
        
        // 公共属性
        public bool IsAuthenticated => isAuthenticated;
        public string BaseURL => baseURL;
    }
}



