<template>
  <div class="task-item-detail-container">
    <!-- 页面头部 -->
    <div class="header">
      <div class="header-content">
        <div class="title-section">
          <el-button 
            type="primary" 
            :icon="ArrowLeft" 
            @click="goBack" 
            circle
            class="back-btn"
          />
          <div class="title-info">
            <h1>任务项详情</h1>
            <p v-if="taskItem">#{{ taskItem.id }} - {{ taskItem.resource_filename || '未指定资源' }}</p>
          </div>
        </div>
        <div class="actions">
          <el-button type="warning" :icon="Edit" @click="showEditDialog">编辑</el-button>
          <el-button type="danger" :icon="Delete" @click="confirmDelete">删除</el-button>
        </div>
      </div>
    </div>

    <!-- 任务项详情内容 -->
    <div class="content" v-loading="loading">
      <div v-if="taskItem" class="detail-content">
        <!-- 基本信息卡片 -->
        <div class="info-card">
          <div class="card-header">
            <h3>基本信息</h3>
            <div class="status-badge">
              <span class="badge" :class="getStatusClass()">{{ getStatusText() }}</span>
            </div>
          </div>
          <div class="card-content">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">任务项ID</span>
                <span class="value">#{{ taskItem.id }}</span>
              </div>
              <div class="info-item">
                <span class="label">主任务ID</span>
                <span class="value">#{{ taskItem.task_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">用户ID</span>
                <span class="value">{{ taskItem.user_id }}</span>
              </div>
              <div class="info-item">
                <span class="label">资源</span>
                <span class="value">{{ taskItem.resource_filename || '未指定资源' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 时间信息卡片 -->
        <div class="info-card">
          <div class="card-header">
            <h3>时间信息</h3>
          </div>
          <div class="card-content">
            <div class="time-grid">
              <div class="time-item">
                <div class="time-label">开始时间</div>
                <div class="time-value">
                  {{ taskItem.begin_time ? formatDateTime(taskItem.begin_time) : '未设置' }}
                </div>
              </div>
              <div class="time-item">
                <div class="time-label">结束时间</div>
                <div class="time-value">
                  {{ taskItem.end_time ? formatDateTime(taskItem.end_time) : '未设置' }}
                </div>
              </div>
              <div class="time-item" v-if="taskItem.begin_time && taskItem.end_time">
                <div class="time-label">用时</div>
                <div class="time-value duration">
                  {{ calculateDuration(taskItem.begin_time, taskItem.end_time) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 得分信息卡片 -->
        <div class="info-card" v-if="taskItem.score !== null && taskItem.score !== undefined">
          <div class="card-header">
            <h3>得分信息</h3>
          </div>
          <div class="card-content">
            <div class="score-display">
              <div class="score-circle">
                <div class="score-number">{{ taskItem.score }}</div>
                <div class="score-label">分</div>
              </div>
              <div class="score-info">
                <div class="score-level">{{ getScoreLevel(taskItem.score) }}</div>
                <div class="score-description">{{ getScoreDescription(taskItem.score) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 创建和更新时间 -->
        <div class="info-card">
          <div class="card-header">
            <h3>记录信息</h3>
          </div>
          <div class="card-content">
            <div class="record-info">
              <div class="record-item">
                <span class="label">创建时间</span>
                <span class="value">{{ formatDateTime(taskItem.create_date) }}</span>
              </div>
              <div class="record-item">
                <span class="label">更新时间</span>
                <span class="value">{{ formatDateTime(taskItem.update_date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <el-empty description="任务项不存在" />
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      title="编辑任务项" 
      width="90%" 
      :max-width="500"
    >
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="资源" prop="resource_id">
          <el-select v-model="editForm.resource_id" placeholder="选择资源" style="width: 100%">
            <el-option label="未指定" :value="null" />
            <!-- 这里可以添加资源选项 -->
          </el-select>
        </el-form-item>
        
        <el-form-item label="开始时间" prop="begin_time">
          <el-date-picker
            v-model="editForm.begin_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker
            v-model="editForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item label="得分" prop="score">
          <el-input-number
            v-model="editForm.score"
            :min="0"
            :max="100"
            :precision="1"
            placeholder="输入得分"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">
          更新
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Edit, Delete } from '@element-plus/icons-vue'
import apiService from '../services/apiService'

interface TaskItem {
  id: number
  user_id: string
  task_id: number
  resource_id?: number
  begin_time?: string
  end_time?: string
  score?: number
  create_date: string
  update_date: string
  resource_filename?: string
}

const route = useRoute()
const router = useRouter()

const taskItemId = ref<number>(parseInt(route.params.id as string))
const taskItem = ref<TaskItem | null>(null)
const loading = ref(false)

// 编辑对话框相关
const editDialogVisible = ref(false)
const saving = ref(false)
const editFormRef = ref()
const editForm = ref({
  resource_id: null as number | null,
  begin_time: null as Date | null,
  end_time: null as Date | null,
  score: null as number | null
})

const editRules = {
  // 可以根据需要添加验证规则
}

// 加载任务项详情
const loadTaskItem = async () => {
  loading.value = true
  try {
    const response = await apiService.getTaskItemById(taskItemId.value)
    taskItem.value = response.data
  } catch (error) {
    console.error('加载任务项详情失败:', error)
    ElMessage.error('加载任务项详情失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 计算持续时间
const calculateDuration = (beginTime: string, endTime: string) => {
  const begin = new Date(beginTime)
  const end = new Date(endTime)
  const diff = end.getTime() - begin.getTime()
  
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分${seconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分${seconds}秒`
  } else {
    return `${seconds}秒`
  }
}

// 获取状态样式类
const getStatusClass = () => {
  if (!taskItem.value) return 'status-unknown'
  
  if (taskItem.value.begin_time && taskItem.value.end_time) {
    return 'status-completed'
  } else if (taskItem.value.begin_time) {
    return 'status-in-progress'
  } else {
    return 'status-pending'
  }
}

// 获取状态文本
const getStatusText = () => {
  if (!taskItem.value) return '未知'
  
  if (taskItem.value.begin_time && taskItem.value.end_time) {
    return '已完成'
  } else if (taskItem.value.begin_time) {
    return '进行中'
  } else {
    return '待开始'
  }
}

// 获取得分等级
const getScoreLevel = (score: number) => {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 70) return '中等'
  if (score >= 60) return '及格'
  return '不及格'
}

// 获取得分描述
const getScoreDescription = (score: number) => {
  if (score >= 90) return '表现出色，继续保持！'
  if (score >= 80) return '表现良好，再接再厉！'
  if (score >= 70) return '表现中等，还有提升空间'
  if (score >= 60) return '刚好及格，需要加强练习'
  return '需要更多练习和努力'
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 显示编辑对话框
const showEditDialog = () => {
  if (!taskItem.value) return
  
  editForm.value = {
    resource_id: taskItem.value.resource_id || null,
    begin_time: taskItem.value.begin_time ? new Date(taskItem.value.begin_time) : null,
    end_time: taskItem.value.end_time ? new Date(taskItem.value.end_time) : null,
    score: taskItem.value.score || null
  }
  editDialogVisible.value = true
}

// 保存编辑
const saveEdit = async () => {
  if (!editFormRef.value || !taskItem.value) return
  
  try {
    const valid = await editFormRef.value.validate()
    if (!valid) return
  } catch {
    return
  }
  
  saving.value = true
  try {
    const data = {
      task_id: taskItem.value.task_id,
      resource_id: editForm.value.resource_id,
      begin_time: editForm.value.begin_time?.toISOString(),
      end_time: editForm.value.end_time?.toISOString(),
      score: editForm.value.score
    }
    
    await apiService.updateTaskItem(taskItem.value.id, data)
    ElMessage.success('任务项更新成功')
    editDialogVisible.value = false
    await loadTaskItem()
  } catch (error) {
    console.error('更新任务项失败:', error)
    ElMessage.error('更新任务项失败')
  } finally {
    saving.value = false
  }
}

// 确认删除
const confirmDelete = async () => {
  if (!taskItem.value) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除任务项 #${taskItem.value.id} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteTaskItem()
  } catch {
    // 用户取消删除
  }
}

// 删除任务项
const deleteTaskItem = async () => {
  if (!taskItem.value) return
  
  try {
    await apiService.deleteTaskItem(taskItem.value.id)
    ElMessage.success('任务项删除成功')
    router.back()
  } catch (error) {
    console.error('删除任务项失败:', error)
    ElMessage.error('删除任务项失败')
  }
}

onMounted(() => {
  loadTaskItem()
})
</script>

<style scoped>
.task-item-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.title-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.title-info p {
  margin: 4px 0 0 0;
  color: #7f8c8d;
  font-size: 14px;
}

.actions {
  display: flex;
  gap: 12px;
}

.content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.detail-content {
  display: grid;
  gap: 24px;
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #e1e8ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.status-badge .badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.status-completed {
  background: #d4edda;
  color: #155724;
}

.status-in-progress {
  background: #fff3cd;
  color: #856404;
}

.status-pending {
  background: #f8d7da;
  color: #721c24;
}

.status-unknown {
  background: #e2e3e5;
  color: #383d41;
}

.card-content {
  display: grid;
  gap: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item .label {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.info-item .value {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 600;
}

.time-grid {
  display: grid;
  gap: 16px;
}

.time-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  border-left: 4px solid #667eea;
}

.time-label {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.time-value {
  font-size: 16px;
  color: #2c3e50;
  font-weight: 600;
}

.time-value.duration {
  color: #667eea;
  font-weight: 700;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 32px;
}

.score-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.score-number {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  font-weight: 500;
  margin-top: 4px;
}

.score-info {
  flex: 1;
}

.score-level {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.score-description {
  font-size: 16px;
  color: #7f8c8d;
  line-height: 1.5;
}

.record-info {
  display: grid;
  gap: 12px;
}

.record-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.record-item .label {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
}

.record-item .value {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .task-item-detail-container {
    padding: 12px;
  }
  
  .header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .title-section {
    justify-content: center;
  }
  
  .actions {
    justify-content: center;
  }
  
  .content {
    padding: 16px;
  }
  
  .info-card {
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .score-display {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .score-circle {
    width: 100px;
    height: 100px;
  }
  
  .score-number {
    font-size: 28px;
  }
  
  .score-level {
    font-size: 20px;
  }
}
</style>