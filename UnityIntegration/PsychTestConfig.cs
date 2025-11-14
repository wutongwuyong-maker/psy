using UnityEngine;

namespace PsychTestSystem
{
    /// <summary>
    /// 心理检测系统配置助手
    /// 提供快速配置和设置功能
    /// </summary>
    [CreateAssetMenu(fileName = "PsychTestConfig", menuName = "PsychTestSystem/Configuration")]
    public class PsychTestConfig : ScriptableObject
    {
        [Header("API服务器配置")]
        [SerializeField] private string baseURL = "http://localhost:8002";
        [SerializeField] private string adminUsername = "admin";
        [SerializeField] private string adminPassword = "password";
        
        [Header("超时设置")]
        [SerializeField] private float requestTimeout = 30f;
        [SerializeField] private int maxRetryAttempts = 3;
        
        [Header("调试选项")]
        [SerializeField] private bool enableDebugLogs = true;
        [SerializeField] private bool enableDetailedLogs = false;
        
        [Header("数据验证")]
        [SerializeField] private bool validateDataBeforeUpload = true;
        [SerializeField] private int maxFileSizeMB = 10;
        
        // 公共属性
        public string BaseURL => baseURL;
        public string AdminUsername => adminUsername;
        public string AdminPassword => adminPassword;
        public float RequestTimeout => requestTimeout;
        public int MaxRetryAttempts => maxRetryAttempts;
        public bool EnableDebugLogs => enableDebugLogs;
        public bool EnableDetailedLogs => enableDetailedLogs;
        public bool ValidateDataBeforeUpload => validateDataBeforeUpload;
        public int MaxFileSizeMB => maxFileSizeMB;
        
        /// <summary>
        /// 验证配置是否有效
        /// </summary>
        /// <returns>配置是否有效</returns>
        public bool IsValid()
        {
            if (string.IsNullOrEmpty(baseURL))
            {
                Debug.LogError("Base URL不能为空");
                return false;
            }
            
            if (string.IsNullOrEmpty(adminUsername))
            {
                Debug.LogError("管理员用户名不能为空");
                return false;
            }
            
            if (string.IsNullOrEmpty(adminPassword))
            {
                Debug.LogError("管理员密码不能为空");
                return false;
            }
            
            if (requestTimeout <= 0)
            {
                Debug.LogError("请求超时时间必须大于0");
                return false;
            }
            
            if (maxRetryAttempts < 0)
            {
                Debug.LogError("最大重试次数不能小于0");
                return false;
            }
            
            if (maxFileSizeMB <= 0)
            {
                Debug.LogError("最大文件大小必须大于0");
                return false;
            }
            
            return true;
        }
        
        /// <summary>
        /// 获取完整的API URL
        /// </summary>
        /// <param name="endpoint">API端点</param>
        /// <returns>完整的URL</returns>
        public string GetFullURL(string endpoint)
        {
            if (string.IsNullOrEmpty(endpoint))
                return baseURL;
            
            // 确保endpoint以/开头
            if (!endpoint.StartsWith("/"))
                endpoint = "/" + endpoint;
            
            return baseURL + endpoint;
        }
        
        /// <summary>
        /// 设置开发环境配置
        /// </summary>
        public void SetDevelopmentConfig()
        {
            baseURL = "http://localhost:8002";
            enableDebugLogs = true;
            enableDetailedLogs = true;
            validateDataBeforeUpload = true;
        }
        
        /// <summary>
        /// 设置测试环境配置
        /// </summary>
        public void SetTestingConfig()
        {
            baseURL = "http://test-server:8002";
            enableDebugLogs = true;
            enableDetailedLogs = false;
            validateDataBeforeUpload = true;
        }
        
        /// <summary>
        /// 设置生产环境配置
        /// </summary>
        public void SetProductionConfig()
        {
            baseURL = "http://prod-server:8002";
            enableDebugLogs = false;
            enableDetailedLogs = false;
            validateDataBeforeUpload = true;
        }
        
        /// <summary>
        /// 重置为默认配置
        /// </summary>
        public void ResetToDefault()
        {
            baseURL = "http://localhost:8002";
            adminUsername = "admin";
            adminPassword = "password";
            requestTimeout = 30f;
            maxRetryAttempts = 3;
            enableDebugLogs = true;
            enableDetailedLogs = false;
            validateDataBeforeUpload = true;
            maxFileSizeMB = 10;
        }
        
        private void OnValidate()
        {
            // 确保URL格式正确
            if (!string.IsNullOrEmpty(baseURL))
            {
                if (!baseURL.StartsWith("http://") && !baseURL.StartsWith("https://"))
                {
                    baseURL = "http://" + baseURL;
                }
                
                // 移除末尾的斜杠
                if (baseURL.EndsWith("/"))
                {
                    baseURL = baseURL.Substring(0, baseURL.Length - 1);
                }
            }
        }
    }
}



