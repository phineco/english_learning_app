<template>
  <el-card class="register-card">
    <h2>用户注册</h2>
    <el-form @submit.prevent="handleRegister">
      <el-form-item label="用户名">
        <el-input v-model="username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="邮箱">
        <el-input v-model="email" type="email" placeholder="请输入邮箱"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="confirmPassword" type="password" placeholder="请再次输入密码"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" native-type="submit">注册</el-button>
      </el-form-item>
    </el-form>
    <p>已有账户? <router-link to="/login">立即登录</router-link></p>
  </el-card>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus';
import apiService from '@/services/apiService'; // 稍后会创建

export default defineComponent({
  name: 'RegisterView',
  setup() {
    const username = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const router = useRouter();
    const handleRegister = async () => {
      if (!username.value || !email.value || !password.value || !confirmPassword.value) {
        ElMessage.error('请填写所有字段');
        return;
      }
      if (password.value !== confirmPassword.value) {
        ElMessage.error('两次输入的密码不一致');
        return;
      }
      try {
        const response = await apiService.register({ username: username.value, email: email.value, password: password.value });
        console.log('Registration successful', response);
        ElMessage.success('注册成功，请登录');
        router.push('/login'); // 注册成功后跳转到登录页
      } catch (error) {
        ElMessage.error('注册失败，请稍后再试');
        console.error('Registration failed', error);
      }
    };

    return {
      username,
      email,
      password,
      confirmPassword,
      handleRegister,
    };
  },
});
</script>

<style scoped>
.register-card {
  max-width: 450px;
  margin: 50px auto;
  padding: 20px;
}
</style>