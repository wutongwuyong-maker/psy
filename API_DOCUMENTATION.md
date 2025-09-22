# 心理检测管理系统 API 文档

## 概述

本文档描述了心理检测管理系统的API接口，包括管理员认证、学生管理、检测记录管理、报告生成以及客户端对接等功能。

## 基础信息

- **基础URL**: `http://localhost:8000`
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

所有API在发生错误时都会返回适当的HTTP状态码和错误信息。本节详细说明了各种可能的错误情况及其响应格式。

### 常见错误码

- `400 Bad Request`: 请求参数错误或格式不正确
- `401 Unauthorized`: 未授权访问（令牌无效或过期）
- `403 Forbidden`: 权限不足（非管理员访问需要管理员权限的接口）
- `404 Not Found`: 请求的资源不存在
- `409 Conflict`: 资源冲突（如学号已存在）
- `422 Unprocessable Entity`: 数据验证失败
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

#### 基本错误响应格式

```json
{
  "detail": "错误信息描述"
}
```

#### 详细错误响应格式（部分接口）

```json
{
  "detail": {
    "error_type": "错误类型",
    "message": "错误信息描述",
    "field_errors": {
      "字段名": ["字段错误信息"]
    }
  }
}
```

### 具体错误情况及响应示例

#### 1. 认证相关错误

##### 401 Unauthorized - 令牌无效或缺失

**错误情况**:
- 未提供JWT令牌
- 提供的JWT令牌无效
- JWT令牌已过期

**响应示例**:
```json
{
  "detail": "Could not validate credentials"
}
```

##### 401 Unauthorized - 用户名或密码错误

**错误情况**:
- 登录时提供的用户名不存在
- 登录时提供的密码不正确

**响应示例**:
```json
{
  "detail": "用户名或密码不正确"
}
```

#### 2. 学生管理相关错误

##### 400 Bad Request - 批量导入Excel格式错误

**错误情况**:
- 上传的文件不是有效的Excel文件
- Excel文件缺少必要的列

**响应示例**:
```json
{
  "detail": "Excel读取失败: 文件格式不正确"
}
```

或

```json
{
  "detail": "缺少必要列: name, student_id"
}
```

##### 404 Not Found - 学生不存在

**错误情况**:
- 查询、更新或删除不存在的学生
- 为不存在的学生生成报告

**响应示例**:
```json
{
  "detail": "学生未找到"
}
```

##### 409 Conflict - 学号已存在

**错误情况**:
- 创建学生时提供的学号已存在
- 批量导入时遇到重复学号

**响应示例**:
```json
{
  "detail": "学号已存在"
}
```

##### 422 Unprocessable Entity - 数据验证失败

**错误情况**:
- 提供的学生数据格式不正确
- 必填字段缺失

**响应示例**:
```json
{
  "detail": {
    "error_type": "validation_error",
    "message": "数据验证失败",
    "field_errors": {
      "student_id": ["学号不能为空"],
      "gender": ["性别必须是'男'或'女'"]
    }
  }
}
```

#### 3. 检测记录相关错误

##### 400 Bad Request - 检测数据格式错误

**错误情况**:
- 上传的检测数据格式不正确
- 缺少必要的检测数据字段

**响应示例**:
```json
{
  "detail": "检测数据格式错误: 缺少必要字段"
}
```

##### 404 Not Found - 检测记录不存在

**错误情况**:
- 查询、更新或删除不存在的检测记录

**响应示例**:
```json
{
  "detail": "记录不存在"
}
```

##### 422 Unprocessable Entity - 状态值无效

**错误情况**:
- 更新检测记录状态时提供了无效的状态值

**响应示例**:
```json
{
  "detail": "无效的状态值，必须是: pending, processing, completed, failed"
}
```

#### 4. 报告生成相关错误

##### 404 Not Found - 无法生成报告

**错误情况**:
- 为不存在的学生生成报告
- 学生没有检测记录

**响应示例**:
```json
{
  "detail": "学生不存在或没有检测记录"
}
```

##### 500 Internal Server Error - 报告生成失败

**错误情况**:
- PDF生成过程中出现错误
- 文件系统权限问题

