<template>
  <h2>资源库</h2>
  <!-- 资源列表 -->
  <div class="resource-list">
    <el-card v-for="resource in resourceList" :key="resource.id" class="resource-item" shadow="hover" @click="handleResourceClick(resource)">
      <div class="resource-content">
        <div class="resource-header">
          <el-checkbox :value="selectedResources.some(item => item.id === resource.id)"
            @change="(checked) => handleItemSelection(resource, checked)" class="resource-checkbox"></el-checkbox>
          <div class="resource-info">
            <h3 class="resource-filename">{{ resource.filename }}</h3>
            <!-- <div class="resource-meta">
                <el-tag :type="getFileTypeColor(resource.file_type)" size="small">{{ resource.file_type }}</el-tag>
                <span class="resource-user">{{ resource.user_username }}</span>
              </div> -->
          </div>
        </div>
        <div class="resource-time">
          <span style="padding-right: 120px;">{{ resource.user_username }}</span>
          <span>{{ formatTime(resource.upload_time) }}</span>
        </div>
      </div>
    </el-card>
  </div>
  <div style="margin-top: 16px;">
    <el-button type="primary" :disabled="selectedResources.length !== 1" @click="handlePractice">立即跟读</el-button>
    <!-- <el-button type="success" :disabled="selectedResources.length !== 1" @click="handleWordPractice">句子听读练习</el-button> -->
    <el-button type="primary" :disabled="selectedResources.length === 0" @click="addToTaskPlan">创建跟读任务</el-button>
    <el-button type="primary" @click="jumpToUpload">上传资源</el-button>
  </div>

  <!-- 创建任务对话框 -->
  <el-dialog v-model="taskDialogVisible" title="创建跟读任务" width="90%" :max-width="500">
    <el-form :model="taskForm" :rules="taskRules" ref="taskFormRef" label-width="100px">
      <el-form-item label="任务周期" prop="cycleType">
        <el-radio-group v-model="taskForm.cycleType">
          <el-radio label="daily">每天</el-radio>
          <el-radio label="weekly">每周</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="taskForm.cycleType === 'weekly'" label="选择星期" prop="weekDays">
        <el-checkbox-group v-model="taskForm.weekDays">
          <el-checkbox label="1">周一</el-checkbox>
          <el-checkbox label="2">周二</el-checkbox>
          <el-checkbox label="3">周三</el-checkbox>
          <el-checkbox label="4">周四</el-checkbox>
          <el-checkbox label="5">周五</el-checkbox>
          <el-checkbox label="6">周六</el-checkbox>
          <el-checkbox label="0">周日</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="开始日期" prop="startDate">
        <el-date-picker
          v-model="taskForm.startDate"
          type="date"
          placeholder="选择开始日期"
          :disabled-date="disabledDate"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="结束日期" prop="endDate">
        <el-date-picker
          v-model="taskForm.endDate"
          type="date"
          placeholder="选择结束日期"
          :disabled-date="disabledEndDate"
          style="width: 100%"
        />
      </el-form-item>
      <!-- <el-form-item label="任务类型" prop="taskType">
        <el-select v-model="taskForm.taskType" placeholder="选择任务类型" style="width: 100%">
          <el-option label="跟读练习" value="reading"></el-option>
          <el-option label="听力练习" value="listening"></el-option>
          <el-option label="口语练习" value="speaking"></el-option>
        </el-select>
      </el-form-item> -->
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTasks" :loading="creating">创建任务</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'
import apiService from '../services/apiService';
import { ElMessage } from 'element-plus';

interface ResourceFile {
  id: number;
  filename: string;
  file_type: string;
  user_username: string;
  upload_time: string;
}

const resourceList = ref<ResourceFile[]>([]);
const selectedResources = ref<ResourceFile[]>([]);
const router = useRouter();
const handleSelectionChange = (selection: ResourceFile[]) => {
    selectedResources.value = selection;
};

