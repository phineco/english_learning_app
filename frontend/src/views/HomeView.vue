<template>
  <h2>欢迎使用英语跟读评分应用</h2>
  <p>在这里，您可以练习英语单词发音，并获得即时评分反馈。</p>
  <el-divider></el-divider>
  
  <!-- 未完成的跟读任务 -->
  <div class="uncompleted-tasks" v-if="uncompletedTasks.length > 0">
    <h3><el-icon><clock /></el-icon> 待完成的跟读任务</h3>
    <div class="task-list">
      <el-card 
        v-for="task in uncompletedTasks" 
        :key="task.id" 
        class="task-item" 
        shadow="hover"
      >
        <div class="task-content">
          <div class="task-info">
            <h4>{{ task.resource_name || '未知资源' }}</h4>
            <p class="task-time">计划时间: {{ formatDateTime(task.plan_time) }}</p>
            <p class="task-duration" v-if="task.begin_time && task.end_time">
              时长: {{ calculateDuration(task.begin_time, task.end_time) }}
            </p>
          </div>
          <div class="task-actions">
            <el-button 
              type="primary" 
              size="small" 
              @click="goToPractice(task)"
            >
              开始跟读
            </el-button>
          </div>
        </div>
      </el-card>
    </div>
    <el-divider></el-divider>
  </div>
  <div class="features">
    <el-row :gutter="20">
      <!-- <el-col :span="8">
        <el-card shadow="hover">
          <h3><el-icon>
              <notebook />
            </el-icon> 单词跟读</h3>
          <p>浏览和学习精心挑选的单词列表。</p>
          <el-button type="primary" @click="goTo('/words')">查看单词</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <h3><el-icon>
              <microphone />
            </el-icon> 句子跟读</h3>
          <p>选择句子进行跟读，系统将对您的发音进行评分。</p>
          <el-button type="success" @click="goTo('/practice')">开始练习</el-button>
        </el-card>
      </el-col> -->
      <el-col :span="8">
        <el-card shadow="hover">
          <h3><el-icon>
              <camera />
            </el-icon> 拍照听写</h3>
          <p>拍照识别文字自动生成音频</p>
          <el-button type="primary" @click="goTo('/take-photo')">拍照</el-button>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <h3><el-icon>
              <upload />
            </el-icon> 上传资源</h3>
          <p>上传txt或mp3文件，自动生成音频或识别文本。</p>
          <el-button type="warning" @click="goTo('/upload')">上传资源</el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Notebook, Microphone, User, Clock } from '@element-plus/icons-vue';
import apiService from '@/services/apiService';
import { ElMessage } from 'element-plus';

interface TaskItem {
  id: number;
  task_id: string;
  resource_id: number;
  resource_name?: string;
  plan_time: string;
  begin_time?: string;
  end_time?: string;
  score?: number;
}

export default defineComponent({
  name: 'HomeView',
  components: {
    Notebook,
    Microphone,
    User,
    Clock
  },
  setup() {
    const router = useRouter();
    const uncompletedTasks = ref<TaskItem[]>([]);
    
    const goTo = (path: string) => {
      router.push(path);
    };
    
    const goToPractice = (task: TaskItem) => {
      router.push({ name: 'Practice', params: { resId: task.resource_id, taskId: task.task_id, taskItemId: task.id } });
      //router.push(`/practice/${resourceId}`);
    };
    
    const formatDateTime = (dateTime: string) => {
      if (!dateTime) return '';
      const date = new Date(dateTime);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    const calculateDuration = (beginTime: string, endTime: string) => {
      if (!beginTime || !endTime) return '';
      const begin = new Date(beginTime);
      const end = new Date(endTime);
      const duration = Math.abs(end.getTime() - begin.getTime());
      const minutes = Math.floor(duration / (1000 * 60));
      const seconds = Math.floor((duration % (1000 * 60)) / 1000);
      return `${minutes}分${seconds}秒`;
    };
    
    const loadUncompletedTasks = async () => {
      try {
        const response = await apiService.getUncompletedTaskItems();
        uncompletedTasks.value = response.data.task_items;
      } catch (error) {
        console.error('获取未完成任务失败:', error);
        ElMessage.error('获取未完成任务失败');
      }
    };
    
    onMounted(() => {
      loadUncompletedTasks();
    });
    
    return {
      goTo,
      goToPractice,
      uncompletedTasks,
      formatDateTime,
      calculateDuration
    };
  },
});
</script>

<style scoped>
.home-card {
  margin: 20px;
  text-align: center;
}
.features h3 {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.features .el-icon {
  margin-right: 8px;
  font-size: 20px;
}
.features p {
  font-size: 14px;
  color: #606266;
  margin-bottom: 15px;
  min-height: 40px;
  line-height: 1.5;
}
.features .el-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

/* 未完成任务样式 */
.uncompleted-tasks {
  margin-bottom: 30px;
}

.uncompleted-tasks h3 {
  display: flex;
  align-items: center;
  font-size: 20px;
  color: #409eff;
  margin-bottom: 20px;
}

.uncompleted-tasks .el-icon {
  margin-right: 8px;
  font-size: 22px;
}

.task-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.task-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.task-item:hover {
  border-color: #409eff;
  transform: translateY(-2px);
}

.task-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.task-info {
  flex: 1;
}

.task-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.task-time, .task-duration {
  margin: 4px 0;
  font-size: 14px;
  color: #909399;
}

.task-actions {
  margin-left: 16px;
}

.task-actions .el-button {
  padding: 8px 16px;
  font-size: 14px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .home-card {
    margin: 10px;
    padding: 15px;
  }
  
  .home-card h2 {
    font-size: 24px;
    margin-bottom: 15px;
  }
  
  .home-card p {
    font-size: 16px;
    margin-bottom: 20px;
  }
  
  /* 未完成任务移动端样式 */
  .uncompleted-tasks h3 {
    font-size: 18px;
    margin-bottom: 16px;
  }
  
  .task-list {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .task-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .task-actions {
    margin-left: 0;
    margin-top: 12px;
    width: 100%;
  }
  
  .task-actions .el-button {
    width: 100%;
    height: 40px;
  }
  
  .features .el-row {
    flex-direction: column !important;
    display: flex !important;
  }
  
  .features .el-col {
    max-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 16px;
  }
  
  .features .el-card {
    padding: 20px 15px;
  }
  
  .features h3 {
    font-size: 20px;
    margin-bottom: 12px;
  }
  
  .features .el-icon {
    font-size: 24px;
  }
  
  .features p {
    font-size: 15px;
    min-height: auto;
    margin-bottom: 18px;
  }
  
  .features .el-button {
    height: 48px;
    font-size: 17px;
    border-radius: 8px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .home-card {
    margin: 5px;
    padding: 10px;
  }
  
  .home-card h2 {
    font-size: 22px;
  }
  
  .features .el-card {
    padding: 15px 10px;
  }
  
  .features h3 {
    font-size: 18px;
  }
  
  .features p {
    font-size: 14px;
  }
}
</style>