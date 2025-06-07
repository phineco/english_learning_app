<template>
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
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus';
import apiService from '../services/apiService';

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
        // apiService.login returns the data directly due to the response interceptor
        const response: any = await apiService.login({ username: username.value, password: password.value });
        // 保存access_token到localStorage，有效期7天
        if (response && response.data.access_token) {
          const now = new Date().getTime();
          const access_expire = now + 20 * 60 * 1000;
          const refresh_expire = now + 30 * 24 * 60 * 60 * 1000;
          localStorage.setItem('user_info', JSON.stringify(response.data.user));
          localStorage.setItem('access_token', response.data.access_token);
          localStorage.setItem('access_token_expire', access_expire.toString());
          localStorage.setItem('refresh_token', response.data.refresh_token);
          localStorage.setItem('refresh_token_expire', refresh_expire.toString());
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

.login-card h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
}

.login-card .el-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-top: 10px;
}

.login-card p {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .login-card {
    max-width: 90%;
    margin: 20px auto;
    padding: 25px 20px;
  }
  
  .login-card h2 {
    font-size: 26px;
    margin-bottom: 25px;
  }
  
  .login-card .el-form-item {
    margin-bottom: 20px;
  }
  
  .login-card .el-input {
    height: 48px;
  }
  
  .login-card .el-input__inner {
    height: 48px;
    font-size: 16px;
    padding: 0 15px;
  }
  
  .login-card .el-button {
    height: 50px;
    font-size: 18px;
    border-radius: 8px;
    margin-top: 15px;
  }
  
  .login-card p {
    font-size: 16px;
    margin-top: 25px;
  }
}

/* 小屏幕手机优化 */
@media (max-width: 480px) {
  .login-card {
    max-width: 95%;
    margin: 15px auto;
    padding: 20px 15px;
  }
  
  .login-card h2 {
    font-size: 24px;
  }
  
  .login-card .el-form-item__label {
    font-size: 15px;
  }
}
</style>
