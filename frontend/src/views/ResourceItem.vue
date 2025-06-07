<template>
  <div class="resource-item-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <button @click="goBack" class="back-btn">
        <el-icon class="back-icon">
          <ArrowLeft />
        </el-icon>
        <span>返回</span>
      </button>
      <h1 class="page-title">资源详情</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 资源内容 -->
    <div v-else-if="resource" class="main-content">
      <!-- 基本信息区域 -->
      <div class="info-section">
        <div class="section-header info-row">
          <h2 class="section-title">基本信息</h2>
        </div>
        <div class="info-grid">
          <div class="info-row">
            <div class="info-label">文件名</div>
            <div class="info-value ">{{ resource.filename }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">文件类型</div>
            <div class="info-value">
              <span class="file-type-tag" :class="getFileTypeClass(resource.file_type)">
                {{ resource.file_type.toUpperCase() }}
              </span>
            </div>
          </div>
          <div class="info-row">
            <div class="info-label">上传者</div>
            <div class="info-value">{{ resource.user_username }}</div>
          </div>
          <div class="info-row">
            <div class="info-label">上传时间</div>
            <div class="info-value">{{ formatTime(resource.upload_time) }}</div>
          </div>
        </div>
      </div>

      <!-- 文本内容区域 -->
      <div class="content-section">
        <div class="section-header">
          <h2 class="section-title">文本内容</h2>
        </div>

        <!-- 内容显示 -->
        <div v-if="!isEditing" class="content-display">
          <div v-if="resource.text_content" class="text-content">
            {{ resource.text_content }}
          </div>
          <div v-else class="empty-content">
            <div class="empty-icon">📄</div>
            <div class="empty-text">暂无文本内容</div>
            <div class="empty-hint">点击编辑按钮添加内容</div>
          </div>
        </div>

        <!-- 编辑模式 -->
        <div v-else class="content-edit">
          <div class="textarea-container">
            <textarea v-model="editContent" class="content-textarea" placeholder="请输入文本内容..."
              :maxlength="10000"></textarea>
            <div class="char-count">
              {{ editContent.length }}/10000
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <button v-if="!isEditing" @click="startEdit" class="edit-btn">
            <el-icon>
              <Edit />
            </el-icon>
            <span>编辑</span>
          </button>
          <div v-else class="edit-actions">
            <button @click="cancelEdit" class="cancel-btn">
              取消
            </button>
            <button @click="saveContent" class="save-btn" :disabled="saving">
              <el-icon v-if="saving" class="loading">
                <Loading />
              </el-icon>
              <el-icon v-else>
                <Check />
              </el-icon>
              <span>{{ saving ? '保存中...' : '保存' }}</span>
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-container">
      <div class="error-content">
        <div class="error-icon">⚠️</div>
        <h3 class="error-title">加载失败</h3>
        <p class="error-message">无法加载资源信息，请检查网络连接</p>
        <button @click="loadResource" class="retry-btn">
          重试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ArrowLeft, Edit, Check, Loading } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import apiService from '../services/apiService';

interface Resource {
  id: number;
  filename: string;
  file_type: string;
  user_username: string;
  upload_time: string;
  text_content?: string;
}

const route = useRoute();
const router = useRouter();
const resource = ref<Resource | null>(null);
const loading = ref(true);
const isEditing = ref(false);
const editContent = ref('');
const saving = ref(false);

const resourceId = route.params.id as string;

// 加载资源信息
const loadResource = async () => {
  try {
    loading.value = true;
    const response = await apiService.getResourceById(resourceId);
    resource.value = response.data;
  } catch (error) {
    console.error('加载资源失败:', error);
    ElMessage.error('加载资源信息失败');
  } finally {
    loading.value = false;
  }
};

// 开始编辑
const startEdit = () => {
  isEditing.value = true;
  editContent.value = resource.value?.text_content || '';
};

// 取消编辑
const cancelEdit = () => {
  isEditing.value = false;
  editContent.value = '';
};

