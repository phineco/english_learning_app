<template>
  <el-result icon="error" title="404 - 页面未找到" sub-title="抱歉，您访问的页面不存在。">
    <template #extra>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </template>
  </el-result>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'NotFoundView',
  setup() {
    const router = useRouter();
    const goHome = () => {
      router.push('/');
    };
    return {
      goHome,
    };
  },
});
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 50px;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.not-found h1 {
  font-size: 72px;
  color: #409eff;
  margin-bottom: 20px;
  font-weight: bold;
}

.not-found p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
  line-height: 1.5;
}

.not-found .el-button {
  padding: 12px 30px;
  font-size: 16px;
  border-radius: 8px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .not-found {
    padding: 30px 20px;
    min-height: 50vh;
  }
  
  .not-found h1 {
    font-size: 64px;
    margin-bottom: 25px;
  }
  
  .not-found p {
    font-size: 20px;
    margin-bottom: 35px;
    padding: 0 10px;
  }
  
  .not-found .el-button {
    padding: 15px 40px;
    font-size: 18px;
    min-height: 50px;
    border-radius: 10px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .not-found {
    padding: 20px 15px;
    min-height: 45vh;
  }
  
  .not-found h1 {
    font-size: 56px;
    margin-bottom: 20px;
  }
  
  .not-found p {
    font-size: 18px;
    margin-bottom: 30px;
    padding: 0 5px;
  }
  
  .not-found .el-button {
    padding: 12px 35px;
    font-size: 16px;
    min-height: 48px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 360px) {
  .not-found h1 {
    font-size: 48px;
  }
  
  .not-found p {
    font-size: 16px;
  }
}
</style>