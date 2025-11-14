# Unity与心理检测管理系统集成指南

## 概述

本指南将帮助你在Unity项目中集成心理检测管理系统，实现从Unity客户端向心理检测系统发送数据的功能。

## 系统要求

- Unity 2020.3 LTS 或更高版本
- .NET Standard 2.1 或更高版本
- 心理检测管理系统API服务运行在 `http://localhost:8002`

## 文件结构

```
UnityIntegration/
├── PsychTestAPIClient.cs      # 主要API客户端
├── PsychTestDataModels.cs     # 数据模型定义
├── PsychTestExample.cs        # 使用示例
└── README.md                  # 本指南
```

## 快速开始

### 1. 导入脚本

1. 在Unity项目中创建文件夹 `Assets/Scripts/PsychTestSystem/`
2. 将所有 `.cs` 文件复制到该文件夹中
3. Unity会自动编译这些脚本

### 2. 基本设置

#### 方法一：使用示例场景

1. 创建一个新的GameObject，命名为 "PsychTestManager"
2. 添加 `PsychTestAPIClient` 组件
3. 添加 `PsychTestExample` 组件
4. 在Inspector中配置API设置：
   - Base URL: `http://localhost:8002`
   - Admin Username: `admin`
   - Admin Password: `password`

#### 方法二：代码集成

```csharp
using PsychTestSystem;
using UnityEngine;

public class MyPsychTestManager : MonoBehaviour
{
    private PsychTestAPIClient apiClient;

    void Start()
    {
        // 获取或创建API客户端
        apiClient = GetComponent<PsychTestAPIClient>();
        if (apiClient == null)
        {
            apiClient = gameObject.AddComponent<PsychTestAPIClient>();
        }

        // 订阅事件
        apiClient.OnAuthenticationResult += OnAuthResult;
        apiClient.OnTestDataUploadResult += OnUploadResult;
        apiClient.OnError += OnError;

        // 开始身份验证
        apiClient.Authenticate();
    }

    private void OnAuthResult(bool success)
    {
        if (success)
        {
            Debug.Log("身份验证成功！");
            // 现在可以发送数据了
        }
    }

    private void OnUploadResult(TestDataUploadResult result)
    {
        Debug.Log($"数据上传成功，记录ID: {result.id}");
    }

    private void OnError(string error)
    {
        Debug.LogError($"API错误: {error}");
    }
}
```

## API使用说明

### 1. 身份验证

系统使用JWT令牌进行身份验证。客户端会自动处理令牌获取和刷新。

```csharp
// 手动触发身份验证
apiClient.Authenticate();

// 检查认证状态
if (apiClient.IsAuthenticated)
{
    // 可以进行API调用
}
```

### 2. 学生验证

在发送检测数据前，建议先验证学号是否存在：

```csharp
apiClient.ValidateStudent("U001");

// 处理验证结果
private void OnStudentValidationResult(StudentValidationResult result)
{
    if (result.exists)
    {
        Debug.Log($"学生存在: {result.student_info.name}");
        // 继续发送检测数据
    }
    else
    {
        Debug.Log("学号不存在");
    }
}
```

### 3. 上传检测数据

这是核心功能，用于发送心理检测数据：

```csharp
// 创建检测数据
ClientTestData testData = new ClientTestData();
testData.student_id = "U001";
testData.name = "张三";
testData.gender = "男";
testData.age = 20;
testData.class_name = "计算机1班";
testData.SetTestTime(DateTime.Now);
testData.SetQuestionnaireScores(8, 4, 12); // 焦虑、抑郁、压力得分
testData.SetPhysiologicalData(85.0f, 13.2f); // 心率、脑电alpha
testData.ai_summary = "检测出高焦虑风险，建议进一步评估";
testData.report_file_path = "reports/张三_U001_20231201_143000.pdf";

// 准备PDF文件数据
byte[] pdfData = LoadPDFFile("path/to/report.pdf");

// 上传数据
apiClient.UploadTestData(testData, pdfData);
```

### 4. 查询检测状态

查询学生的检测状态和历史记录：

```csharp
apiClient.GetStudentTestStatus("U001");

// 处理状态查询结果
private void OnTestStatusResult(TestStatusResult result)
{
    Debug.Log($"学生 {result.student_id} 状态: {result.status}");
    Debug.Log($"是否异常: {result.is_abnormal}");
    Debug.Log($"检测次数: {result.test_record_count}");
}
```

## 数据模型说明

### ClientTestData（检测数据）

| 字段                       | 类型                | 说明                |
| -------------------------- | ------------------- | ------------------- |
| student_id                 | string              | 学号（必填）        |
| name                       | string              | 学生姓名（必填）    |
| gender                     | string              | 性别（必填）        |
| age                        | int                 | 年龄（必填）        |
| class_name                 | string              | 班级名称（可选）    |
| test_time                  | string              | 检测时间（ISO格式） |
| questionnaire_scores       | QuestionnaireScores | 问卷得分            |
| physiological_data_summary | PhysiologicalData   | 生理数据            |
| ai_summary                 | string              | AI分析总结（必填）  |
| report_file_path           | string              | 报告文件路径        |

### QuestionnaireScores（问卷得分）

| 字段       | 类型 | 说明     |
| ---------- | ---- | -------- |
| anxiety    | int  | 焦虑得分 |
| depression | int  | 抑郁得分 |
| stress     | int  | 压力得分 |

### PhysiologicalData（生理数据）

| 字段       | 类型  | 说明        |
| ---------- | ----- | ----------- |
| heart_rate | float | 心率        |
| eeg_alpha  | float | 脑电alpha值 |

## 错误处理

系统提供完善的错误处理机制：

```csharp
apiClient.OnError += (errorMessage) => {
    Debug.LogError($"API错误: {errorMessage}");
    // 处理错误，如重试、显示错误信息等
};
```

