# 心理检测管理系统 API 文档

## 概述

本文档描述了心理检测管理系统的API接口，包括管理员认证、学生管理、检测记录管理、报告生成以及客户端对接等功能。

## 基础信息

- **基础URL**: `http://localhost:8002`
- **API版本**: v1.0.0
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证

### 获取JWT令牌

**端点**: `POST /token`

**描述**: 获取管理员访问令牌

**请求参数**:

```json
{
  "username": "admin",
  "password": "password"
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**使用方式**: 在后续请求的Header中添加 `Authorization: Bearer <access_token>`

## 学生管理

### 获取学生列表

**端点**: `GET /api/students`

**描述**: 获取学生列表，支持筛选、排序和分页

**请求参数**:

- `skip`: 跳过记录数 (默认: 0)
- `limit`: 限制记录数 (默认: 100)
- `class_name`: 班级筛选 (可选)
- `gender`: 性别筛选 (可选)
- `sort_by`: 排序字段 (默认: "name")
- `sort_order`: 排序方向 (默认: "asc")

**响应**:

```json
[
  {
    "id": 1,
    "student_id": "U001",
    "name": "张三",
    "class_name": "计算机1班",
    "gender": "男",
    "created_at": "2023-07-10T10:00:00"
  }
]
```

### 获取单个学生

**端点**: `GET /api/students/{student_id}`

**描述**: 根据学号获取单个学生信息

**响应**:

```json
{
  "id": 1,
  "student_id": "U001",
  "name": "张三",
  "class_name": "计算机1班",
  "gender": "男",
  "created_at": "2023-07-10T10:00:00"
}
```

### 创建学生

**端点**: `POST /api/students`

**描述**: 创建新的学生记录

**请求体**:

```json
{
  "student_id": "U002",
  "name": "李四",
  "class_name": "计算机2班",
  "gender": "女"
}
```

### 更新学生

**端点**: `PUT /api/students/{student_id}`

**描述**: 更新学生信息

**请求体**:

```json
{
  "name": "李四更新",
  "class_name": "计算机2班更新"
}
```

### 删除学生

**端点**: `DELETE /api/students/{student_id}`

**描述**: 删除学生记录

### 批量导入学生

**端点**: `POST /api/students/batch-import`

**描述**: 通过Excel文件批量导入学生

**请求参数**:

- `file`: Excel文件 (必须包含列: name, student_id, class_name, gender)

### 学号验证

**端点**: `POST /api/students/validate`

**描述**: 验证学号是否存在

**请求体**:

```json
{
  "student_id": "U001"
}
```

## 检测记录管理

### 获取检测记录列表

**端点**: `GET /test-data/records/`

**描述**: 获取检测记录列表，支持筛选和分页

**请求参数**:

- `user_id`: 学号筛选 (可选)
- `start_time`: 开始时间 (可选)
- `end_time`: 结束时间 (可选)
- `is_abnormal`: 是否异常 (可选)
- `status`: 状态筛选 (可选)
- `skip`: 跳过记录数 (默认: 0)
- `limit`: 限制记录数 (默认: 100)

**响应**:

```json
[
  {
    "id": 1,
    "student_fk_id": 1,
    "test_time": "2023-07-10T10:00:00",
    "ai_summary": "检测出高焦虑风险，建议进一步评估",
    "report_file_path": "pdfs/U001_0710.pdf",
    "is_abnormal": true,
    "status": "pending",
    "student": {
      "id": 1,
      "student_id": "U001",
      "name": "张三",
      "class_name": "计算机1班",
      "gender": "男",
      "created_at": "2023-07-10T10:00:00"
    },
    "scores": [
      {
        "id": 1,
        "module_name": "焦虑",
        "score": 18
      }
    ],
    "physiological_data": [
      {
        "id": 1,
        "data_key": "心率",
        "data_value": 85.0
      }
    ]
  }
]
```

### 获取检测记录详情

**端点**: `GET /test-data/records/{record_id}`

**描述**: 获取单个检测记录详情

### 上传检测数据

**端点**: `POST /test-data/upload`

**描述**: 上传心理检测数据

**请求体**:

```json
{
  "user_id": "U001",
  "name": "张三",
  "gender": "男",
  "age": 20,
  "test_time": "2023-07-10T10:00:00",
  "questionnaire_scores": {
    "焦虑": 8,
    "抑郁": 4,
    "压力": 12
  },
  "physiological_data_summary": {
    "心率": 85,
    "脑电alpha": 13.2
  },
  "ai_summary": "检测出高焦虑风险，建议进一步评估",
  "report_file_path": "pdfs/U001_0710.pdf"
}
```

### 删除检测记录

**端点**: `DELETE /test-data/records/{record_id}`

**描述**: 删除检测记录

### 更新检测记录状态

**端点**: `PUT /api/test-records/{record_id}/status`

**描述**: 更新检测记录状态

**请求体**:

```json
{
  "status": "completed",
  "ai_summary": "处理完成，建议关注焦虑水平"
}
```

### 批量获取检测记录状态

**端点**: `GET /api/test-records/batch-status`

**描述**: 批量获取检测记录状态

**请求参数**:

- `student_ids`: 学号列表 (可选，数组格式)

**响应**:

```json
{
  "records": [
    {
      "id": 1,
      "test_time": "2023-07-10T10:00:00",
      "is_abnormal": true,
      "status": "completed",
      "ai_summary": "检测出高焦虑风险"
    }
  ],
  "total_count": 1,
  "abnormal_count": 1,
  "pending_count": 0,
  "processing_count": 0,
  "completed_count": 1,
  "failed_count": 0
}
```

## 报告管理

### 生成报告内容

**端点**: `GET /api/reports/{student_id}`

**描述**: 生成学生报告内容

**响应**:

```json
{
  "content": "学生张三的心理检测报告内容..."
}
```

### 下载报告

**端点**: `GET /api/reports/{student_id}/download`

**描述**: 下载学生报告文件

**请求参数**:

- `format`: 文件格式 (pdf 或 excel，默认: pdf)

### 批量生成报告

**端点**: `POST /api/test-records/batch-generate-reports`

**描述**: 批量生成检测记录报告

**请求体**:

```json
{
  "record_ids": [1, 2, 3],
  "format": "pdf"
}
```

**响应**:

```json
{
  "message": "成功生成 3 份报告",
  "report_files": [
    {
      "record_id": 1,
      "student_id": "U001",
      "file_path": "reports/U001_20230710.pdf",
      "file_name": "U001_20230710.pdf"
    }
  ],
  "failed_count": 0
}
```

## 仪表板统计

### 获取统计数据

**端点**: `GET /api/dashboard/stats`

**描述**: 获取仪表板统计数据

**响应**:

```json
{
  "total_students": 100,
  "total_records": 250,
  "abnormal_count": 45,
  "today_records": 12
}
```

### 获取趋势数据

**端点**: `GET /api/dashboard/trend`

**描述**: 获取检测趋势数据

**请求参数**:

- `days`: 统计天数 (默认: 7)

**响应**:

```json
{
  "dates": ["2023-07-04", "2023-07-05", "2023-07-06"],
  "values": [10, 15, 12]
}
```

### 获取得分统计

**端点**: `GET /api/dashboard/score-stats`

**描述**: 获取问卷得分统计数据

**请求参数**:

- `limit`: 限制记录数 (默认: 100)

**响应**:

```json
{
  "焦虑": {
    "0-10": 20,
    "11-15": 30,
    "16-20": 25,
    "21-25": 15,
    "26-30": 10
  },
  "抑郁": {
    "0-10": 25,
    "11-15": 35,
    "16-20": 20,
    "21-25": 15,
    "26-30": 5
  },
  "压力": {
    "0-10": 30,
    "11-15": 25,
    "16-20": 20,
    "21-25": 15,
    "26-30": 10
  }
}
```

### 获取班级分布

**端点**: `GET /api/dashboard/class-distribution`

**描述**: 获取班级学生分布数据

**响应**:

```json
{
  "计算机1班": 30,
  "计算机2班": 25,
  "计算机3班": 28,
  "计算机4班": 17
}
```

## 客户端对接接口

### 学号验证

**端点**: `POST /api/client/validate-student`

**描述**: 客户端学号验证

**请求体**:

```json
{
  "student_id": "U001"
}
```

**响应**:

```json
{
  "exists": true,
  "student_info": {
    "student_id": "U001",
    "name": "张三",
    "class_name": "计算机1班",
    "gender": "男"
  }
}
```

### 上传检测数据

**端点**: `POST /api/client/upload-test-data`

**描述**: 客户端上传检测数据和PDF文件

**请求格式**: `multipart/form-data`

**请求参数**:

- `pdf_file`: PDF文件
- `test_data`: JSON字符串，格式如下：

```json
{
  "user_id": "U001",
  "name": "张三",
  "gender": "男",
  "age": 20,
  "test_time": "2023-07-10T10:00:00",
  "questionnaire_scores": {
    "焦虑": 8,
    "抑郁": 4,
    "压力": 12
  },
  "physiological_data_summary": {
    "心率": 85,
    "脑电alpha": 13.2
  },
  "ai_summary": "检测出高焦虑风险，建议进一步评估",
  "report_file_path": "pdfs/U001_0710.pdf"
}
```

**响应**:

```json
{
  "id": 1,
  "student_fk_id": 1,
  "test_time": "2023-07-10T10:00:00",
  "ai_summary": "检测出高焦虑风险，建议进一步评估",
  "report_file_path": "client_pdfs/张三_U001_20230710_100000.pdf",
  "is_abnormal": true,
  "status": "completed",
  "student": {
    "id": 1,
    "student_id": "U001",
    "name": "张三",
    "class_name": "计算机1班",
    "gender": "男",
    "created_at": "2023-07-10T10:00:00"
  },
  "scores": [
    {
      "id": 1,
      "module_name": "焦虑",
      "score": 8
    },
    {
      "id": 2,
      "module_name": "抑郁",
      "score": 4
    },
    {
      "id": 3,
      "module_name": "压力",
      "score": 12
    }
  ],
  "physiological_data": [
    {
      "id": 1,
      "data_key": "心率",
      "data_value": 85.0
    },
    {
      "id": 2,
      "data_key": "脑电alpha",
      "data_value": 13.2
    }
  ]
}
```

### 查询学生检测状态

**端点**: `GET /api/client/test-status/{student_id}`

**描述**: 查询学生检测状态

**响应**:

```json
{
  "student_id": "U001",
  "status": "completed",
  "is_abnormal": true,
  "latest_test_time": "2023-07-10T10:00:00",
  "test_record_count": 1
}
```

**状态说明**:

- `not_started`: 未开始检测
- `in_progress`: 检测进行中
- `completed`: 检测已完成

## 数据模型

### Student (学生模型)

```json
{
  "id": 1,
  "student_id": "U001",
  "name": "张三",
  "class_name": "计算机1班",
  "gender": "男",
  "created_at": "2023-07-10T10:00:00"
}
```

### Test (检测记录模型)

```json
{
  "id": 1,
  "student_fk_id": 1,
  "test_time": "2023-07-10T10:00:00",
  "ai_summary": "检测出高焦虑风险，建议进一步评估",
  "report_file_path": "pdfs/U001_0710.pdf",
  "is_abnormal": true,
  "status": "pending"
}
```

### Score (问卷得分模型)

```json
{
  "id": 1,
  "test_fk_id": 1,
  "module_name": "焦虑",
  "score": 18
}
```

### PhysiologicalData (生理数据模型)

```json
{
  "id": 1,
  "test_fk_id": 1,
  "data_key": "心率",
  "data_value": 85.0
}
```

## 错误处理

所有API在发生错误时都会返回适当的HTTP状态码和错误信息：

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未授权访问
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `409 Conflict`: 资源冲突（如学号已存在）
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误信息描述"
}
```

