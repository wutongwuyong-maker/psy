<template>
  <div class="report-view">
    <h2 class="page-title">检测报告预览</h2>
    <el-card class="report-card">
      <div class="loading" v-if="loading">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
      <div class="error" v-else-if="errorMsg">{{ errorMsg }}</div>
      <pre class="report-content" v-else>{{ reportContent }}</pre>
    </el-card>
    <div class="operation-bar">
      <el-select v-model="selectedFormat" placeholder="选择下载格式">
        <el-option label="PDF" value="pdf"></el-option>
        <el-option label="Excel" value="excel"></el-option>
      </el-select>
      <el-button type="primary" @click="downloadReport">下载报告</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import service from "@/http";

const route = useRoute();
const studentId = route.params.student_id || route.params.id || "";

const reportContent = ref("");
const loading = ref(true);
const errorMsg = ref("");
const selectedFormat = ref("pdf");

const fetchReport = async () => {
  if (!studentId) {
    errorMsg.value = "学号参数缺失";
    loading.value = false;
    return;
  }

  try {
    const res = await service.get(`/api/reports/${studentId}`);
    // 确保 content 始终是字符串
    let content = res.data?.content;

    // 如果 content 是数组或对象，转换为字符串
    if (Array.isArray(content)) {
      content = content.join("\n");
    } else if (typeof content === "object" && content !== null) {
      content = JSON.stringify(content, null, 2);
    } else if (typeof content !== "string") {
      content = String(content || "报告内容为空");
    }

    reportContent.value = content || "报告内容为空";
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || "获取报告失败";
    reportContent.value = ""; // 清空内容，避免显示错误数据
  } finally {
    loading.value = false;
  }
};

const downloadReport = () => {
  window.open(
    `/api/reports/${studentId}/download?format=${selectedFormat.value}`,
    "_blank"
  );
};

onMounted(() => {
  fetchReport();
});
</script>

<style scoped>
.report-view {
  padding: 32px;
  max-width: 1200px;
  margin: auto;
}

.page-title {
  text-align: center;
  margin-bottom: 32px;
  font-weight: 500;
}

.report-card {
  margin-bottom: 24px;
}

.loading {
  text-align: center;
  padding: 40px 0;
}

.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin: 0 4px;
  background: var(--accent);
  border-radius: 50%;
  animation: dot-pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}
.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dot-pulse {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.error {
  text-align: center;
  color: var(--error-color);
  padding: 40px 0;
}

.report-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
  border: 1px solid #eaeaea;
  border-radius: var(--radius);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.operation-bar {
  display: flex;
  gap: 12px;
  justify-content: center;
  align-items: center;
}
</style>
