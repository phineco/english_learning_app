<template>
  <div class="take-photo-container">
    <div class="header">
      <h2>照片识别</h2>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <div class="upload-container" v-if="!selectedImage">
        <el-upload
          ref="uploadRef"
          class="upload-demo"
          :auto-upload="false"
          :show-file-list="false"
          accept="image/*"
          @change="handleFileSelect"
        >
          <template #trigger>
            <el-button type="primary" size="large">
              <el-icon><Upload /></el-icon>
              选择照片
            </el-button>
          </template>
        </el-upload>
        <div class="upload-tips">
          <p>支持 JPG、PNG、JPEG 格式</p>
          <p>建议图片大小不超过 10MB</p>
        </div>
      </div>

      <!-- 预览选择的照片 -->
      <div class="photo-preview" v-if="selectedImage">
        <img :src="selectedImage" alt="选择的照片" class="selected-image" />
        <div class="photo-controls">
          <el-button type="primary" @click="uploadPhoto" :loading="uploading">
            <el-icon><Upload /></el-icon>
            上传识别
          </el-button>
          <el-button @click="resetSelection">
            <el-icon><RefreshRight /></el-icon>
            重新选择
          </el-button>
        </div>
      </div>
    </div>

    <!-- 识别结果区域 -->
    <div class="result-section" v-if="recognitionResult">
      <el-card class="result-card">
        <template #header>
          <div class="card-header">
            <span>识别结果</span>
          </div>
        </template>

        <!-- 识别的文本 -->
        <div class="text-result" v-if="recognitionResult.text">
          <h3>识别文本</h3>
          <div class="text-content">
            {{ recognitionResult.text }}
          </div>
        </div>

        <!-- 语音播放器 -->
        <div class="audio-result" v-if="recognitionResult.audio_url">
          <h3>语音播放</h3>
          <div class="audio-controls">
            <audio ref="audioElement" :src="recognitionResult.audio_url" class="audio-player"></audio>
            <div class="audio-buttons">
              <el-button type="primary" @click="playAudio" :disabled="isPlaying">
                <el-icon><VideoPlay /></el-icon>
                听写
              </el-button>
              <el-button @click="pauseAudio" :disabled="!isPlaying">
                <el-icon><VideoPause /></el-icon>
                暂停
              </el-button>
              <el-button @click="stopAudio">
                <el-icon></el-icon>
                停止
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="loading">
      <el-loading-spinner size="large" />
      <p>{{ loadingText }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import type { UploadFile } from 'element-plus';
import { Upload, RefreshRight, VideoPlay, VideoPause } from '@element-plus/icons-vue';
import apiService from '../services/apiService';

interface RecognitionResult {
  text?: string;
  audio_url?: string;
  video_url?: string;
}

// 响应式数据
const uploadRef = ref();
const audioElement = ref<HTMLAudioElement>();
const selectedImage = ref<string>('');
const selectedFile = ref<File | null>(null);
const loading = ref(false);
const uploading = ref(false);
const loadingText = ref('正在处理...');
const recognitionResult = ref<RecognitionResult | null>(null);
const isPlaying = ref(false);

// 处理文件选择
const handleFileSelect = (file: UploadFile) => {
  if (!file.raw) return;
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('请选择 JPG、PNG 或 JPEG 格式的图片');
    return;
  }
  
  // 检查文件大小 (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.raw.size > maxSize) {
    ElMessage.error('图片大小不能超过 10MB');
    return;
  }
  
  selectedFile.value = file.raw;
  
  // 创建预览
  const reader = new FileReader();
  reader.onload = (e) => {
    selectedImage.value = e.target?.result as string;
  };
  reader.readAsDataURL(file.raw);
};

// 重置选择
const resetSelection = () => {
  selectedImage.value = '';
  selectedFile.value = null;
  recognitionResult.value = null;
  isPlaying.value = false;
  if (uploadRef.value) {
    uploadRef.value.clearFiles();
  }
  if (audioElement.value) {
    audioElement.value.pause();
    audioElement.value.currentTime = 0;
  }
};