## 示例代码

### Python 示例

```python
import requests
import json

# 1. 获取JWT令牌
token_response = requests.post(
    "http://localhost:8002/token",
    data={"username": "admin", "password": "password"}
)
access_token = token_response.json()["access_token"]

# 2. 设置请求头
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# 3. 获取学生列表
students_response = requests.get(
    "http://localhost:8002/api/students",
    headers=headers
)
print(students_response.json())

# 4. 客户端学号验证
validation_response = requests.post(
    "http://localhost:8002/api/client/validate-student",
    json={"student_id": "U001"}
)
print(validation_response.json())
```

### JavaScript 示例

```javascript
// 1. 获取JWT令牌
async function login() {
  const response = await fetch("http://localhost:8002/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: "admin",
      password: "password",
    }),
  });

  const data = await response.json();
  return data.access_token;
}

// 2. 使用令牌访问API
async function getStudents(token) {
  const response = await fetch("http://localhost:8002/api/students", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return await response.json();
}

// 3. 客户端上传检测数据
async function uploadTestData(token, testData, pdfFile) {
  const formData = new FormData();
  formData.append("pdf_file", pdfFile);
  formData.append("test_data", JSON.stringify(testData));

  const response = await fetch(
    "http://localhost:8002/api/client/upload-test-data",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    },
  );

  return await response.json();
}
```

## 更新日志

### v1.0.0 (2023-07-10)

- 统一使用Student模型作为学生基础信息
- 修复了数据模型不一致问题
- 完善了客户端对接接口
- 优化了状态管理逻辑
- 更新了API文档

## 注意事项

1. **认证**: 大部分API需要JWT认证，请在请求头中包含有效的访问令牌
2. **数据格式**: 所有日期时间格式使用ISO 8601标准
3. **文件上传**: 客户端上传接口支持PDF文件，文件大小限制为10MB
4. **状态管理**: 客户端和服务端状态有映射关系，请参考状态说明
5. **错误处理**: 请正确处理各种HTTP状态码和错误信息

## 联系方式

如有问题或建议，请联系开发团队。