**响应示例**:
```json
{
  "detail": "报告生成失败: 内部服务器错误"
}
```

#### 5. 客户端对接相关错误

##### 400 Bad Request - 文件上传错误

**错误情况**:
- 上传的PDF文件格式不正确
- 文件大小超过限制

**响应示例**:
```json
{
  "detail": "文件上传失败: 文件格式不支持或大小超过限制"
}
```

##### 404 Not Found - 学生不存在（客户端验证）

**错误情况**:
- 客户端验证不存在的学号

**响应示例**:
```json
{
  "exists": false,
  "student_info": null
}
```

#### 6. 通用服务器错误

##### 500 Internal Server Error - 数据库错误

**错误情况**:
- 数据库连接失败
- 数据库查询错误

**响应示例**:
```json
{
  "detail": "数据库操作失败: 内部服务器错误"
}
```

##### 500 Internal Server Error - 服务器内部错误

**错误情况**:
- 未捕获的异常
- 系统资源不足

**响应示例**:
```json
{
  "detail": "服务器内部错误，请稍后重试"
}
```

### 错误处理建议

1. **客户端错误处理**:
   - 检查HTTP状态码，根据不同状态码采取不同处理方式
   - 对于400/422错误，检查请求参数和数据格式
   - 对于401错误，重新获取JWT令牌
   - 对于404错误，提示用户资源不存在
   - 对于5xx错误，提示用户稍后重试

2. **重试机制**:
   - 对于5xx错误，可以实现指数退避重试机制
   - 对于网络超时，可以适当重试

3. **错误日志**:
   - 记录API调用错误，便于问题排查
   - 对于重要操作，记录完整的请求和响应信息

4. **用户提示**:
   - 将技术性错误信息转换为用户友好的提示
   - 对于可恢复的错误，提供明确的解决建议

## 请求限制

为了保护API服务的稳定性和安全性，系统实现了以下请求限制机制：

### 速率限制

- **默认限制**: 每个IP地址每分钟最多可发起60次请求
- **认证用户限制**: 已认证用户每分钟最多可发起120次请求
- **特殊端点限制**:
  - 文件上传端点: 每分钟最多10次请求
  - 报告生成端点: 每分钟最多5次请求
  - 批量导入端点: 每分钟最多3次请求

### 限制响应格式

当超过请求限制时，API将返回以下响应：

```json
{
  "detail": "请求频率超过限制，请稍后重试",
  "retry_after": 60  // 建议等待的秒数
}
```

### 限制策略

1. **滑动窗口算法**: 使用滑动窗口算法计算请求频率
2. **令牌桶算法**: 对特殊端点使用令牌桶算法进行更精细的控制
3. **IP级别限制**: 对未认证用户基于IP地址进行限制
4. **用户级别限制**: 对已认证用户基于用户ID进行限制

### 最佳实践

1. **批量操作**: 尽可能使用批量操作接口减少请求次数
2. **缓存策略**: 对不常变化的数据实现客户端缓存
3. **错误处理**: 正确处理429状态码，实现适当的退避重试机制
4. **请求优化**: 避免不必要的请求，合并相关操作

## 认证示例

### 使用JWT令牌进行认证的完整请求示例

#### 1. 获取JWT令牌

**请求示例**:

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

**响应示例**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY4OTA0MjQwMn0.OXJdKqWd7V3X9L7xK5n8W3J2fG6hY1i0ZpL4mN7oQ9E",
  "token_type": "bearer"
}
```

#### 2. 使用JWT令牌访问受保护的API

**请求示例**:

```bash
curl -X GET "http://localhost:8000/api/students" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY4OTA0MjQwMn0.OXJdKqWd7V3X9L7xK5n8W3J2fG6hY1i0ZpL4mN7oQ9E"
```

#### 3. 使用JWT令牌上传文件

**请求示例**:

```bash
curl -X POST "http://localhost:8000/api/students/batch-import" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTY4OTA0MjQwMn0.OXJdKqWd7V3X9L7xK5n8W3J2fG6hY1i0ZpL4mN7oQ9E" \
  -F "file=@students.xlsx"