// 保存内容
const saveContent = async () => {
  try {
    saving.value = true;
    await apiService.updateResource(resourceId, {
      text_content: editContent.value
    });
    
    // 更新本地数据
    if (resource.value) {
      resource.value.text_content = editContent.value;
    }
    
    isEditing.value = false;
    ElMessage.success('保存成功');
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败，请重试');
  } finally {
    saving.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 获取文件类型对应的CSS类
const getFileTypeClass = (fileType: string) => {
  return fileType.toLowerCase();
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

onMounted(() => {
  loadResource();
});
</script>

<style scoped>
.resource-item-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 20px;
}

/* 顶部导航栏 */
.top-nav {
  background: #fff;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #e4e7ed;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #ecf5ff;
  color: #337ecc;
}

.back-icon {
  font-size: 16px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  flex: 1;
}

/* 加载状态 */
.loading-container {
  padding: 20px 16px;
}

/* 主要内容区域 */
.main-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 区域样式 */
.info-section,
.content-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #e4e7ed;
}

.section-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  display: flex;
  padding: 0px 20px;
  align-items: center;
  font-size: 24px;
  color: #409eff;
  margin-bottom: 0px;
}

/* 基本信息网格 */
.info-grid {
  padding: 16px 20px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f2f5;
}

.info-row:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: #606266;
  min-width: 70px;
  font-size: 13px;
  margin-right: 12px;
}

.info-value {
  flex: 1;
  color: #303133;
  font-size: 13px;
}

.filename {
  font-family: 'Monaco', 'Menlo', monospace;
  background: #f8f9fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 13px;
}

.file-type-tag {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.file-type-tag.mp3 {
  background: #e8f5e8;
  color: #52c41a;
}

.file-type-tag.wav {
  background: #e6f7ff;
  color: #1890ff;
}

.file-type-tag.txt {
  background: #fff7e6;
  color: #fa8c16;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.edit-btn {
  width: 90%;
  background: #409eff;
  color: #fff;
  border: none;
  margin-bottom: 10px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.edit-btn:hover {
  background: #337ecc;
  transform: translateY(-1px);
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.cancel-btn {
  background: #f5f5f5;
  color: #606266;
  border: 1px solid #dcdfe6;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.save-btn {
  background: #67c23a;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  margin-bottom: 10px;
}

.save-btn:hover:not(:disabled) {
  background: #5daf34;
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 内容显示 */
.content-display {
  padding: 20px;
  min-height: 200px;
}

.text-content {
  line-height: 1.6;
  color: #303133;
  white-space: pre-wrap;
  word-break: break-word;
  background: #f8f9fa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
  font-size: 14px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #909399;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-hint {
  font-size: 14px;
  color: #c0c4cc;
}

/* 编辑模式 */
.content-edit {
  padding: 20px;
}

.textarea-container {
  position: relative;
}

.content-textarea {
  width: 90%;
  min-height: 300px;
  padding: 16px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  resize: vertical;
  outline: none;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.content-textarea:focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.char-count {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 12px;
  color: #909399;
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 4px;
}

/* 错误状态 */
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.error-content {
  text-align: center;
  background: #fff;
  padding: 40px 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.error-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.error-message {
  font-size: 14px;
  color: #606266;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.retry-btn {
  background: #409eff;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #337ecc;
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 12px;
    gap: 12px;
  }
  
  .section-header {
    padding: 12px 16px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: center;
  }
  
  .info-grid {
    padding: 16px;
  }
  
  .info-row {
    gap: 6px;
    padding: 10px 0;
  }
  
  .info-label {
    min-width: auto;
    font-size: 13px;
  }
  
  .info-value {
    font-size: 13px;
  }
  
  .content-display,
  .content-edit {
    padding: 16px;
  }
  
  .text-content {
    padding: 16px;
    font-size: 13px;
  }
  
  .content-textarea {
    min-height: 250px;
    padding: 12px;
    font-size: 13px;
  }
  
  .edit-actions {
    flex-direction: column;
    width: 90%;
  }
  
  .cancel-btn,
  .save-btn {
    width: 98%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .top-nav {
    padding: 10px 12px;
  }
  
  .page-title {
    font-size: 16px;
  }
  
  .section-title {
    font-size: 14px;
  }
  
  .error-content {
    padding: 30px 20px;
  }
  
  .error-icon {
    font-size: 48px;
  }
  
  .error-title {
    font-size: 18px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.info-section,
.content-section {
  animation: fadeIn 0.5s ease-out;
}

.loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>