<template>
  <!-- <Navbar /> -->
  <router-view />
  <BottomNavbar />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Navbar from './components/Navbar.vue'; // 导入 Navbar 组件
import BottomNavbar from './components/BottomNavbar.vue'; // 导入 BottomNavbar 组件

export default defineComponent({
  name: 'App',
  components: {
    Navbar, // 注册 Navbar 组件
    BottomNavbar, // 注册 BottomNavbar 组件
  },
});
</script>

<style>
/* Global styles are typically handled in a separate CSS file imported in main.ts */
/* This file can remain minimal or include styles specific to the App shell if needed */

/* 为主内容区域添加底部间距，避免被底部导航遮挡 */
body {
  padding-bottom: 60px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  body {
    padding-bottom: 65px;
  }
}

@media (max-width: 480px) {
  body {
    padding-bottom: 70px;
  }
}
</style>
