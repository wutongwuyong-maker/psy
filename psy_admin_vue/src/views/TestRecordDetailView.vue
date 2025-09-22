<template>
  <div class="record-detail">
    <div class="page-header">
      <h2 class="page-title">检测记录详情</h2>
      <el-button @click="$router.back()" type="primary">返回列表</el-button>
    </div>

    <div v-if="loading" class="loading">
      <span class="dot"></span><span class="dot"></span
      ><span class="dot"></span>
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="detail-container">
      <!-- 基本信息 -->
      <el-card class="info-card">
        <template #header>
          <div class="card-header">
            <span>检测基本信息</span>
            <el-tag :type="record.is_abnormal ? 'danger' : 'success'">
              {{ record.is_abnormal ? "异常" : "正常" }}
            </el-tag>
          </div>
        </template>
        <div class="info-grid">
          <div class="info-item">
            <label>检测时间：</label>
            <span>{{ formatDate(record.test_time) }}</span>
          </div>
          <div class="info-item">
            <label>用户姓名：</label>
            <span>{{ record.student?.name }}</span>
          </div>
          <div class="info-item">
            <label>用户ID：</label>
            <span>{{ record.student?.student_id }}</span>
          </div>
          <div class="info-item">
            <label>性别：</label>
            <span>{{ record.student?.gender }}</span>
          </div>
          <div class="info-item">
            <label>年龄：</label>
            <span>{{ record.student?.age || "未知" }}</span>
          </div>
          <div class="info-item">
            <label>AI评估总结：</label>
            <span class="summary-text">{{ record.ai_summary || "无" }}</span>
          </div>
        </div>
      </el-card>

      <!-- 问卷得分分析 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>问卷得分分析</span>
            <el-button type="text" @click="downloadScoreData"
              >下载得分数据</el-button
            >
          </div>
        </template>
        <div ref="scoreChart" class="chart-container"></div>
      </el-card>

      <!-- 生理数据趋势 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>生理数据趋势</span>
            <el-button type="text" @click="downloadPhysData"
              >下载生理数据</el-button
            >
          </div>
        </template>
        <div ref="physChart" class="chart-container"></div>
      </el-card>

      <!-- 详细数据表格 -->
      <el-card class="data-card">
        <template #header>
          <div class="card-header">
            <span>详细数据</span>
          </div>
        </template>
        <el-tabs v-model="activeTab" @tab-click="handleTabChange">
          <el-tab-pane label="问卷得分" name="scores">
            <el-table :data="record.scores" border stripe>
              <el-table-column
                prop="module_name"
                label="模块名称"
                align="center"
              ></el-table-column>
              <el-table-column prop="score" label="得分" align="center">
                <template #default="scope">
                  <span
                    :class="{
                      'high-score': scope.row.score > 20,
                      'warning-score': scope.row.score > 15,
                    }"
                  >
                    {{ scope.row.score }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="生理数据" name="physiological">
            <el-table :data="record.physiological_data" border stripe>
              <el-table-column
                prop="data_key"
                label="数据项"
                align="center"
              ></el-table-column>
              <el-table-column
                prop="data_value"
                label="数值"
                align="center"
              ></el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import service from "@/http";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";

export default {
  name: "TestRecordDetailView",
  setup() {
    const route = useRoute();
    const recordId = route.params.id;
    const loading = ref(true);
    const error = ref(null);
    const record = ref({});
    const scoreChart = ref(null);
    const physChart = ref(null);
    const scoreChartInstance = ref(null);
    const physChartInstance = ref(null);
    const activeTab = ref("scores");

    const fetchRecordDetail = async () => {
      try {
        const recordRes = await service.get(`/test-data/records/${recordId}`);
        record.value = recordRes.data;

        // 如果记录中没有用户信息，尝试获取
        if (!record.value.user && record.value.user_id) {
          try {
            const studentRes = await service.get(
              `/api/students/info/${record.value.user_id}`
            );
            record.value.user = studentRes.data;
          } catch (studentErr) {
            console.warn(
              "获取学生信息失败:",
              studentErr.response?.data?.detail
            );
          }
        }
      } catch (err) {
        error.value = err.response?.data?.detail || "获取记录详情失败";
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString) => {
      return dateString ? new Date(dateString).toLocaleString() : "";
    };

    const initScoreChart = () => {
      if (!scoreChart.value) return;

      scoreChartInstance.value = echarts.init(scoreChart.value);

      const scores = record.value.scores || [];

      const option = {
        title: {
          text: "问卷得分分布",
          left: "center",
        },
        tooltip: {
          trigger: "item",
          formatter: "{b}: {c} 分",
        },
        radar: {
          indicator: [
            { name: "焦虑", max: 30 },
            { name: "抑郁", max: 30 },
            { name: "压力", max: 30 },
          ],
          radius: "80%",
        },
        series: [
          {
            type: "radar",
            data: [
              {
                value: scores.map((s) => s.score),
                name: "得分",
                areaStyle: {
                  color: "rgba(54, 162, 235, 0.2)",
                },
                lineStyle: {
                  color: "rgba(54, 162, 235, 1)",
                },
              },
            ],
          },
        ],
      };

      scoreChartInstance.value.setOption(option);
    };

    const initPhysChart = () => {
      if (!physChart.value) return;

      physChartInstance.value = echarts.init(physChart.value);

      const physData = record.value.physiological_data || [];
      const categories = [...new Set(physData.map((item) => item.data_key))];
      const series = [];

      categories.forEach((category) => {
        const categoryData = physData.filter(
          (item) => item.data_key === category
        );
        series.push({
          name: category,
          type: "line",
          data: categoryData.map((item) => item.data_value),
          smooth: true,
        });
      });

      const option = {
        title: {
          text: "生理数据趋势",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
        },
        legend: {
          data: categories,
          top: 30,
        },
        xAxis: {
          type: "category",
          data: physData.map((_, index) => `数据${index + 1}`),
        },
        yAxis: {
          type: "value",
        },
        series: series,
      };

      physChartInstance.value.setOption(option);
    };

    const downloadScoreData = () => {
      const scores = record.value.scores || [];
      let csvContent = "模块名称,得分\n";
      scores.forEach((score) => {
        csvContent += `${score.module_name},${score.score}\n`;
      });

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `问卷得分_${record.value.student?.name}_${
        new Date().toISOString().split("T")[0]
      }.csv`;
      link.click();
      ElMessage.success("得分数据已下载");
    };

    const downloadPhysData = () => {
      const physData = record.value.physiological_data || [];
      let csvContent = "数据项,数值\n";
      physData.forEach((item) => {
        csvContent += `${item.data_key},${item.data_value}\n`;
      });

      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `生理数据_${record.value.student?.name}_${
        new Date().toISOString().split("T")[0]
      }.csv`;
      link.click();
      ElMessage.success("生理数据已下载");
    };

    const handleResize = () => {
      if (scoreChartInstance.value) {
        scoreChartInstance.value.resize();
      }
      if (physChartInstance.value) {
        physChartInstance.value.resize();
      }
    };

    const handleTabChange = (tab) => {
      setTimeout(() => {
        if (tab.props.name === "scores" && scoreChart.value) {
          initScoreChart();
        } else if (tab.props.name === "physiological" && physChart.value) {
          initPhysChart();
        }
      }, 100);
    };

    onMounted(() => {
      fetchRecordDetail().then(() => {
        // 数据加载完成后初始化图表
        setTimeout(() => {
          initScoreChart();
          initPhysChart();
        }, 100);
      });
      window.addEventListener("resize", handleResize);
    });

    onUnmounted(() => {
      window.removeEventListener("resize", handleResize);
      if (scoreChartInstance.value) {
        scoreChartInstance.value.dispose();
      }
      if (physChartInstance.value) {
        physChartInstance.value.dispose();
      }
    });

    return {
      loading,
      error,
      record,
      scoreChart,
      physChart,
      activeTab,
      formatDate,
      downloadScoreData,
      downloadPhysData,
      handleTabChange,
    };
  },
};
</script>

<style scoped>
.record-detail {
  padding: 32px;
  max-width: 1200px;
  margin: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
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

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card,
.chart-card,
.data-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-weight: 600;
  color: var(--text-sub);
  font-size: 14px;
}

.info-item span {
  font-size: 16px;
}

.summary-text {
  word-break: break-word;
  line-height: 1.6;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.high-score {
  color: #f56c6c;
  font-weight: bold;
}

.warning-score {
  color: #e6a23c;
  font-weight: 600;
}
</style>