```

#### 4. 处理令牌过期

当令牌过期时，API将返回401状态码：

```json
{
  "detail": "Could not validate credentials"
}
```

**解决方案**: 重新获取JWT令牌并重试请求

#### 5. Python完整认证示例

```python
import requests
from requests.auth import HTTPBasicAuth
import time

class APIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None
    
    def authenticate(self):
        """获取JWT令牌"""
        response = requests.post(
            f"{self.base_url}/token",
            data={"username": self.username, "password": self.password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            # 假设令牌有效期为1小时
            self.token_expiry = time.time() + 3600
            return True
        return False
    
    def get_headers(self):
        """获取包含认证信息的请求头"""
        if not self.token or (self.token_expiry and time.time() > self.token_expiry):
            self.authenticate()
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def get_students(self, params=None):
        """获取学生列表"""
        response = requests.get(
            f"{self.base_url}/api/students",
            headers=self.get_headers(),
            params=params
        )
        
        if response.status_code == 401:
            # 令牌可能过期，重试一次
            self.authenticate()
            response = requests.get(
                f"{self.base_url}/api/students",
                headers=self.get_headers(),
                params=params
            )
        
        return response.json()

# 使用示例
client = APIClient("http://localhost:8000", "admin", "password")
students = client.get_students({"limit": 10})
print(students)
```

#### 6. JavaScript完整认证示例

```javascript
class APIClient {
  constructor(baseUrl, username, password) {
    this.baseUrl = baseUrl;
    this.username = username;
    this.password = password;
    this.token = null;
    this.tokenExpiry = null;
  }

  async authenticate() {
    const response = await fetch(`${this.baseUrl}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: this.username,
        password: this.password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      this.token = data.access_token;
      // 假设令牌有效期为1小时
      this.tokenExpiry = Date.now() + 3600 * 1000;
      return true;
    }
    return false;
  }

  async getHeaders() {
    if (!this.token || (this.tokenExpiry && Date.now() > this.tokenExpiry)) {
      await this.authenticate();
    }

    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json',
    };
  }

  async getStudents(params = {}) {
    const url = new URL(`${this.baseUrl}/api/students`);
    Object.keys(params).forEach(key => {
      if (params[key] !== undefined) {
        url.searchParams.append(key, params[key]);
      }
    });

    let response = await fetch(url, {
      headers: await this.getHeaders(),
    });

    if (response.status === 401) {
      // 令牌可能过期，重试一次
      await this.authenticate();
      response = await fetch(url, {
        headers: await this.getHeaders(),
      });
    }

    return response.json();
  }
}

// 使用示例
const client = new APIClient('http://localhost:8000', 'admin', 'password');
client.getStudents({ limit: 10 })
  .then(students => console.log(students))
  .catch(error => console.error('Error:', error));
```

## 数据验证

### 输入数据验证规则

API对所有输入数据进行严格验证，确保数据完整性和安全性。以下是各主要数据模型的验证规则：

#### 1. 学生数据验证

##### 必填字段
- `student_id`: 学号，字符串类型，长度1-20字符，只能包含字母、数字和下划线
- `name`: 姓名，字符串类型，长度1-50字符
- `class_name`: 班级，字符串类型，长度1-50字符
- `gender`: 性别，必须是"男"或"女"

##### 字段格式验证
```json
{
  "student_id": "^[a-zA-Z0-9_]{1,20}$",
  "name": "^.{1,50}$",
  "class_name": "^.{1,50}$",
  "gender": "^(男|女)$"
}
```

##### 验证错误示例
```json
{
  "detail": {
    "error_type": "validation_error",
    "message": "数据验证失败",
    "field_errors": {
      "student_id": ["学号不能为空", "学号格式不正确"],
      "gender": ["性别必须是'男'或'女'"]
    }
  }
}
```

#### 2. 检测记录数据验证

##### 必填字段
- `student_fk_id`: 学生ID，整数类型，必须引用有效学生
- `test_time`: 检测时间，ISO 8601格式日期时间
- `scores`: 检测分数，数组类型，每个元素包含module_name和score字段

##### 字段格式验证
```json
{
  "student_fk_id": "^[0-9]+$",
  "test_time": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?$",
  "scores": "array",
  "scores.*.module_name": "^.{1,50}$",
  "scores.*.score": "^(0|[1-9][0-9]?|100)$"
}
```

##### 分数范围验证
- 每个检测模块的分数必须在0-100之间
- 必须至少包含一个检测模块的分数

##### 验证错误示例
```json
{
  "detail": {
    "error_type": "validation_error",
    "message": "数据验证失败",
    "field_errors": {
      "test_time": ["检测时间格式不正确"],
      "scores": ["必须至少包含一个检测模块的分数"],
      "scores.0.score": ["分数必须在0-100之间"]
    }
  }
}
```

#### 3. 用户认证数据验证

##### 登录数据验证
```json
{
  "username": "^[a-zA-Z0-9_]{3,20}$",
  "password": "^.{6,}$"
}
```

##### 验证规则
- 用户名长度3-20字符，只能包含字母、数字和下划线
- 密码长度至少6字符

##### 验证错误示例
```json
{
  "detail": "用户名或密码不正确"
}
```

#### 4. 文件上传验证

##### 文件类型验证
- 批量导入学生: 仅支持.xlsx和.xls格式的Excel文件
- 客户端上传检测数据: 仅支持.pdf格式的文件

##### 文件大小验证
- 批量导入学生: 最大10MB
- 客户端上传检测数据: 最大10MB

##### Excel文件结构验证
- 必须包含列: name, student_id, class_name, gender
- 数据行数不能超过1000行

##### 验证错误示例
```json
{
  "detail": "文件上传失败: 文件格式不支持或大小超过限制"
}
```

或

```json
{
  "detail": "Excel读取失败: 缺少必要列: name, student_id"
}
```

#### 5. 批量操作验证

##### 批量查询学生验证
- `student_ids`: 数组类型，元素数量不能超过100
- 每个学号必须符合学号格式验证规则

##### 验证错误示例
```json
{
  "detail": {
    "error_type": "validation_error",
    "message": "数据验证失败",
    "field_errors": {
      "student_ids": ["学号数量不能超过100个"],
      "student_ids.0": ["学号格式不正确"]
    }
  }
}
```

### 数据验证最佳实践

1. **客户端验证**: 在发送请求前进行基本的客户端验证，减少无效请求
2. **错误处理**: 正确处理422状态码，向用户显示友好的错误信息
3. **数据清理**: 在发送数据前进行清理，去除不必要的空格和特殊字符
4. **类型转换**: 确保数据类型正确，如日期时间使用ISO 8601格式
5. **边界测试**: 测试边界值，如最大长度、最大数量等

### 自定义验证规则

系统支持以下自定义验证规则：

1. **学号唯一性验证**: 创建或更新学生时验证学号唯一性
2. **学生存在性验证**: 创建检测记录时验证学生存在
3. **状态值验证**: 更新状态时验证状态值是否在允许范围内
4. **文件格式验证**: 上传文件时验证文件格式和内容

### 验证错误代码

| 错误代码 | 描述 |
|---------|------|
| `validation.required` | 必填字段缺失 |
| `validation.format` | 字段格式不正确 |
| `validation.min_length` | 字段长度小于最小值 |
| `validation.max_length` | 字段长度大于最大值 |
| `validation.min_value` | 数值小于最小值 |
| `validation.max_value` | 数值大于最大值 |
| `validation.unique` | 值必须唯一 |
| `validation.exists` | 引用的记录不存在 |
| `validation.enum` | 值不在允许的枚举范围内 |

## 示例代码

### Python 示例

```python
import requests
import json

# 1. 获取JWT令牌
token_response = requests.post(
    "http://localhost:8000/token",
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
    "http://localhost:8000/api/students",
    headers=headers
)
print(students_response.json())

# 4. 客户端学号验证
validation_response = requests.post(
    "http://localhost:8000/api/client/validate-student",
    json={"student_id": "U001"}
)
print(validation_response.json())
```

### JavaScript 示例

```javascript
// 1. 获取JWT令牌
async function login() {
  const response = await fetch("http://localhost:8000/token", {
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
  const response = await fetch("http://localhost:8000/api/students", {
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
    "http://localhost:8000/api/client/upload-test-data",
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