// 处理单个项目的选择
const handleItemSelection = (resource: ResourceFile, checked: boolean) => {
    if (checked) {
        if (!selectedResources.value.some(item => item.id === resource.id)) {
            selectedResources.value.push(resource);
        }
    } else {
        selectedResources.value = selectedResources.value.filter(item => item.id !== resource.id);
    }
};

// 获取文件类型对应的颜色
const getFileTypeColor = (fileType: string) => {
    const typeMap: { [key: string]: string } = {
        'txt': 'info',
        'pdf': 'danger',
        'doc': 'primary',
        'docx': 'primary',
        'mp3': 'success',
        'wav': 'success',
        'mp4': 'warning',
        'avi': 'warning'
    };
    return typeMap[fileType.toLowerCase()] || 'info';
};

// 格式化时间
const formatTime = (timeString: string) => {
    const date = new Date(timeString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};

const toLocalIsoTime = (timeString: string) => {
  const date = new Date(timeString);
  date.setHours(date.getHours() + 8);
  return date.toISOString();
}

const handlePractice = () => {
    const ids = selectedResources.value.map(item => item.id);
    console.log(ids);
    // 可以根据需要选择跳转到单词练习或句子练习
    // 默认跳转到单词练习
    router.push({ name: 'Practice', params: { id: ids[0] } });
};

const handleWordPractice = () => {
    const ids = selectedResources.value.map(item => item.id);
    console.log(ids);
    router.push({ name: 'WordPractice', params: { id: ids[0] } });
};

// 任务创建相关
const taskDialogVisible = ref(false);
const creating = ref(false);
const taskFormRef = ref();
const taskForm = ref({
  cycleType: 'daily', // 'daily' 或 'weekly'
  weekDays: [], // 选择的星期几，数组格式
  startDate: '',
  endDate: '',
  taskType: 'practice'
});

const taskRules = {
  cycleType: [{ required: true, message: '请选择任务周期', trigger: 'change' }],
  weekDays: [
    {
      validator: (rule: any, value: string[], callback: Function) => {
        if (taskForm.value.cycleType === 'weekly' && (!value || value.length === 0)) {
          callback(new Error('请至少选择一天'));
        } else {
          callback();
        }
      },
      trigger: 'change'
    }
  ],
  startDate: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  endDate: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  taskType: [{ required: true, message: '请选择任务类型', trigger: 'change' }]
};

// 禁用过去的日期
const disabledDate = (time: Date) => {
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000;
};

// 禁用结束日期（不能早于开始日期）
const disabledEndDate = (time: Date) => {
  const today = Date.now() - 24 * 60 * 60 * 1000;
  if (time.getTime() < today) {
    return true;
  }
  if (taskForm.value.startDate) {
    const startDate = new Date(taskForm.value.startDate).getTime();
    return time.getTime() < startDate;
  }
  return false;
};

const addToTaskPlan = () => {
  if (selectedResources.value.length === 0) {
    ElMessage.warning('请先选择资源');
    return;
  }
  
  // 重置表单
  taskForm.value = {
    cycleType: 'daily',
    weekDays: [],
    startDate: '',
    endDate: '',
    taskType: 'practice'
  };
  
  taskDialogVisible.value = true;
};

// 创建任务
const createTasks = async () => {
  if (!taskFormRef.value) return;
  
  try {
    const valid = await taskFormRef.value.validate();
    if (!valid) return;
    
    creating.value = true;
    
    // 为每个选中的资源创建任务
    const promises = selectedResources.value.map(async (resource) => {
      const taskData = {
        resource_id: resource.id,
        task_type: taskForm.value.taskType,
        task_status: 'pending',
        cycle_type: taskForm.value.cycleType,
        week_days: taskForm.value.cycleType === 'weekly' ? taskForm.value.weekDays.join(',') : '',
        task_plan_date: toLocalIsoTime(taskForm.value.startDate),
        task_finish_date: toLocalIsoTime(taskForm.value.endDate)
      };
      
      return await apiService.createTask(taskData);
    });
    
    await Promise.all(promises);
    
    ElMessage.success(`成功创建 ${selectedResources.value.length} 个任务`);
    taskDialogVisible.value = false;
    selectedResources.value = [];
    
    // 跳转到任务页面
    router.push({ name: 'Task' });
    
  } catch (error) {
    console.error('创建任务失败:', error);
    ElMessage.error('创建任务失败，请重试');
  } finally {
    creating.value = false;
  }
};
const jumpToUpload = () => {
  router.push({ name: 'UploadResource' });
};

// 处理资源卡片点击事件
const handleResourceClick = (resource: ResourceFile) => {
  router.push({ name: 'ResourceItem', params: { id: resource.id } });
};

onMounted(async () => {
  try {
    const res = await apiService.getResourceList();
    //console.log(res);
    resourceList.value = res.data;
  } catch (e) {
    ElMessage.error('获取资源列表失败');
  }
});
</script>

<style scoped>
.resource-library-card {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.resource-library-card h2 {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-bar .el-input {
  flex: 1;
}

/* 资源列表样式 */
.resource-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  cursor: pointer;
}

.resource-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.resource-content {
  padding: 0;
}

.resource-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.resource-checkbox {
  margin-top: 4px;
  flex-shrink: 0;
}

.resource-info {
  flex: 1;
  min-width: 0;
}

.resource-filename {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
  word-break: break-all;
  line-height: 1.4;
}

.resource-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.resource-user {
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.resource-time {
  text-align: right;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f2f5;
}

.resource-time span {
  font-size: 12px;
  color: #909399;
}

.el-button {
  margin: 2px;
}

/* 任务对话框样式 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.el-radio {
  margin-right: 0;
  margin-bottom: 8px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .el-dialog {
    margin: 5vh auto !important;
  }
  
  .el-radio-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .el-checkbox-group {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .dialog-footer .el-button {
    width: 48%;
  }
  .resource-library-card {
    margin: 10px;
    padding: 15px;
  }
  
  .resource-library-card h2 {
    font-size: 26px;
    margin-bottom: 25px;
  }
  
  .search-bar {
    flex-direction: column;
    gap: 15px;
    margin-bottom: 25px;
  }
  
  .search-bar .el-input {
    width: 100%;
  }
  
  .search-bar .el-input__inner {
    height: 48px;
    font-size: 16px;
    padding: 0 15px;
  }
  
  .search-bar .el-button {
    width: 100%;
    height: 48px;
    font-size: 16px;
    border-radius: 8px;
  }
  
  .resource-list {
    margin-top: 25px;
    gap: 16px;
  }
  
  .resource-item {
    border-radius: 16px;
  }
  
  .resource-content {
    padding: 4px;
  }
  
  .resource-header {
    gap: 16px;
  }
  
  .resource-filename {
    font-size: 18px;
    margin-bottom: 12px;
  }
  
  .resource-meta {
    gap: 16px;
  }
  
  .resource-user {
    font-size: 15px;
    padding: 4px 12px;
    border-radius: 6px;
  }
  
  .resource-time span {
    font-size: 14px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .resource-library-card {
    margin: 5px;
    padding: 12px;
  }
  
  .resource-library-card h2 {
    font-size: 24px;
  }
  
  .search-bar {
    gap: 12px;
  }
  
  .resource-list {
    gap: 12px;
  }
  
  .resource-item {
    border-radius: 12px;
  }
  
  .resource-filename {
    font-size: 16px;
    margin-bottom: 10px;
  }
  
  .resource-meta {
    gap: 12px;
  }
  
  .resource-user {
    font-size: 14px;
    padding: 3px 10px;
  }
  
  .resource-time span {
    font-size: 13px;
  }
}
</style>