<template>
  <div class="student-management">
    <h2 class="page-title">学生信息管理</h2>

    <!-- 筛选与功能区 -->
    <div class="filter-bar">
      <input v-model="filterName" placeholder="姓名" class="filter-input" />
      <input
        v-model="filterStudentId"
        placeholder="学号"
        class="filter-input"
      />
      <input v-model="filterClass" placeholder="班级" class="filter-input" />
      <select v-model="filterGender" class="filter-input">
        <option :value="null">全部性别</option>
        <option value="男">男</option>
        <option value="女">女</option>
      </select>

      <select v-model="sortBy" class="filter-input">
        <option value="name">按姓名</option>
        <option value="student_id">按学号</option>
        <option value="class_name">按班级</option>
        <option value="created_at">按创建时间</option>
      </select>

      <select v-model="sortOrder" class="filter-input">
        <option value="asc">升序</option>
        <option value="desc">降序</option>
      </select>

      <button @click="fetchStudents" class="filter-btn primary">筛选</button>
      <button @click="resetFilters" class="filter-btn">重置</button>
      <button @click="openAddDialog" class="filter-btn primary">
        新增学生
      </button>
      <button @click="refreshStudents" class="filter-btn">刷新</button>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table
        :data="paginatedStudents"
        border
        stripe
        v-loading="loading"
        @sort-change="handleSortChange"
      >
        <el-table-column
          prop="name"
          label="姓名"
          align="center"
          sortable="custom"
        ></el-table-column>
        <el-table-column
          prop="student_id"
          label="学号"
          align="center"
          sortable="custom"
        ></el-table-column>
        <el-table-column
          prop="class_name"
          label="班级"
          align="center"
          sortable="custom"
        ></el-table-column>
        <el-table-column
          prop="gender"
          label="性别"
          align="center"
          sortable="custom"
        ></el-table-column>
        <el-table-column
          prop="created_at"
          label="创建时间"
          align="center"
          :formatter="formatDate"
          sortable="custom"
        ></el-table-column>
        <el-table-column label="操作" align="center" width="150">
          <template #default="scope">
            <el-button type="text" @click="openEditDialog(scope.row)"
              >编辑</el-button
            >
            <el-button
              type="text"
              @click="deleteStudent(scope.row)"
              style="color: #f56c6c"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="filteredStudents.length"
        >
        </el-pagination>
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="40%">
      <el-form :model="form" :rules="rules" ref="formRef">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="学号" prop="student_id">
          <el-input
            v-model="form.student_id"
            @blur="validateStudentId"
          ></el-input>
        </el-form-item>
        <el-form-item label="班级" prop="class_name">
          <el-input v-model="form.class_name"></el-input>
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-select v-model="form.gender" placeholder="请选择性别">
            <el-option label="男" value="男"></el-option>
            <el-option label="女" value="女"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveStudent">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog title="确认删除" v-model="deleteDialogVisible" width="30%">
      <p>是否确认删除该学生信息？</p>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="deleteDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDelete">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import service from "@/http";

