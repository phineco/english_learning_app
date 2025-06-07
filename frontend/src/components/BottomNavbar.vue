<template>
  <div class="bottom-navbar">
    <div class="nav-item" @click="navigateTo('/')" :class="{ active: isActive('/') }">
      <el-icon size="24"><House /></el-icon>
      <span>Home</span>
    </div>
    <div class="nav-item" @click="navigateTo('/tasks')" :class="{ active: isActive('/tasks') }">
      <el-icon size="24"><List /></el-icon>
      <span>Task</span>
    </div>
    <div class="nav-item" @click="navigateTo('/resource-library')" :class="{ active: isActive('/resource-library') }">
      <el-icon size="24"><Folder /></el-icon>
      <span>Resource</span>
    </div>
    <div class="nav-item" @click="navigateTo('/profile')" :class="{ active: isActive('/profile') }">
      <el-icon size="24"><User /></el-icon>
      <span>My</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import { House, List, Folder, User } from '@element-plus/icons-vue';
const router = useRouter();
const route = useRoute();

const navigateTo = (path: string) => {
  router.push(path);
};

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/';
  }
  return route.path.startsWith(path);
};
</script>

<style scoped>
.bottom-navbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: #fff;
  border-top: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  height: 100%;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #909399;
}

.nav-item:hover {
  background-color: #f5f7fa;
}

.nav-item.active {
  color: #409eff;
}

.nav-item span {
  font-size: 12px;
  margin-top: 2px;
  font-weight: 500;
}

.nav-item .el-icon {
  margin-bottom: 2px;
}



/* 移动端优化 */
@media (max-width: 768px) {
  .bottom-navbar {
    height: 65px;
  }
  
  .nav-item span {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .bottom-navbar {
    height: 70px;
  }
  
  .nav-item .el-icon {
    font-size: 22px;
  }
  
  .nav-item span {
    font-size: 10px;
  }
}
</style>