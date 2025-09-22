<template>
  <div class="records-wrapper">
    <h2 class="page-title">心理检测记录</h2>

    <!-- 筛选与功能区 -->
    <div class="filter-bar">
      <!-- 视图切换 -->
      <div class="view-toggle">
        <button
          @click="viewMode = 'grid'"
          :class="{ active: viewMode === 'grid' }"
          class="filter-btn"
        >
          大图标
        </button>
        <button
          @click="viewMode = 'list'"
          :class="{ active: viewMode === 'list' }"
          class="filter-btn"
        >
          列表
        </button>
      </div>

      <!-- 筛选组件 -->
      <input v-model="filterUserId" placeholder="用户ID" class="filter-input" />
      <input v-model="filterUserName" placeholder="姓名" class="filter-input" />
      <input v-model="filterClass" placeholder="班级" class="filter-input" />
      <select v-model="filterGender" class="filter-input">
        <option :value="null">全部性别</option>
        <option value="男">男</option>
        <option value="女">女</option>
      </select>
      <input v-model="filterStartDate" type="date" class="filter-input" />
      <input v-model="filterEndDate" type="date" class="filter-input" />
      <select v-model="filterIsAbnormal" class="filter-input">
        <option :value="null">全部</option>
        <option :value="true">异常</option>
        <option :value="false">正常</option>
      </select>
      <select v-model="filterStatus" class="filter-input">
        <option :value="null">全部状态</option>
        <option value="pending">待处理</option>
        <option value="processing">处理中</option>
        <option value="completed">已完成</option>
        <option value="failed">失败</option>
      </select>

      <!-- 操作按钮 -->
      <button @click="fetchRecords" class="filter-btn primary">筛选</button>
      <button @click="resetFilters" class="filter-btn">重置</button>
      <button @click="openImportModal" class="filter-btn primary">
        导入Excel
      </button>

      <!-- 数据导出按钮 -->
      <div class="export-actions">
        <button @click="exportStudents" class="filter-btn primary">
          导出学生数据
        </button>
        <button @click="exportTestRecords" class="filter-btn primary">
          导出检测记录
        </button>
        <button @click="exportDashboardStats" class="filter-btn primary">
          导出统计数据
        </button>
      </div>

      <!-- 批量操作按钮 -->
      <div v-if="selectedRecords.length > 0" class="batch-actions">
        <span class="batch-count"
          >已选择 {{ selectedRecords.length }} 条记录</span
        >
        <button @click="batchGenerateReports" class="filter-btn primary">
          批量生成报告
        </button>
        <button @click="batchUpdateStatus" class="filter-btn">
          批量更新状态
        </button>
        <button @click="clearSelection" class="filter-btn">取消选择</button>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore && !loading" class="load-more">
        <button @click="loadMore" :disabled="loadingMore" class="load-more-btn">
          {{ loadingMore ? "加载中..." : "加载更多" }}
        </button>
      </div>
    </div>

    <!-- Excel导入模态框 -->
    <div v-if="importModalVisible" class="modal">
      <div class="modal-content">
        <h3>导入学生检测记录</h3>
        <input
          type="file"
          ref="fileInput"
          class="file-input"
          accept=".xlsx,.xls"
          @change="handleFileSelect"
        />
        <button @click="uploadExcel" class="filter-btn primary mt-4">
          开始导入
        </button>
        <button @click="importModalVisible = false" class="filter-btn mt-2">
          取消
        </button>
      </div>
    </div>

    <!-- 加载状态指示器 -->
    <div v-if="loading || loadingMore" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <span>{{
          loadingMore ? "加载更多数据..." : "正在加载检测记录..."
        }}</span>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && records.length === 0" class="empty-state">
      <div class="empty-icon">
        <img src="@/assets/img/empty.svg" alt="暂无数据" />
      </div>
      <h3>暂无检测记录</h3>
      <p>点击"导入Excel"按钮开始导入学生数据</p>
      <button @click="openImportModal" class="filter-btn primary">
        导入Excel
      </button>
    </div>

    <!-- 数据展示区域 -->
    <div
      v-if="!loading && records.length > 0"
      :class="{
        masonry: viewMode === 'grid',
        'list-view': viewMode === 'list',
      }"
      @scroll="handleScroll"
      ref="scrollContainer"
    >
      <div
        v-for="r in records"
        :key="r.id"
        class="record-card"
        :class="{ selected: selectedRecords.includes(r.id) }"
        @click="viewDetail(r.id)"
      >
        <!-- 复选框 -->
        <div class="checkbox-wrapper" @click.stop="toggleSelection(r.id)">
          <input
            type="checkbox"
            :checked="selectedRecords.includes(r.id)"
            class="record-checkbox"
          />
        </div>

        <div class="record-content">
          <div class="record-avatar">
            {{ r.student?.name?.charAt(0) || "?" }}
          </div>
          <h3>{{ r.student?.name }}</h3>
          <p class="sub">
            {{ r.student?.student_id }} · {{ formatDate(r.test_time) }}
          </p>
          <p class="summary">{{ truncateText(r.ai_summary, 30) }}</p>

          <!-- 状态标签 -->
          <div class="status-tags">
            <div class="tag" :class="{ abnormal: r.is_abnormal }">
              {{ r.is_abnormal ? "异常" : "正常" }}
            </div>
            <div class="status-tag" :class="r.status">
              {{ getStatusText(r.status) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量更新状态模态框 -->
    <div v-if="showStatusModal" class="modal">
      <div class="modal-content">
        <h3>批量更新状态</h3>
        <p>选择要更新的状态：</p>
        <div class="status-options">
          <button
            v-for="status in statusOptions"
            :key="status.value"
            @click="selectBatchStatus(status.value)"
            :class="{ active: selectedBatchStatus === status.value }"
            class="status-btn"
          >
            {{ status.label }}
          </button>
        </div>
        <div class="modal-actions">
          <button @click="confirmBatchUpdateStatus" class="filter-btn primary">
            确认更新
          </button>
          <button @click="showStatusModal = false" class="filter-btn">
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 回顶部按钮 -->
    <transition name="fade">
      <button v-if="showBackTop" class="back-top" @click="backTop">↑</button>
    </transition>
  </div>
</template>

<script>
import { ElMessage } from "element-plus";
import router from "@/router";
import service from "@/http"; // ✅ 唯一用到的实例

export default {
  name: "TestRecordsView",
  data() {
    return {
      records: [],
      loading: false,
      error: null,
      filterUserId: "",
      filterUserName: "",
      filterClass: "",
      filterGender: null,
      filterStartDate: "",
      filterEndDate: "",
      filterIsAbnormal: null,
      filterStatus: null,
      showBackTop: false,
      viewMode: "grid", // 视图模式（grid/list）
      importModalVisible: false, // 导入模态框显隐
      selectedFile: null, // 选中的Excel文件
      selectedRecords: [], // 选中的记录ID列表
      showStatusModal: false, // 状态更新模态框
      selectedBatchStatus: null, // 选中的批量状态
      statusOptions: [
        { value: "pending", label: "待处理" },
        { value: "processing", label: "处理中" },
        { value: "completed", label: "已完成" },
        { value: "failed", label: "失败" },
      ],
      // 懒加载相关
      currentPage: 1,
      pageSize: 20,
      hasMore: true,
      loadingMore: false,
      // 防抖相关
      debounceTimer: null,
      isFiltering: false,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.onScroll);
    this.fetchRecords();
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.onScroll);
    // 清理防抖定时器
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
  },
  methods: {
    onScroll() {
      this.showBackTop = window.scrollY > 300;
    },
    backTop() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    openImportModal() {
      this.importModalVisible = true;
    },
    handleFileSelect(e) {
      this.selectedFile = e.target.files[0];
    },
    async uploadExcel() {
      if (!this.selectedFile) {
        alert("请选择Excel文件");
        return;
      }
      const formData = new FormData();
      formData.append("file", this.selectedFile);
      try {
        const res = await service.post("/api/students/batch-import", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        alert(res.data.detail);
        this.importModalVisible = false;
        this.fetchRecords();
      } catch (err) {
        alert(err.response?.data?.detail || "导入失败");
      }
    },
    // 带防抖的筛选方法
    debouncedFetchRecords() {
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }
      this.debounceTimer = setTimeout(() => {
        this.fetchRecords();
      }, 500); // 500ms 防抖延迟
    },

    async fetchRecords() {
      if (this.isFiltering) return; // 防止重复请求

      this.isFiltering = true;
      this.loading = true;
      this.error = null;

      // 重置分页状态
      this.currentPage = 1;
      this.hasMore = true;

      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.push("/login");
          return;
        }

        const params = new URLSearchParams();
        if (this.filterUserId) params.append("user_id", this.filterUserId);
        if (this.filterUserName)
          params.append("user_name", this.filterUserName);
        if (this.filterClass) params.append("class_name", this.filterClass);
        if (this.filterGender !== null)
          params.append("gender", this.filterGender);
        if (this.filterStartDate) {
          const startDate = new Date(this.filterStartDate);
          if (!isNaN(startDate.getTime())) {
            params.append("start_time", startDate.toISOString());
          }
        }
        if (this.filterEndDate) {
          const endDate = new Date(this.filterEndDate);
          if (!isNaN(endDate.getTime())) {
            endDate.setDate(endDate.getDate() + 1);
            endDate.setMilliseconds(-1);
            params.append("end_time", endDate.toISOString());
          }
        }
        if (this.filterIsAbnormal !== null)
          params.append("is_abnormal", this.filterIsAbnormal);
        if (this.filterStatus !== null)
          params.append("status", this.filterStatus);

        // 添加分页参数
        params.append("skip", 0);
        params.append("limit", this.pageSize);

        const res = await service.get("/test-data/records/", { params });
        this.records = res.data;

        // 检查是否还有更多数据
        if (res.data.length < this.pageSize) {
          this.hasMore = false;
        }
      } catch (err) {
        this.error = "无法加载检测记录。请检查网络或稍后再试。";
        if (err.response?.status === 401) {
          alert("认证失败，请重新登录。");
          localStorage.removeItem("access_token");
          router.push("/login");
        }
      } finally {
        this.loading = false;
        this.isFiltering = false;
      }
    },
    resetFilters() {
      Object.assign(this.$data, {
        filterUserId: "",
        filterUserName: "",
        filterClass: "",
        filterGender: null,
        filterStartDate: "",
        filterEndDate: "",
        filterIsAbnormal: null,
        filterStatus: null,
        selectedRecords: [],
      });
      this.fetchRecords();
    },
    formatDate(dateString) {
      return dateString ? new Date(dateString).toLocaleString() : "";
    },
    truncateText(text, maxLength) {
      if (!text) return "";
      return text.length <= maxLength
        ? text
        : text.substring(0, maxLength) + "...";
    },
    viewDetail(id) {
      router.push(`/test-records/${id}`);
    },

    // 批量操作相关方法
    toggleSelection(recordId) {
      const index = this.selectedRecords.indexOf(recordId);
      if (index > -1) {
        this.selectedRecords.splice(index, 1);
      } else {
        this.selectedRecords.push(recordId);
      }
    },

    clearSelection() {
      this.selectedRecords = [];
    },

    async batchGenerateReports() {
      if (this.selectedRecords.length === 0) {
        alert("请先选择要生成报告的记录");
        return;
      }

      try {
        // 调用后端的批量生成报告接口
        const response = await service.post(
          "/api/test-records/batch-generate-reports",
          {
            record_ids: this.selectedRecords,
            format: "pdf",
          }
        );

        alert(`成功生成 ${response.data.report_files.length} 份报告`);
        this.clearSelection();

        // 可选：自动下载报告文件
        if (response.data.report_files.length > 0) {
          response.data.report_files.forEach((file) => {
            // 创建下载链接
            const link = document.createElement("a");
            link.href = `/api/reports/${file.student_id}/download?format=pdf`;
            link.download = file.file_name;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          });
        }
      } catch (error) {
        alert(
          "批量生成报告失败：" + (error.response?.data?.detail || error.message)
        );
      }
    },

    batchUpdateStatus() {
      if (this.selectedRecords.length === 0) {
        alert("请先选择要更新状态的记录");
        return;
      }
      this.showStatusModal = true;
    },

    selectBatchStatus(status) {
      this.selectedBatchStatus = status;
    },

    async confirmBatchUpdateStatus() {
      if (!this.selectedBatchStatus) {
        alert("请选择要更新的状态");
        return;
      }

      try {
        // 批量更新状态
        const updatePromises = this.selectedRecords.map((recordId) =>
          service.put(`/api/test-records/${recordId}/status`, {
            status: this.selectedBatchStatus,
          })
        );

        await Promise.all(updatePromises);

        alert(`成功更新 ${this.selectedRecords.length} 条记录的状态`);
        this.showStatusModal = false;
        this.clearSelection();
        this.fetchRecords();
      } catch (error) {
        alert(
          "批量更新状态失败：" + (error.response?.data?.detail || error.message)
        );
      }
    },

    getStatusText(status) {
      const statusMap = {
        pending: "待处理",
        processing: "处理中",
        completed: "已完成",
        failed: "失败",
      };
      return statusMap[status] || status;
    },

    // 数据导出方法
    async exportStudents() {
      try {
        const response = await service.get("/api/export/students", {
          responseType: "blob",
        });

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute(
          "download",
          `学生数据_${new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/:/g, "-")}.xlsx`
        );
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        ElMessage.success("学生数据导出成功");
      } catch (error) {
        ElMessage.error(
          "学生数据导出失败：" + (error.response?.data?.detail || error.message)
        );
      }
    },

    async exportTestRecords() {
      try {
        // 构建导出参数
        const params = new URLSearchParams();
        if (this.filterUserId) params.append("user_id", this.filterUserId);
        if (this.filterStartDate)
          params.append(
            "start_time",
            new Date(this.filterStartDate).toISOString()
          );
        if (this.filterEndDate) {
          const end = new Date(this.filterEndDate);
          end.setDate(end.getDate() + 1);
          end.setMilliseconds(-1);
          params.append("end_time", end.toISOString());
        }
        if (this.filterIsAbnormal !== null)
          params.append("is_abnormal", this.filterIsAbnormal);
        if (this.filterStatus !== null)
          params.append("status", this.filterStatus);

        const response = await service.get(
          `/api/export/test-records?${params.toString()}`,
          {
            responseType: "blob",
          }
        );

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute(
          "download",
          `检测记录数据_${new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/:/g, "-")}.xlsx`
        );
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        ElMessage.success("检测记录数据导出成功");
      } catch (error) {
        ElMessage.error(
          "检测记录数据导出失败：" +
            (error.response?.data?.detail || error.message)
        );
      }
    },

    async exportDashboardStats() {
      try {
        const response = await service.get("/api/export/dashboard-stats", {
          responseType: "blob",
        });

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute(
          "download",
          `仪表板统计数据_${new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/:/g, "-")}.xlsx`
        );
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);

        ElMessage.success("仪表板统计数据导出成功");
      } catch (error) {
        ElMessage.error(
          "仪表板统计数据导出失败：" +
            (error.response?.data?.detail || error.message)
        );
      }
    },

    // 懒加载相关方法
    handleScroll(event) {
      const { scrollTop, scrollHeight, clientHeight } = event.target;
      const scrollPosition = scrollHeight - scrollTop - clientHeight;

      // 当滚动到底部附近时加载更多
      if (scrollPosition < 100 && this.hasMore && !this.loadingMore) {
        this.loadMore();
      }
    },

    async loadMore() {
      if (this.loadingMore || !this.hasMore) return;

      this.loadingMore = true;
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          router.push("/login");
          return;
        }

        const params = new URLSearchParams();
        // 添加分页参数
        params.append("skip", (this.currentPage - 1) * this.pageSize);
        params.append("limit", this.pageSize);

        // 添加筛选参数
        if (this.filterUserId) params.append("user_id", this.filterUserId);
        if (this.filterUserName)
          params.append("user_name", this.filterUserName);
        if (this.filterClass) params.append("class_name", this.filterClass);
        if (this.filterGender !== null)
          params.append("gender", this.filterGender);
        if (this.filterStartDate)
          params.append(
            "start_time",
            new Date(this.filterStartDate).toISOString()
          );
        if (this.filterEndDate) {
          const end = new Date(this.filterEndDate);
          end.setDate(end.getDate() + 1);
          end.setMilliseconds(-1);
          params.append("end_time", end.toISOString());
        }
        if (this.filterIsAbnormal !== null)
          params.append("is_abnormal", this.filterIsAbnormal);
        if (this.filterStatus !== null)
          params.append("status", this.filterStatus);

        const res = await service.get("/test-data/records/", { params });
        const newRecords = res.data;

        // 添加新记录到现有记录中
        this.records = [...this.records, ...newRecords];

        // 检查是否还有更多数据
        if (newRecords.length < this.pageSize) {
          this.hasMore = false;
        } else {
          this.currentPage++;
        }
      } catch (err) {
        console.error("加载更多数据失败:", err);
        ElMessage.error("加载更多数据失败");
      } finally {
        this.loadingMore = false;
      }
    },
  },
  created() {
    this.fetchRecords();
  },
};
</script>