常见错误类型：

- 网络连接错误
- 身份验证失败
- 数据格式错误
- 服务器内部错误

## 最佳实践

### 1. 数据验证

在发送数据前进行验证：

```csharp
private bool ValidateTestData(ClientTestData data)
{
    if (string.IsNullOrEmpty(data.student_id))
    {
        Debug.LogError("学号不能为空");
        return false;
    }

    if (data.age <= 0 || data.age > 100)
    {
        Debug.LogError("年龄必须在1-100之间");
        return false;
    }

    if (data.questionnaire_scores.anxiety < 0 || data.questionnaire_scores.anxiety > 30)
    {
        Debug.LogError("焦虑得分必须在0-30之间");
        return false;
    }

    return true;
}
```

### 2. 异步处理

所有API调用都是异步的，使用事件回调处理结果：

```csharp
private void SendTestData()
{
    if (!apiClient.IsAuthenticated)
    {
        Debug.LogWarning("未认证，先进行身份验证");
        apiClient.Authenticate();
        return;
    }

    // 验证学号
    apiClient.ValidateStudent(studentId);
}

private void OnStudentValidationResult(StudentValidationResult result)
{
    if (result.exists)
    {
        // 学号存在，继续上传数据
        UploadTestData();
    }
    else
    {
        Debug.LogError("学号不存在，请检查");
    }
}
```

### 3. 文件处理

处理PDF文件上传：

```csharp
private byte[] LoadPDFFile(string filePath)
{
    try
    {
        return File.ReadAllBytes(filePath);
    }
    catch (Exception e)
    {
        Debug.LogError($"读取PDF文件失败: {e.Message}");
        return null;
    }
}

private void SavePDFFile(byte[] pdfData, string fileName)
{
    try
    {
        string path = Path.Combine(Application.persistentDataPath, fileName);
        File.WriteAllBytes(path, pdfData);
        Debug.Log($"PDF文件已保存: {path}");
    }
    catch (Exception e)
    {
        Debug.LogError($"保存PDF文件失败: {e.Message}");
    }
}
```

### 4. 网络状态检查

在发送数据前检查网络状态：

```csharp
private bool IsNetworkAvailable()
{
    return Application.internetReachability != NetworkReachability.NotReachable;
}

private void SendDataWithNetworkCheck()
{
    if (!IsNetworkAvailable())
    {
        Debug.LogWarning("网络不可用，请检查网络连接");
        return;
    }

    // 发送数据
    apiClient.UploadTestData(testData, pdfData);
}
```

## 配置选项

### API客户端配置

在Inspector中可以配置以下选项：

- **Base URL**: API服务器地址（默认：http://localhost:8002）
- **Admin Username**: 管理员用户名（默认：admin）
- **Admin Password**: 管理员密码（默认：password）
- **Enable Debug Logs**: 是否启用调试日志

### 环境配置

不同环境的配置：

```csharp
// 开发环境
apiClient.baseURL = "http://localhost:8002";

// 测试环境
apiClient.baseURL = "http://test-server:8002";

// 生产环境
apiClient.baseURL = "http://prod-server:8002";
```

## 故障排除

### 常见问题

1. **身份验证失败**
   - 检查用户名和密码是否正确
   - 确认API服务器是否运行
   - 检查网络连接

2. **数据上传失败**
   - 确认学号是否存在
   - 检查数据格式是否正确
   - 验证PDF文件是否有效

3. **网络超时**
   - 检查网络连接稳定性
   - 增加超时时间设置
   - 检查防火墙设置

### 调试技巧

1. **启用调试日志**

   ```csharp
   apiClient.enableDebugLogs = true;
   ```

2. **检查API响应**

   ```csharp
   private void OnError(string error)
   {
       Debug.LogError($"API错误详情: {error}");
       // 可以添加更详细的错误处理
   }
   ```

3. **网络状态监控**
   ```csharp
   private void Update()
   {
       if (Application.internetReachability == NetworkReachability.NotReachable)
       {
           Debug.LogWarning("网络连接已断开");
       }
   }
   ```

## 扩展功能

### 自定义数据模型

如果需要添加新的数据字段：

```csharp
[Serializable]
public class ExtendedTestData : ClientTestData
{
    public string additional_field;
    public int custom_score;
}
```

### 批量操作

实现批量数据上传：

```csharp
private void UploadBatchData(List<ClientTestData> testDataList)
{
    StartCoroutine(UploadBatchCoroutine(testDataList));
}

private IEnumerator UploadBatchCoroutine(List<ClientTestData> testDataList)
{
    foreach (var testData in testDataList)
    {
        // 上传单个数据
        apiClient.UploadTestData(testData, pdfData);

        // 等待一段时间避免请求过于频繁
        yield return new WaitForSeconds(1.0f);
    }
}
```

## 性能优化

1. **请求缓存**
   - 缓存学生验证结果
   - 避免重复的身份验证

2. **数据压缩**
   - 压缩PDF文件
   - 优化JSON数据大小

3. **并发控制**
   - 限制同时进行的请求数量
   - 使用队列管理请求

## 安全考虑

1. **敏感信息保护**
   - 不要在代码中硬编码密码
   - 使用环境变量或配置文件

2. **数据验证**
   - 客户端验证数据格式
   - 服务器端验证数据有效性

3. **网络安全**
   - 使用HTTPS协议
   - 验证SSL证书

## 更新日志

### v1.0.0

- 初始版本发布
- 支持基本的API交互功能
- 包含完整的示例代码

## 技术支持

如有问题或建议，请联系开发团队或查看项目文档。

---

**注意**: 本集成方案基于心理检测管理系统v1.0.0版本开发，如API有更新，可能需要相应调整代码。
