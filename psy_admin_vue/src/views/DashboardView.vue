<template>
  <div class="dashboard">
    <h2 class="page-title">系统概览</h2>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon total">
            <i class="el-icon-user"></i>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ totalStudents }}</div>
            <div class="stat-label">总学生数</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon records">
            <i class="el-icon-document"></i>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ totalRecords }}</div>
            <div class="stat-label">检测记录</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon abnormal">
            <i class="el-icon-warning"></i>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ abnormalCount }}</div>
            <div class="stat-label">异常记录</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon today">
            <i class="el-icon-date"></i>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ todayRecords }}</div>
            <div class="stat-label">今日检测</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 检测趋势图 - 已注释 -->
      <!--
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>检测趋势分析</span>
            <el-select
              v-model="trendPeriod"
              @change="fetchTrendData"
              style="width: 120px"
            >
              <el-option label="最近7天" value="7"></el-option>
              <el-option label="最近30天" value="30"></el-option>
              <el-option label="最近90天" value="90"></el-option>
            </el-select>
          </div>
        </template>
        <div ref="trendChart" class="chart-container"></div>
      </el-card>
      -->

      <!-- 异常分布图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>异常状态分布</span>
          </div>
        </template>
        <div ref="abnormalChart" class="chart-container"></div>
      </el-card>

      <!-- 班级分布 -->
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>班级学生分布</span>
          </div>
        </template>
        <div ref="classChart" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>最近检测记录</span>
          <el-button v-if="false" type="primary" @click="exportData">
            导出数据
          </el-button>
        </div>
      </template>
      <el-table :data="recentRecords" border stripe v-loading="loading">
        <el-table-column
          prop="student.name"
          label="学生姓名"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="student.student_id"
          label="学号"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="student.class_name"
          label="班级"
          align="center"
        ></el-table-column>
        <el-table-column
          prop="test_time"
          label="检测时间"
          align="center"
          :formatter="formatDate"
        ></el-table-column>
        <el-table-column prop="is_abnormal" label="状态" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_abnormal ? 'danger' : 'success'">
              {{ scope.row.is_abnormal ? "异常" : "正常" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="scope">
            <el-button type="text" @click="viewDetail(scope.row.id)"
              >查看详情</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import service from "@/http";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";

export default {
  name: "DashboardView",
  setup() {
    const router = useRouter();
    const loading = ref(true);

    // 统计数据
    const totalStudents = ref(0);
    const totalRecords = ref(0);
    const abnormalCount = ref(0);
    const todayRecords = ref(0);

    // 图表引用
    const trendChart = ref(null);
    const abnormalChart = ref(null);
    const scoreChart = ref(null);
    const classChart = ref(null);

    // 图表实例
    const trendChartInstance = ref(null);
    const abnormalChartInstance = ref(null);
    const scoreChartInstance = ref(null);
    const classChartInstance = ref(null);

    // 最近记录
    const recentRecords = ref([]);
    const trendPeriod = ref("7");

    // 获取统计数据
    const fetchStats = async () => {
      try {
        const res = await service.get("/api/dashboard/stats");
        const stats = res.data;

        totalStudents.value = stats.total_students;
        totalRecords.value = stats.total_records;
        abnormalCount.value = stats.abnormal_count;
        todayRecords.value = stats.today_records;
      } catch (error) {
        console.error("获取统计数据失败:", error);
      }
    };

    // 获取最近记录
    const fetchRecentRecords = async () => {
      try {
        const res = await service.get(
          "/test-data/records/?limit=10&sort_by=test_time&sort_order=desc"
        );
        recentRecords.value = res.data;
      } catch (error) {
        console.error("获取最近记录失败:", error);
      }
    };

    // 获取趋势数据
    const fetchTrendData = async () => {
      try {
        const res = await service.get(
          `/api/dashboard/trend?days=${trendPeriod.value}`
        );
        const trendData = res.data;

        updateTrendChart(trendData.dates, trendData.values);
      } catch (error) {
        console.error("获取趋势数据失败:", error);
      }
    };

    // 更新趋势图表
    const updateTrendChart = (dates, values) => {
      if (!trendChartInstance.value) return;

      const option = {
        title: {
          text: `检测趋势 (${trendPeriod.value}天)`,
          left: "center",
        },
        tooltip: {
          trigger: "axis",
        },
        xAxis: {
          type: "category",
          data: dates,
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            data: values,
            type: "line",
            smooth: true,
            areaStyle: {
              color: "rgba(54, 162, 235, 0.2)",
            },
            lineStyle: {
              color: "rgba(54, 162, 235, 1)",
            },
          },
        ],
      };

      trendChartInstance.value.setOption(option);
    };

    // 更新异常分布图表
    const updateAbnormalChart = () => {
      if (!abnormalChartInstance.value) return;

      const normalCount = totalRecords.value - abnormalCount.value;

      const option = {
        title: {
          text: "异常状态分布",
          left: "center",
        },
        tooltip: {
          trigger: "item",
        },
        legend: {
          orient: "vertical",
          left: "left",
        },
        series: [
          {
            type: "pie",
            radius: "50%",
            data: [
              { value: normalCount, name: "正常" },
              { value: abnormalCount.value, name: "异常" },
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
          },
        ],
      };

      abnormalChartInstance.value.setOption(option);
    };

    // 更新得分统计图表
    const updateScoreChart = async () => {
      try {
        const res = await service.get("/api/dashboard/score-stats");
        const scoreDistribution = res.data;

        const series = Object.entries(scoreDistribution).map(
          ([name, distribution]) => ({
            name,
            type: "bar",
            data: Object.values(distribution),
            emphasis: {
              focus: "series",
            },
          })
        );

        if (scoreChartInstance.value) {
          scoreChartInstance.value.setOption({
            title: {
              text: "问卷得分分布",
              left: "center",
            },
            tooltip: {
              trigger: "axis",
              axisPointer: {
                type: "shadow",
              },
            },
            legend: {
              data: Object.keys(scoreDistribution),
              top: 30,
            },
            xAxis: {
              type: "category",
              data: ["0-10", "11-15", "16-20", "21-25", "26-30"],
            },
            yAxis: {
              type: "value",
            },
            series: series,
          });
        }
      } catch (error) {
        console.error("更新得分图表失败:", error);
      }
    };

    // 更新班级分布图表
    const updateClassChart = async () => {
      try {
        const res = await service.get("/api/dashboard/class-distribution");
        const classDistribution = res.data;

        const data = Object.entries(classDistribution).map(([name, value]) => ({
          value,
          name,
        }));

        if (classChartInstance.value) {
          classChartInstance.value.setOption({
            title: {
              text: "班级学生分布",
              left: "center",
            },
            tooltip: {
              trigger: "item",
            },
            series: [
              {
                type: "pie",
                radius: "50%",
                data: data,
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: "rgba(0, 0, 0, 0.5)",
                  },
                },
              },
            ],
          });
        }
      } catch (error) {
        console.error("更新班级图表失败:", error);
      }
    };

    // 初始化图表
    const initCharts = () => {
      if (trendChart.value) {
        trendChartInstance.value = echarts.init(trendChart.value);
      }
      if (abnormalChart.value) {
        abnormalChartInstance.value = echarts.init(abnormalChart.value);
      }
      if (scoreChart.value) {
        scoreChartInstance.value = echarts.init(scoreChart.value);
      }
      if (classChart.value) {
        classChartInstance.value = echarts.init(classChart.value);
      }
    };

    // 格式化日期
    const formatDate = (row) => {
      return row.test_time ? new Date(row.test_time).toLocaleString() : "";
    };

    // 查看详情
    const viewDetail = (id) => {
      router.push(`/test-records/${id}`);
    };

    // 导出数据
    const exportData = () => {
      ElMessage.success("数据导出功能开发中...");
    };

    // 处理窗口大小变化
    const handleResize = () => {
      if (trendChartInstance.value) trendChartInstance.value.resize();
      if (abnormalChartInstance.value) abnormalChartInstance.value.resize();
      if (scoreChartInstance.value) scoreChartInstance.value.resize();
      if (classChartInstance.value) classChartInstance.value.resize();
    };

    onMounted(async () => {
      loading.value = true;
      await fetchStats();
      await fetchRecentRecords();
      await fetchTrendData();

      initCharts();
      updateAbnormalChart();
      await updateScoreChart();
      await updateClassChart();

      window.addEventListener("resize", handleResize);
      loading.value = false;
    });

    onUnmounted(() => {
      window.removeEventListener("resize", handleResize);
      if (trendChartInstance.value) trendChartInstance.value.dispose();
      if (abnormalChartInstance.value) abnormalChartInstance.value.dispose();
      if (scoreChartInstance.value) scoreChartInstance.value.dispose();
      if (classChartInstance.value) classChartInstance.value.dispose();
    });

    return {
      loading,
      totalStudents,
      totalRecords,
      abnormalCount,
      todayRecords,
      recentRecords,
      trendPeriod,
      trendChart,
      abnormalChart,
      scoreChart,
      classChart,
      formatDate,
      viewDetail,
      exportData,
    };
  },
};
</script>

<style scoped>
.dashboard {
  padding: 32px;
  max-width: 1400px;
  margin: auto;
}

.page-title {
  text-align: center;
  margin-bottom: 32px;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.records {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.abnormal {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.stat-icon.today {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-container {
  width: 100%;
  height: 300px;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
