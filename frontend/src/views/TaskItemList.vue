<template>
  <div class="task-item-list-container">
    <h2>任务项列表</h2>

    <!-- 任务信息 -->
    <div v-if="taskInfo" class="task-info">
      <p>{{ taskInfo.resource_filename }} - {{ getCycleText(taskInfo.cycle_type, taskInfo.week_days?.split(',')) }}</p>
    </div>

    <!-- 任务项列表 -->
    <div class="task-item-list" v-loading="loading && currentPage === 1">
      <div v-if="taskItems.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无任务项" />
      </div>

      <el-card v-for="item,index in taskItems" :key="item.id" class="task-item-card" shadow="hover">
        <div class="task-item-content">
          <div class="task-item-header">
            <div class="item-info">
              <span class="item-id">#{{ index + 1 }}</span>
              <span class="resource-name">{{ item.resource_filename || '未指定资源' }}</span>
            </div>
            <div class="item-actions">
              <!-- <el-button type="primary" size="small" :icon="View" @click="viewDetail(item)" circle />
              <el-button type="warning" size="small" :icon="Edit" @click="editItem(item)" circle /> -->
              <el-button type="danger" size="small" :icon="Delete" @click="confirmDelete(item)" circle />
            </div>
          </div>

          <div class="task-item-details">
            <div class="time-info">
              <div class="time-item" v-if="item.plan_time">
                <span class="label">计划时间:</span>
                <span class="value">{{ formatDateTime(item.plan_time) }}</span>
              </div>
              <div class="time-item" v-if="item.begin_time">
                <span class="label">开始时间:</span>
                <span class="value">{{ formatDateTime(item.begin_time) }}</span>
              </div>
              <div class="time-item" v-if="item.end_time">
                <span class="label">结束时间:</span>
                <span class="value">{{ formatDateTime(item.end_time) }}</span>
              </div>
              <div class="time-item" v-if="item.score !== null && item.score !== undefined">
                <span class="label">得分:</span>
                <span class="value score">{{ item.score }}</span>
              </div>
            </div>

            <div class="duration" v-if="item.begin_time && item.end_time">
              <span class="label">用时:</span>
              <span class="value">{{ calculateDuration(item.begin_time, item.end_time) }}</span>
            </div>

            <!-- 跟读按钮 -->
            <div class="practice-action" v-if="item.score === null || item.score === undefined">
              <el-button type="primary" @click="goToPractice(item)" class="practice-btn">
                跟读
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 加载更多指示器 -->
    <div v-if="loading && currentPage > 1" class="loading-more">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>加载中...</span>
    </div>

    <!-- 没有更多数据提示 -->
    <div v-if="!hasMore && taskItems.length > 0" class="no-more">
      <span>没有更多数据了</span>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" :icon="ArrowLeft" @click="goBack">返回</el-button>
      <el-button type="primary" :icon="Plus" @click="showCreateDialog">新建任务项</el-button>
    </div>

    <!-- 创建/编辑任务项对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingItem ? '编辑任务项' : '新建任务项'" width="90%" :max-width="500">
      <el-form :model="itemForm" :rules="itemRules" ref="itemFormRef" label-width="100px">
        <el-form-item label="资源" prop="resource_id">
          <el-select v-model="itemForm.resource_id" placeholder="选择资源" style="width: 100%">
            <el-option label="未指定" :value="null" />
            <!-- 这里可以添加资源选项 -->
          </el-select>
        </el-form-item>

        <el-form-item label="开始时间" prop="begin_time">
          <el-date-picker v-model="itemForm.begin_time" type="datetime" placeholder="选择开始时间" style="width: 100%" />
        </el-form-item>

        <el-form-item label="结束时间" prop="end_time">
          <el-date-picker v-model="itemForm.end_time" type="datetime" placeholder="选择结束时间" style="width: 100%" />
        </el-form-item>

        <el-form-item label="得分" prop="score">
          <el-input-number v-model="itemForm.score" :min="0" :max="100" :precision="1" placeholder="输入得分"
            style="width: 100%" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveItem" :loading="saving">
          {{ editingItem ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, View, Edit, Delete, Loading } from '@element-plus/icons-vue'
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

interface TaskInfo {
  id: number
  task_id: string
  resource_filename?: string
  cycle_type: string
  week_days?: string
}

const route = useRoute()
const router = useRouter()

const taskId = ref<string>(route.params.taskId as string)
const taskItems = ref<TaskItem[]>([])
const taskInfo = ref<TaskInfo | null>(null)
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const hasMore = ref(true)
const isScrollLoading = ref(false)

// 对话框相关
const dialogVisible = ref(false)
const editingItem = ref<TaskItem | null>(null)
const saving = ref(false)
const itemFormRef = ref()
const itemForm = ref({
  resource_id: null as number | null,
  begin_time: null as Date | null,
  end_time: null as Date | null,
  score: null as number | null
})

const itemRules = {
  // 可以根据需要添加验证规则
}

// 加载任务项列表
const loadTaskItems = async (append = false) => {
  if (append) {
    isScrollLoading.value = true
  } else {
    loading.value = true
  }
  
  try {
    const response = await apiService.getTaskItemsByTask(taskId.value, {
      page: currentPage.value,
      per_page: pageSize.value
    })
    
    const newItems = response.data.task_items || []
    
    if (append) {
      taskItems.value = [...taskItems.value, ...newItems]
    } else {
      taskItems.value = newItems
    }
    
    total.value = response.data.total || 0
    taskInfo.value = response.data.task || null
    
    // 检查是否还有更多数据
    hasMore.value = taskItems.value.length < total.value
    
  } catch (error) {
    console.error('加载任务项失败:', error)
    ElMessage.error('加载任务项失败')
  } finally {
    loading.value = false
    isScrollLoading.value = false
  }
}

// 获取周期文本
const getCycleText = (cycleType: string, weekDays?: string[]) => {
  if (cycleType === 'daily') {
    return '每天'
  } else if (cycleType === 'weekly' && weekDays && weekDays.length > 0) {
    const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const selectedDays = weekDays.map(day => dayNames[parseInt(day)]).join('、')
    return `每周${selectedDays}`
  }
  return cycleType || '未设置'
}

// 格式化日期时间
const formatDateTime = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  date.setHours(date.getHours() - 8)
  return date.toLocaleString('zh-CN')
}

