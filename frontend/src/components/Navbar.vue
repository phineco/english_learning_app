<template>
  <el-menu mode="horizontal" router :default-active="$route.path">
    <el-menu-item index="/">首页</el-menu-item>
    <el-menu-item index="/words">单词列表</el-menu-item>
    <el-menu-item index="/resource-library">资源库</el-menu-item>
    <el-menu-item index="/practice">跟读练习</el-menu-item>
    <el-menu-item index="/login" style="float: right;">登录</el-menu-item>
  </el-menu>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'Navbar',
});
</script>

<style scoped>
.el-menu {
  border-bottom: solid 1px #e6e6e6;
}
.el-menu-item {
  font-size: 16px;
}
</style>