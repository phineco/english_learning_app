import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 从环境变量或默认 /api
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器，例如添加认证token
apiClient.interceptors.request.use(
  (config) => {
    // 检查token及有效期
    const token = localStorage.getItem('access_token');
    const expire = localStorage.getItem('access_token_expire');
    const now = new Date().getTime();

    // 检查访问令牌是否即将过期（如5分钟内）, 则刷新token
    if (token && expire && now + 5 * 60 * 1000 > Number(expire)) {
      return refreshAccessToken().then(() => {
        const newToken = localStorage.getItem('access_token');
        config.headers.Authorization = `Bearer ${newToken}`;
        return config;
      });
    } else if (config.url !== '/auth/login' && config.url !== '/auth/register') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    console.error(error);
    return Promise.reject(error);
  }
);

// 响应拦截器，例如处理全局错误
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error(error);
    // 例如，处理401未授权错误，跳转到登录页
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('access_token_expire');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('refresh_token_expire');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

async function refreshAccessToken() {
  let refreshToken = localStorage.getItem('refresh_token');
  const refreshExpire = localStorage.getItem('refresh_token_expire');
  const now = new Date().getTime();

  // 检查refresh token是否过期
  if (!refreshToken || (refreshExpire && now >= Number(refreshExpire))) {
    window.location.href = '/login';
    throw new Error('Refresh token已过期');
  }

  try {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/refresh`, {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
        'Content-Type': 'application/json'
      }
    });

    // 更新访问令牌
    let accessToken = response.data.access_token;
    localStorage.setItem('access_token', accessToken);
    const now = new Date().getTime();
    const access_expire = now + 20 * 60 * 1000;
    localStorage.setItem('access_token_expire', access_expire.toString());
    // 可选：更新刷新令牌（如果后端返回新的刷新令牌）
    // if (response.data.refresh_token) {
    //   refreshToken = response.data.refresh_token;
    //   localStorage.setItem('refresh_token', refreshToken);
    // }
  } catch (refreshError) {
    console.error('刷新访问令牌失败', refreshError);
    // 刷新失败 - 退出登录
    window.location.href = '/login';
    throw refreshError;
  }
}

export default {
  // 认证相关
  login(credentials: any) {
    return apiClient.post('/auth/login', credentials).then(res => res);
  },
  register(data: any) {
    return apiClient.post('/auth/register', data);
  },
  logout() {
    // 可能需要后端API支持
    localStorage.removeItem('user-token');
    return Promise.resolve();
  },

  // 单词相关
  getWords() {
    return apiClient.get('/words');
  },
  getWordById(id: string | number) {
    return apiClient.get(`/words/${id}`);
  },

  // 跟读录音相关
  submitRecordingForEvaluation(formData: FormData) {
    return apiClient.post('/records/submitRecords', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getUserRecordings() {
    return apiClient.get('/records/history');
  },
  // 更多API方法...
  // 获取资源库文件列表
  getResourceList() {
    return apiClient.get('/resources');
  },

  getResourceById(id: string | number) {
    return apiClient.get(`/resources/${id}`);
  },
  updateResource(id: string | number, data: any) {
    return apiClient.put(`/resources/${id}`, data);
  },
  // 新增：文本转语音
  textToSpeech(formData: FormData) {
    return apiClient.post('/convert/text-to-speech', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // 新增：语音转文本
  speechToText(formData: FormData) {
    return apiClient.post('/convert/speech-to-text', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getMp3(url: string, config = {}) {
    return apiClient.get(`/mp3/${url}`, { ...config, responseType: 'blob' });
  },

  // 任务相关
  getTasks(params?: any) {
    return apiClient.get('/tasks', { params });
  },
  getTaskById(id: string | number) {
    return apiClient.get(`/tasks/${id}`);
  },
  createTask(data: any) {
    console.log(data);
    return apiClient.post('/tasks', data);
  },
  updateTask(id: string | number, data: any) {
    return apiClient.put(`/tasks/${id}`, data);
  },
  deleteTask(id: string | number) {
    return apiClient.delete(`/tasks/${id}`);
  },
  batchDeleteTasks(ids: number[]) {
    return apiClient.delete('/tasks/batch', { data: { ids } });
  },
  getTaskStats() {
    return apiClient.get('/tasks/stats');
  },

  // 任务项相关
  getTaskItems(params?: any) {
    return apiClient.get('/task-items', { params });
  },
  getTaskItemById(id: string | number) {
    return apiClient.get(`/task-items/${id}`);
  },
  createTaskItem(data: any) {
    return apiClient.post('/task-items', data);
  },
  updateTaskItem(id: string | number, data: any) {
    return apiClient.put(`/task-items/${id}`, data);
  },
  deleteTaskItem(id: string | number) {
    return apiClient.delete(`/task-items/${id}`);
  },
  getTaskItemsByTask(taskId: string | number, params?: any) {
    return apiClient.get(`/tasks/${taskId}/items`, { params });
  },
  getUncompletedTaskItems() {
    return apiClient.get('/task-items/uncompleted');
  },

  test() {
    return apiClient.get('/test');
  }
};

  