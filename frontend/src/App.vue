<template>
  <Navbar />
  <router-view />
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import Navbar from './components/Navbar.vue'; // 导入 Navbar 组件

export default defineComponent({
  name: 'App',
  components: {
    Navbar, // 注册 Navbar 组件
  },
});
</script>

<style>
/* Global styles are typically handled in a separate CSS file imported in main.ts */
/* This file can remain minimal or include styles specific to the App shell if needed */
</style>
