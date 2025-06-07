<template>
    <h2>上传学习资源</h2>
    <el-upload
      class="upload-demo"
      drag
      :action="''"
      :auto-upload="false"
      :before-upload="beforeUpload"
      :on-change="handleFileChange"
      :file-list="fileList"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将mp3或txt文件拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">仅支持mp3或txt文件</div>
    </el-upload>
    <el-button type="primary" :disabled="!selectedFile" @click="handleSubmit" style="margin-top: 20px;">提交</el-button>
    <div v-if="loading" style="margin-top: 10px;">处理中...</div>
    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    <div v-if="resultText" style="margin-top: 10px;">
      <h4>识别/生成结果：</h4>
      <pre>{{ resultText }}</pre>
    </div>
    <div v-if="resultAudioUrl" style="margin-top: 10px;">
      <h4>生成音频：</h4>
      <audio :src="resultAudioUrl" controls></audio>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { ElMessage } from 'element-plus';
import apiService from '../services/apiService';
import router from '../router';

export default defineComponent({
  name: 'UploadResource',
  setup() {
    const fileList = ref<any[]>([]);
    const selectedFile = ref<File | null>(null);
    const loading = ref(false);
    const error = ref<string | null>(null);
    const resultText = ref('');
    const resultAudioUrl = ref('');

    const beforeUpload = (file: File) => {
      const isMp3 = file.type === 'audio/mpeg' || file.name.endsWith('.mp3');
      const isTxt = file.type === 'text/plain' || file.name.endsWith('.txt');
      if (!isMp3 && !isTxt) {
        ElMessage.error('只能上传mp3或txt文件');
        return false;
      }
      return true;
    };

    const handleFileChange = (file: any) => {
      selectedFile.value = file.raw;
      fileList.value = [file];
      resultText.value = '';
      resultAudioUrl.value = '';
      error.value = null;
    };

    const handleSubmit = async () => {
      if (!selectedFile.value) {
        ElMessage.warning('请先选择文件');
        return;
      }
      loading.value = true;
      error.value = null;
      resultText.value = '';
      resultAudioUrl.value = '';
      const file = selectedFile.value;
      const isMp3 = file.type === 'audio/mpeg' || file.name.endsWith('.mp3');
      const isTxt = file.type === 'text/plain' || file.name.endsWith('.txt');
      const formData = new FormData();
      formData.append('file', file);
      try {
        if (isTxt) {
          // 文本转语音
          const res = await apiService.textToSpeech(formData);
          if (res.data && res.data.audioUrl) {
            resultAudioUrl.value = res.data.audioUrl;
            ElMessage.success('生成音频成功');
            router.push({ name: 'ResourceLibrary' });
          } else {
            error.value = '音频生成失败';
          }
        } else if (isMp3) {
          // 语音转文本
          const res = await apiService.speechToText(formData);
          if (res.data && res.data.text) {
            resultText.value = res.data.text;
            ElMessage.success('识别文本成功');
            router.push({ name: 'ResourceLibrary' });
          } else {
            error.value = '文本识别失败';
          }
        } else {
          error.value = '文件类型不支持';
        }
      } catch (err) {
        error.value = '处理失败';
        ElMessage.error(error.value);
        console.error(err);
      }
      loading.value = false;
    };

    return {
      fileList,
      selectedFile,
      loading,
      error,
      resultText,
      resultAudioUrl,
      beforeUpload,
      handleFileChange,
      handleSubmit,
    };
  },
});
</script>

<style scoped>
.upload-resource {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
}

.upload-resource h1 {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
}

.upload-area {
  margin: 20px 0;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-button {
  margin: 5px;
  min-height: 40px;
}

.el-upload {
  width: 100%;
}

.el-upload-dragger {
  width: 100%;
  height: 180px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .upload-resource {
    margin: 10px;
    padding: 15px;
  }
  
  .upload-resource h1 {
    font-size: 26px;
    margin-bottom: 25px;
  }
  
  .upload-area {
    margin: 25px 0;
  }
  
  .el-form-item {
    margin-bottom: 25px;
  }
  
  .el-form-item__label {
    font-size: 16px;
    margin-bottom: 8px;
    display: block;
    text-align: left;
  }
  
  .el-input {
    height: 48px;
  }
  
  .el-input__inner {
    height: 48px;
    font-size: 16px;
    padding: 0 15px;
  }
  
  .el-textarea__inner {
    font-size: 16px;
    padding: 15px;
    min-height: 120px;
  }
  
  .el-button {
    margin: 8px 4px;
    min-height: 48px;
    font-size: 16px;
    border-radius: 8px;
    padding: 12px 20px;
  }
  
  .el-button--primary {
    width: 100%;
    margin: 15px 0;
  }
  
  .el-upload-dragger {
    height: 200px;
    border-radius: 8px;
  }
  
  .el-upload-dragger .el-icon {
    font-size: 48px;
    margin-bottom: 15px;
  }
  
  .el-upload-dragger .el-upload__text {
    font-size: 16px;
    line-height: 1.5;
  }
  
  .el-upload-dragger .el-upload__tip {
    font-size: 14px;
    margin-top: 10px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .upload-resource {
    margin: 5px;
    padding: 12px;
  }
  
  .upload-resource h1 {
    font-size: 24px;
  }
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .el-form-item__label {
    font-size: 15px;
  }
  
  .el-input__inner {
    font-size: 15px;
  }
  
  .el-textarea__inner {
    font-size: 15px;
    min-height: 100px;
  }
  
  .el-button {
    margin: 6px 2px;
    min-height: 44px;
    font-size: 15px;
    padding: 10px 15px;
  }
  
  .el-upload-dragger {
    height: 160px;
  }
  
  .el-upload-dragger .el-icon {
    font-size: 40px;
  }
  
  .el-upload-dragger .el-upload__text {
    font-size: 15px;
  }
}

/* 表单布局优化 */
@media (max-width: 768px) {
  .el-form--label-top .el-form-item__label {
    padding-bottom: 8px;
  }
  
  .el-form-item__content {
    margin-left: 0 !important;
  }
}
</style>