<style scoped>
@import "@/assets/css/healing-theme.css";

.records-wrapper {
  padding: 32px;
  max-width: 1200px;
  margin: auto;
}

.page-title {
  text-align: center;
  margin-bottom: 32px;
  font-weight: 500;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
  justify-content: center;
}
.filter-input {
  padding: 8px 12px;
  border: 1px solid #d0d9dc;
  border-radius: var(--radius);
  background: var(--card-bg);
}
.filter-btn {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
}
.filter-btn.primary {
  background: var(--accent);
  color: #fff;
}

.masonry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.record-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: var(--transition);
}
.record-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}
.record-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 20px;
  margin-bottom: 8px;
}
h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}
.sub {
  color: var(--text-sub);
  font-size: 13px;
}
.summary {
  color: var(--text-sub);
  font-size: 14px;
}
.tag {
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: #fff;
  background: #6dbe6b;
}
.tag.abnormal {
  background: #e9897e;
}

.loading,
.empty {
  text-align: center;
  margin-top: 48px;
  color: var(--text-sub);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 48px;
  text-align: center;
  color: var(--text-sub);
}

.back-top {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 999;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  border: none;
  box-shadow: var(--shadow);
  cursor: pointer;
  transition: opacity 0.3s;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 批量操作样式 */
.batch-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 16px;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: var(--radius);
}

