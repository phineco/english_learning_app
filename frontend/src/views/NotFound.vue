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
.el-result {
  height: 70vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>