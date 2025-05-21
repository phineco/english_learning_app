<template>
  <el-card class="login-card">
    <h2>用户登录</h2>
    <el-form @submit.prevent="handleLogin">
      <el-form-item label="用户名" label-width="80px">
        <el-input v-model="username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码" label-width="80px">
        <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
        <el-button type="primary" native-type="submit">登录</el-button>
    </el-form>
    <p>还没有账户? <router-link to="/register">立即注册</router-link></p>
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus';
import apiService from '@/services/apiService'; // 稍后会创建

export default defineComponent({
  name: 'LoginView',
  setup() {
    const username = ref('');
    const password = ref('');
    const router = useRouter();
    const handleLogin = async () => {
      if (!username.value || !password.value) {
        ElMessage.error('请输入用户名和密码');
        return;
      }
      try {
        const response = await apiService.login({ username: username.value, password: password.value });
        // 保存access_token到localStorage，有效期7天
        if (response && response.access_token) {
          const now = new Date().getTime();
          const expire = now + 7 * 24 * 60 * 60 * 1000;
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('access_token_expire', expire.toString());
        }
        console.log('Login successful', response);
        ElMessage.success('登录成功');
        router.push('/'); // 登录成功后跳转到首页
      } catch (error) {
        ElMessage.error('登录失败，请检查您的凭据');
        console.error('Login failed', error);
      }
    };

    return {
      username,
      password,
      handleLogin,
    };
  },
});
</script>

<style scoped>
.login-card {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
}
</style>