<template>
    <h2>个人中心</h2>
    
    <!-- 未登录状态 -->
    <div v-if="!isLoggedIn" class="login-prompt">
      <div class="login-content">
        <el-icon class="login-icon" size="60"><User /></el-icon>
        <h3>您还未登录</h3>
        <p>登录后可查看个人信息和学习统计</p>
        <el-button type="primary" size="large" @click="goToLogin">
          <el-icon><User /></el-icon>
          立即登录
        </el-button>
      </div>
    </div>

    <!-- 已登录状态 -->
    <div v-else>
      <div class="profile-section">
        <div class="avatar-section">
          <el-avatar :size="80" :src="userInfo.avatar" icon="User" />
          <div class="user-info">
            <h3>{{ userInfo.username }}</h3>
            <p>{{ userInfo.email }}</p>
            <div class="user-details" v-if="userInfo.joinDate">
              <span class="detail-item">
                <el-icon><Calendar /></el-icon>
                加入时间：{{ formatDate(userInfo.joinDate) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <el-menu mode="vertical" class="profile-menu">
          <!-- <el-menu-item index="1" @click="goToWordList">
            <el-icon><Document /></el-icon>
            <span>我的单词</span>
          </el-menu-item> -->
          <el-menu-item index="2" @click="goToPracticeHistory">
            <el-icon><Clock /></el-icon>
            <span>练习记录</span>
          </el-menu-item>
          <el-menu-item index="3" @click="goToSettings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
          <el-menu-item index="4" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="stats-section">
        <h3>学习统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalWords }}</div>
            <div class="stat-label">总单词数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.practiceCount }}</div>
            <div class="stat-label">练习次数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.studyDays }}</div>
            <div class="stat-label">学习天数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.accuracy }}%</div>
            <div class="stat-label">准确率</div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Document, Clock, Setting, SwitchButton, User, Calendar } from '@element-plus/icons-vue';
import apiService from '../services/apiService';

const router = useRouter();

const userInfo = ref({
  username: '',
  email: '',
  avatar: ''
});

const stats = ref({
  totalWords: 0,
  practiceCount: 0,
  studyDays: 0,
  accuracy: 0
});

const isLoggedIn = computed(() => {
  return !!localStorage.getItem('access_token');
});

const goToWordList = () => {
  router.push('/words');
};

const goToPracticeHistory = () => {
  // 这里可以跳转到练习历史页面
  ElMessage.info('练习记录功能开发中');
};

const goToSettings = () => {
  // 这里可以跳转到设置页面
  ElMessage.info('设置功能开发中');
};

const goToLogin = () => {
  router.push('/login');
};

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('access_token_expire');
    localStorage.removeItem('refresh_token_expire');
    localStorage.removeItem('user_info');
    userInfo.value = { username: '', email: '', avatar: '' };
    ElMessage.success('已退出登录');
    router.push('/login');
  } catch {
    // 用户取消退出
  }
};

const loadUserInfo = () => {
  console.log(apiService.test());
  const token = localStorage.getItem('access_token');
  const savedUserInfo = localStorage.getItem('user_info');
  
  if (token && savedUserInfo) {
    try {
      const parsedInfo = JSON.parse(savedUserInfo);
      userInfo.value = {
        ...parsedInfo,
        joinDate: parsedInfo.created_at || '2024-01-01' // 默认加入时间
      };
    } catch (e) {
      console.error('解析用户信息失败:', e);
    }
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const loadStats = () => {
  // 只有在登录状态下才加载统计数据
  if (isLoggedIn.value) {
    // 这里可以从后端API获取用户统计数据
    // 暂时使用模拟数据
    stats.value = {
      totalWords: 156,
      practiceCount: 42,
      studyDays: 15,
      accuracy: 85
    };
  } else {
    stats.value = {
      totalWords: 0,
      practiceCount: 0,
      studyDays: 0,
      accuracy: 0
    };
  }
};

onMounted(() => {
  loadUserInfo();
  loadStats();
});
</script>

<style scoped>
.profile-card {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
}

.profile-card h2 {
  font-size: 24px;
  margin-bottom: 20px;
  text-align: center;
  color: #303133;
}

.profile-section {
  margin-bottom: 30px;
}

.avatar-section {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.user-info {
  margin-left: 20px;
}

.user-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  color: #303133;
}

.user-info p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.user-details {
  margin-top: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #606266;
  margin-bottom: 4px;
}

.detail-item .el-icon {
  margin-right: 6px;
  color: #909399;
}

/* 未登录状态样式 */
.login-prompt {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  padding: 40px 20px;
}

.login-content {
  text-align: center;
  max-width: 300px;
}

.login-icon {
  color: #c0c4cc;
  margin-bottom: 20px;
}

.login-content h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 12px 0;
}

.login-content p {
  color: #909399;
  font-size: 14px;
  margin: 0 0 24px 0;
  line-height: 1.5;
}

.login-content .el-button {
  padding: 12px 24px;
  font-size: 16px;
}

.menu-section {
  margin-bottom: 30px;
}

.profile-menu {
  border: none;
}

.profile-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin-bottom: 8px;
  border-radius: 8px;
  transition: all 0.3s;
}

.profile-menu .el-menu-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.stats-section h3 {
  font-size: 18px;
  margin-bottom: 16px;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.stat-item:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .profile-card {
    margin: 10px;
    padding: 15px;
  }
  
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }
  
  .user-info {
    margin-left: 0;
    margin-top: 15px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-item {
    padding: 15px;
  }
  
  .stat-number {
    font-size: 20px;
  }
}

@media (max-width: 480px) {
  .profile-card {
    margin: 5px;
    padding: 10px;
  }
  
  .profile-card h2 {
    font-size: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .stat-item {
    padding: 12px;
  }
  
  .stat-number {
    font-size: 18px;
  }
  
  .profile-menu .el-menu-item {
    height: 45px;
    line-height: 45px;
  }
}
</style>