export default {
  name: "StudentManagement",
  setup() {
    // 基础数据
    const students = ref([]);
    const dialogVisible = ref(false);
    const deleteDialogVisible = ref(false);
    const dialogTitle = ref("新增学生");
    const formRef = ref(null);
    const selectedStudent = ref(null);
    const loading = ref(false);

    // 表单数据
    const form = reactive({
      name: "",
      student_id: "",
      class_name: "",
      gender: "",
    });

    // 验证规则
    const rules = reactive({
      name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
      student_id: [{ required: true, message: "请输入学号", trigger: "blur" }],
      class_name: [{ required: true, message: "请输入班级", trigger: "blur" }],
      gender: [{ required: true, message: "请选择性别", trigger: "change" }],
    });

    // 筛选条件
    const filterName = ref("");
    const filterStudentId = ref("");
    const filterClass = ref("");
    const filterGender = ref(null);
    const sortBy = ref("name");
    const sortOrder = ref("asc");

    // 分页
    const currentPage = ref(1);
    const pageSize = ref(10);

    // 获取学生列表
    const fetchStudents = async () => {
      loading.value = true;
      try {
        const res = await service.get("/api/students");
        students.value = res.data;
      } catch (err) {
        console.error("获取学生信息失败:", err);
      } finally {
        loading.value = false;
      }
    };

    // 刷新学生列表
    const refreshStudents = () => {
      fetchStudents();
    };

    // 打开新增对话框
    const openAddDialog = () => {
      dialogTitle.value = "新增学生";
      form.name = "";
      form.student_id = "";
      form.class_name = "";
      form.gender = "";
      selectedStudent.value = null;
      dialogVisible.value = true;
    };

    // 打开编辑对话框
    const openEditDialog = (student) => {
      dialogTitle.value = "编辑学生";
      form.name = student.name;
      form.student_id = student.student_id;
      form.class_name = student.class_name;
      form.gender = student.gender;
      selectedStudent.value = student;
      dialogVisible.value = true;
    };

    // 验证学号
    const validateStudentId = async () => {
      if (!form.student_id) return;
      try {
        await service.post("/api/students/validate", {
          student_id: form.student_id,
        });
        if (formRef.value) {
          formRef.value.setFieldError("student_id", "学号已存在");
        }
      } catch (err) {
        if (err.response?.status === 404) {
          if (formRef.value) {
            formRef.value.clearValidate("student_id");
          }
        }
      }
    };

    // 保存学生
    const saveStudent = async () => {
      if (!formRef.value) return;
      await formRef.value.validate();
      try {
        if (selectedStudent.value) {
          await service.put(
            `/api/students/${selectedStudent.value.student_id}`,
            form
          );
        } else {
          await service.post("/api/students", form);
        }
        dialogVisible.value = false;
        fetchStudents();
      } catch (err) {
        console.error("保存学生信息失败:", err);
      }
    };

    // 删除学生
    const deleteStudent = (student) => {
      selectedStudent.value = student;
      deleteDialogVisible.value = true;
    };

    // 确认删除
    const confirmDelete = async () => {
      try {
        await service.delete(
          `/api/students/${selectedStudent.value.student_id}`
        );
        deleteDialogVisible.value = false;
        fetchStudents();
      } catch (err) {
        console.error("删除学生信息失败:", err);
      }
    };

    // 重置筛选条件
    const resetFilters = () => {
      filterName.value = "";
      filterStudentId.value = "";
      filterClass.value = "";
      filterGender.value = null;
      sortBy.value = "name";
      sortOrder.value = "asc";
      currentPage.value = 1;
      fetchStudents();
    };

    // 处理排序变化
    const handleSortChange = ({ prop, order }) => {
      if (prop) {
        sortBy.value = prop;
        sortOrder.value = order || "asc";
      }
    };

    // 处理页面大小变化
    const handleSizeChange = (size) => {
      pageSize.value = size;
      currentPage.value = 1;
    };

    // 处理页码变化
    const handleCurrentChange = (page) => {
      currentPage.value = page;
    };

    // 计算筛选后的学生列表
    const filteredStudents = computed(() => {
      let result = [...students.value];

      // 姓名筛选
      if (filterName.value) {
        result = result.filter((student) =>
          student.name?.toLowerCase().includes(filterName.value.toLowerCase())
        );
      }

      // 学号筛选
      if (filterStudentId.value) {
        result = result.filter((student) =>
          student.student_id
            ?.toLowerCase()
            .includes(filterStudentId.value.toLowerCase())
        );
      }

      // 班级筛选
      if (filterClass.value) {
        result = result.filter((student) =>
          student.class_name
            ?.toLowerCase()
            .includes(filterClass.value.toLowerCase())
        );
      }

      // 性别筛选
      if (filterGender.value !== null) {
        result = result.filter(
          (student) => student.gender === filterGender.value
        );
      }

      // 排序
      result.sort((a, b) => {
        const aValue = a[sortBy.value] || "";
        const bValue = b[sortBy.value] || "";

        if (sortOrder.value === "asc") {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      });

      return result;
    });

    // 计算分页后的学生列表
    const paginatedStudents = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value;
      const end = start + pageSize.value;
      return filteredStudents.value.slice(start, end);
    });

    onMounted(() => {
      fetchStudents();
    });

    return {
      // 数据
      students,
      dialogVisible,
      deleteDialogVisible,
      dialogTitle,
      formRef,
      form,
      rules,
      selectedStudent,
      loading,

      // 筛选条件
      filterName,
      filterStudentId,
      filterClass,
      filterGender,
      sortBy,
      sortOrder,

      // 分页
      currentPage,
      pageSize,

      // 计算属性
      filteredStudents,
      paginatedStudents,

      // 方法
      refreshStudents,
      openAddDialog,
      openEditDialog,
      validateStudentId,
      saveStudent,
      deleteStudent,
      confirmDelete,
      resetFilters,
      handleSortChange,
      handleSizeChange,
      handleCurrentChange,
      formatDate: (row) =>
        row.created_at ? new Date(row.created_at).toLocaleString() : "",
    };
  },
};
</script>

<style scoped>
.student-management {
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
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  align-items: center;
}

.filter-input {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.filter-input:focus {
  outline: none;
  border-color: #409eff;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.filter-btn.primary {
  background: #409eff;
  color: #fff;
  border-color: #409eff;
}

.filter-btn.primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}

.table-container {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-input {
    min-width: auto;
  }

  .filter-btn {
    width: 100%;
  }
}
</style>