.batch-count {
  color: var(--text-sub);
  font-size: 14px;
}

.checkbox-wrapper {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 10;
}

.record-checkbox {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.record-card.selected {
  border: 2px solid var(--accent);
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.record-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.status-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-tag {
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 11px;
  color: #fff;
  font-weight: 500;
}

.status-tag.pending {
  background: #ffc107;
}

.status-tag.processing {
  background: #17a2b8;
}

.status-tag.completed {
  background: #28a745;
}

.status-tag.failed {
  background: #dc3545;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--radius);
  max-width: 500px;
  width: 90%;
  box-shadow: var(--shadow-hover);
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
}

.file-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #d0d9dc;
  border-radius: var(--radius);
  background: var(--card-bg);
  margin-bottom: 16px;
}

.status-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.status-btn {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: var(--radius);
  background: var(--card-bg);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.status-btn:hover {
  border-color: var(--accent);
  background: rgba(0, 123, 255, 0.05);
}

.status-btn.active {
  border-color: var(--accent);
  background: var(--accent);
  color: #fff;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.list-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.list-view .record-card {
  display: flex;
  align-items: center;
  padding: 16px;
  flex-direction: row;
}

.list-view .record-avatar {
  width: 40px;
  height: 40px;
  font-size: 16px;
  margin-right: 16px;
  margin-bottom: 0;
}

.list-view .record-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.list-view .status-tags {
  flex-direction: row;
  gap: 8px;
}

/* 数据导出按钮组样式 */
.export-actions {
  display: flex;
  gap: 8px;
  margin-left: 16px;
}

/* 加载更多按钮样式 */
.load-more {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  margin-bottom: 32px;
}

.load-more-btn {
  padding: 12px 24px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: var(--transition);
  font-size: 14px;
  font-weight: 500;
}

.load-more-btn:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.load-more-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载状态指示器样式 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-spinner span {
  color: var(--text);
  font-size: 14px;
  font-weight: 500;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 60px 20px;
  text-align: center;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin: 40px 0;
}

.empty-icon {
  width: 80px;
  height: 80px;
  opacity: 0.6;
}

.empty-state h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text);
}

.empty-state p {
  margin: 0;
  color: var(--text-sub);
  font-size: 14px;
  line-height: 1.6;
  max-width: 400px;
}

.empty-state .filter-btn {
  margin-top: 8px;
}

/* 虚拟滚动优化样式 */
.masonry,
.list-view {
  height: calc(100vh - 200px);
  overflow-y: auto;
  padding-right: 8px;
}

.masonry::-webkit-scrollbar,
.list-view::-webkit-scrollbar {
  width: 8px;
}

.masonry::-webkit-scrollbar-track,
.list-view::-webkit-scrollbar-track {
  background: var(--card-bg);
  border-radius: 4px;
}

.masonry::-webkit-scrollbar-thumb,
.list-view::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.masonry::-webkit-scrollbar-thumb:hover,
.list-view::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 记录项进入动画 */
.record-card {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.5s ease forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 性能优化：减少重绘 */
.record-card {
  will-change: transform, opacity;
  contain: layout style paint;
}

/* 大数据量时的性能优化 */
.masonry {
  contain: layout style paint;
}

.list-view {
  contain: layout style paint;
}
</style>
