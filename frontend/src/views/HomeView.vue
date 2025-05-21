<template>
  <el-card class="home-card">
    <h2>欢迎使用英语跟读评分应用</h2>
    <p>在这里，您可以练习英语单词发音，并获得即时评分反馈。</p>
    <el-divider></el-divider>
    <div class="features">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover">
            <h3><el-icon><notebook /></el-icon> 单词列表</h3>
            <p>浏览和学习精心挑选的单词列表。</p>
            <el-button type="primary" @click="goTo('/words')">查看单词</el-button>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <h3><el-icon><microphone /></el-icon> 跟读练习</h3>
            <p>选择单词进行跟读，系统将对您的发音进行评分。</p>
            <el-button type="success" @click="goTo('/practice')">开始练习</el-button>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <h3><el-icon><upload /></el-icon> 上传资源</h3>
            <p>上传txt或mp3文件，自动生成音频或识别文本。</p>
            <el-button type="warning" @click="goTo('/upload')">上传资源</el-button>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover">
            <h3><el-icon><user /></el-icon> 用户中心</h3>
            <p>管理您的个人信息和学习记录 (待开发)。</p>
            <el-button type="info" disabled>敬请期待</el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </el-card>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';
import { Notebook, Microphone, User, Upload } from '@element-plus/icons-vue'; // 引入图标

export default defineComponent({
  name: 'HomeView',
  components: {
    Notebook,    // 注册图标组件
    Microphone,
    User
  },
  setup() {
    const router = useRouter();
    const goTo = (path: string) => {
      router.push(path);
    };
    return {
      goTo,
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
}
.features .el-icon {
  margin-right: 8px;
}
.features p {
  font-size: 14px;
  color: #606266;
  margin-bottom: 15px;
  min-height: 40px; /* Ensure consistent card height */
}
@media (max-width: 768px) {
  .features .el-row {
    flex-direction: column !important;
    display: flex !important;
  }
  .features .el-col {
    max-width: 100% !important;
    flex: 0 0 100% !important;
    margin-bottom: 16px;
  }
}
</style>