// 上传照片
const uploadPhoto = async () => {
  if (!selectedFile.value) return;
  
  try {
    uploading.value = true;
    loading.value = true;
    loadingText.value = '正在识别文本并生成语音...';
    
    // 创建FormData
    const formData = new FormData();
    formData.append('file', selectedFile.value, selectedFile.value.name);
    
    // 调用文本转语音API
    const result = await apiService.textToSpeech(formData);
    
    recognitionResult.value = result.data;
    ElMessage.success('识别完成！');
    
  } catch (error) {
    console.error('上传失败:', error);
    ElMessage.error('上传失败，请重试');
  } finally {
    uploading.value = false;
    loading.value = false;
  }
};

// 音频播放控制
const playAudio = () => {
  if (audioElement.value) {
    audioElement.value.play();
    isPlaying.value = true;
    
    // 监听播放结束事件
    audioElement.value.onended = () => {
      isPlaying.value = false;
    };
  }
};

const pauseAudio = () => {
  if (audioElement.value) {
    audioElement.value.pause();
    isPlaying.value = false;
  }
};

const stopAudio = () => {
  if (audioElement.value) {
    audioElement.value.pause();
    audioElement.value.currentTime = 0;
    isPlaying.value = false;
  }
};

// 组件挂载
onMounted(() => {
  // 检查浏览器支持文件上传
  if (!window.File || !window.FileReader) {
    ElMessage.error('您的浏览器不支持文件上传功能');
  }
});

// 组件卸载
onUnmounted(() => {
  // 清理资源
  resetSelection();
});
</script>

<style scoped>
.take-photo-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h2 {
  font-size: 28px;
  color: #303133;
  margin: 0;
}

/* 上传区域 */
.upload-section {
  margin-bottom: 30px;
}

.upload-container {
  text-align: center;
  padding: 40px 20px;
  border: 2px dashed #dcdfe6;
  border-radius: 12px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.upload-container:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-tips {
  color: #909399;
  font-size: 14px;
  line-height: 1.5;
}

.upload-tips p {
  margin: 5px 0;
}

.photo-preview {
  text-align: center;
}

.selected-image {
  width: 100%;
  max-width: 600px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.photo-controls {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* 结果区域 */
.result-section {
  margin-top: 30px;
}

.result-card {
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.text-result {
  margin-bottom: 25px;
}

.text-result h3 {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.text-content {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #409eff;
  font-size: 16px;
  line-height: 1.6;
  color: #303133;
}

.audio-result {
  margin-bottom: 25px;
}

.audio-result h3 {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.audio-controls {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.audio-player {
  display: none; /* 隐藏默认的音频控件 */
}

.audio-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.audio-buttons .el-button {
  min-width: 80px;
}

.video-result h3 {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.video-container {
  text-align: center;
}

.video-player {
  width: 100%;
  max-width: 600px;
  height: auto;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.video-controls {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.speed-control span {
  font-size: 14px;
  color: #606266;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-overlay p {
  color: white;
  font-size: 16px;
  margin-top: 15px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .take-photo-container {
    padding: 15px;
  }
  
  .header h2 {
    font-size: 24px;
  }
  
  .camera-controls,
  .photo-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .camera-controls .el-button,
  .photo-controls .el-button {
    width: 200px;
    height: 48px;
    font-size: 16px;
  }
  
  .text-content {
    font-size: 15px;
    padding: 12px;
  }
  
  .video-controls {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .take-photo-container {
    padding: 10px;
  }
  
  .header h2 {
    font-size: 22px;
  }
  
  .camera-controls .el-button,
  .photo-controls .el-button {
    width: 180px;
    height: 44px;
    font-size: 15px;
  }
  
  .text-content {
    font-size: 14px;
    padding: 10px;
  }
}
</style>