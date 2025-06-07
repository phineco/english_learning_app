<template>
  <div class="task-container">
    <div class="header">
      <h1>任务列表</h1>
      <div class="stats" v-if="stats">
        <span class="stat-item">待完成: {{ stats.pending || 0 }}</span>
        <span class="stat-item">已完成: {{ stats.completed || 0 }}</span>
      </div>
    </div>

    <div class="filter-section">
      <el-select v-model="filterStatus" placeholder="筛选状态" @change="loadTasks">
        <el-option label="全部" value=""></el-option>
        <el-option label="待完成" value="pending"></el-option>
        <el-option label="进行中" value="in_progress"></el-option>
        <el-option label="已完成" value="completed"></el-option>
      </el-select>
      <!-- <el-select v-model="filterType" placeholder="筛选类型" @change="loadTasks">
        <el-option label="全部" value=""></el-option>
        <el-option label="阅读" value="reading"></el-option>
        <el-option label="听力" value="listening"></el-option>
        <el-option label="口语" value="speaking"></el-option>
        <el-option label="写作" value="writing"></el-option>
      </el-select> -->
    </div>

    <div class="task-list" v-loading="loading">
      <div v-if="tasks.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无任务"></el-empty>
      </div>

      <div v-for="task in tasks" :key="task.id" class="task-item">
        <div class="task-content" @click="handleTaskClick(task)">
          <div class="task-header">
            <span class="task-id">{{ task.resource_filename }}</span>
            <!-- <el-tag :type="getStatusType(task.task_status)" size="small">
              {{ getStatusText(task.task_status) }}
            </el-tag> -->
          </div>
          <div class="cycle-type">{{ getCycleText(task.cycle_type, task.week_days.split(',')) }}</div>
          <div class="task-info">
            <!-- <div class="task-type">
              <el-icon><Document /></el-icon>
              {{ getTypeText(task.task_type) }}
            </div> -->
            <div class="task-dates">
              <div class="plan-date">
                <el-icon>
                  <Calendar />
                </el-icon>
                开始: {{ formatDate(task.task_plan_date) }}
              </div>
              <div class="plan-date">
                <el-icon>
                  <Calendar />
                </el-icon>
                结束: <p v-if="task.task_finish_date">{{ formatDate(task.task_finish_date) }}</p>
              </div>
              <div class="finish-date">
                <el-icon>
                  <Check />
                </el-icon>
                已完成: {{ task.finished_task_num }} | 任务总数：{{ task.task_num }}
              </div>
            </div>
          </div>
        </div>

        <div class="task-actions">
          <el-button type="danger" size="small" :icon="Delete" @click.stop="confirmDelete(task)" circle></el-button>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > pageSize">
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50]"
        :total="total" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, Calendar, Check, Delete } from '@element-plus/icons-vue'
import apiService from '../services/apiService'

interface Task {
  id: number
  user_id: number
  task_id: string
  resource_id: number
  task_type: string
  task_plan_date: string
  task_finish_date?: string
  task_status: string
  create_date: string
  update_date: string
}

interface TaskStats {
  pending: number
  completed: number
  in_progress: number
}

const router = useRouter()
const loading = ref(false)
const tasks = ref<Task[]>([])
const stats = ref<TaskStats | null>(null)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const filterStatus = ref('')
const filterType = ref('')

// 加载任务列表
const loadTasks = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    if (filterType.value) {
      params.type = filterType.value
    }
    
    const response = await apiService.getTasks(params)
    tasks.value = response.data.tasks || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('加载任务失败:', error)
    ElMessage.error('加载任务失败')
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStats = async () => {
  try {
    const response = await apiService.getTaskStats()
    stats.value = response.data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

// 处理任务点击
const handleTaskClick = (task: Task) => {
  // 跳转到任务项列表页面
  router.push({
    name: 'TaskItemList',
    params: { taskId: task.id }
  })
}

// 确认删除
const confirmDelete = async (task: Task) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务 "${task.resource_filename}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteTask(task.id)
  } catch (error) {
    // 用户取消删除
  }
}

// 删除任务
const deleteTask = async (taskId: number) => {
  try {
    await apiService.deleteTask(taskId)
    ElMessage.success('删除成功')
    await loadTasks()
    await loadStats()
  } catch (error) {
    console.error('删除任务失败:', error)
    ElMessage.error('删除任务失败')
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  switch (status) {
    case 'pending': return 'warning'
    case 'in_progress': return 'primary'
    case 'completed': return 'success'
    default: return 'info'
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待完成'
    case 'in_progress': return '进行中'
    case 'completed': return '已完成'
    default: return status
  }
}

// 获取类型文本
const getTypeText = (type: string) => {
  switch (type) {
    case 'reading': return '阅读'
    case 'listening': return '听力'
    case 'speaking': return '口语'
    case 'writing': return '写作'
    default: return type
  }
}

// 获取周期文本
const getCycleText = (cycleType: string, weekDays?: number[]) => {
  if (cycleType === 'daily') {
    return '每天'
  } else if (cycleType === 'weekly' && weekDays && weekDays.length > 0) {
    const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const selectedDays = weekDays.map(day => dayNames[day]).join('、')
    return `每周：${selectedDays}`
  }
  return cycleType || '未设置'
}

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadTasks()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadTasks()
}

onMounted(() => {
  loadTasks()
  loadStats()
})
</script>

<style scoped>
.task-container {
  padding: 16px;
  max-width: 100%;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  padding: 4px 12px;
  background: #f5f5f5;
  border-radius: 16px;
  font-size: 14px;
  color: #666;
}

.filter-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-section .el-select {
  width: 120px;
}

.task-list {
  min-height: 200px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.task-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.task-content {
  flex: 1;
  cursor: pointer;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.task-id {
  font-weight: 600;
  font-size: 16px;
  color: #333;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-type {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.task-dates {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.plan-date,
.finish-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
}

.cycle-type  {
  text-align: left;
  font-size: 12px;
  color: #999;
}

.finish-date {
  color: #67c23a;
}

.task-actions {
  margin-left: 12px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .task-container {
    padding: 12px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .stats {
    width: 100%;
    justify-content: space-around;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .filter-section .el-select {
    width: 100%;
  }
  
  .task-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .task-content {
    margin-bottom: 12px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .task-actions {
    margin-left: 0;
    align-self: flex-end;
  }
  
  .task-dates {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .task-container {
    padding: 8px;
  }
  
  .task-item {
    padding: 12px;
  }
  
  .header h1 {
    font-size: 18px;
  }
}
</style>