// 计算持续时间
const calculateDuration = (beginTime: string, endTime: string) => {
  const begin = new Date(beginTime)
  const end = new Date(endTime)
  const diff = end.getTime() - begin.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)
  return `${minutes}分${seconds}秒`
}

// 跳转到跟读页面
const goToPractice = (item: TaskItem) => {
  if (item.resource_id) {
    router.push({ name: 'Practice', params: { id: item.resource_id } })
  } else {
    ElMessage.warning('该任务项未指定资源，无法进行跟读练习')
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 无限滚动处理
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const windowHeight = window.innerHeight
  const documentHeight = document.documentElement.scrollHeight
  
  // 当滚动到距离底部100px时加载更多
  if (scrollTop + windowHeight >= documentHeight - 100) {
    loadMore()
  }
}

// 加载更多数据
const loadMore = async () => {
  if (loading.value || isScrollLoading.value || !hasMore.value) {
    return
  }
  
  currentPage.value++
  await loadTaskItems(true)
}

// 显示创建对话框
const showCreateDialog = () => {
  editingItem.value = null
  itemForm.value = {
    resource_id: null,
    begin_time: null,
    end_time: null,
    score: null
  }
  dialogVisible.value = true
}

// 编辑任务项
const editItem = (item: TaskItem) => {
  editingItem.value = item
  itemForm.value = {
    resource_id: item.resource_id || null,
    begin_time: item.begin_time ? new Date(item.begin_time) : null,
    end_time: item.end_time ? new Date(item.end_time) : null,
    score: item.score || null
  }
  dialogVisible.value = true
}

// 查看详情
const viewDetail = (item: TaskItem) => {
  router.push({ name: 'TaskItemDetail', params: { id: item.id } })
}

// 保存任务项
const saveItem = async () => {
  if (!itemFormRef.value) return
  
  try {
    const valid = await itemFormRef.value.validate()
    if (!valid) return
  } catch {
    return
  }
  
  saving.value = true
  try {
    const data = {
      task_id: taskId.value,
      resource_id: itemForm.value.resource_id,
      begin_time: itemForm.value.begin_time?.toISOString(),
      end_time: itemForm.value.end_time?.toISOString(),
      score: itemForm.value.score
    }
    
    if (editingItem.value) {
      await apiService.updateTaskItem(editingItem.value.id, data)
      ElMessage.success('任务项更新成功')
    } else {
      await apiService.createTaskItem(data)
      ElMessage.success('任务项创建成功')
    }
    
    dialogVisible.value = false
    await loadTaskItems()
  } catch (error) {
    console.error('保存任务项失败:', error)
    ElMessage.error('保存任务项失败')
  } finally {
    saving.value = false
  }
}

// 确认删除
const confirmDelete = async (item: TaskItem) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除任务项 #${item.id} 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteItem(item.id)
  } catch {
    // 用户取消删除
  }
}

// 删除任务项
const deleteItem = async (itemId: number) => {
  try {
    await apiService.deleteTaskItem(itemId)
    ElMessage.success('任务项删除成功')
    await loadTaskItems()
  } catch (error) {
    console.error('删除任务项失败:', error)
    ElMessage.error('删除任务项失败')
  }
}

onMounted(() => {
  loadTaskItems()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.task-item-list-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.task-item-list-container h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 24px;
  font-weight: 600;
}

.task-info {
  background: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
}

.task-info p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.task-item-list {
  display: grid;
  gap: 16px;
  margin-bottom: 24px;
}

.task-item-card {
  margin-bottom: 16px;
  transition: all 0.3s ease;
}

.task-item-card:hover {
  transform: translateY(-2px);
}

.task-item-content {
  padding: 0;
}

.task-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-id {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.resource-name {
  font-weight: 500;
  color: #2c3e50;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.task-item-details {
  display: grid;
  gap: 12px;
}

.time-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.time-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.time-item .label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.time-item .value {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.time-item .value.score {
  color: #e74c3c;
  font-weight: 600;
}

.duration {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #409eff;
  color: white;
  border-radius: 8px;
  font-weight: 500;
}

.practice-action {
  margin-top: 12px;
  text-align: center;
}

.practice-btn {
  background: #67c23a;
  border-color: #67c23a;
  color: white;
  font-weight: 500;
  padding: 8px 24px;
}

.practice-btn:hover {
  background: #5daf34;
  border-color: #5daf34;
}

.empty-state {
  text-align: center;
  padding: 40px;
}

.loading-more {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 20px;
  color: #666;
  font-size: 14px;
}

.no-more {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}

.action-buttons {
  margin-top: 24px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .task-item-list-container {
    padding: 12px;
  }
  
  .task-item-list-container h2 {
    font-size: 20px;
    text-align: center;
  }
  
  .task-info {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  .time-info {
    grid-template-columns: 1fr;
  }
  
  .item-actions {
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .practice-btn {
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>