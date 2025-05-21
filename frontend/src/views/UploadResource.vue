<template>
  <el-card class="upload-resource-card">
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
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { ElMessage } from 'element-plus';
import apiService from '@/services/apiService';

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
          } else {
            error.value = '音频生成失败';
          }
        } else if (isMp3) {
          // 语音转文本
          const res = await apiService.speechToText(formData);
          if (res && res.text) {
            resultText.value = res.text;
            ElMessage.success('识别文本成功');
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
.upload-resource-card {
  margin: 20px;
}
</style>