import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue';
import LoginView from '../views/Login.vue';
import RegisterView from '../views/Register.vue';
import WordListView from '../views/WordList.vue';
import PracticeView from '../views/Practice.vue';
import NotFoundView from '../views/NotFound.vue'; // 引入 NotFoundView
import UploadResource from '../views/UploadResource.vue'; 
import ResourceLibrary from '../views/ResourceLibrary.vue';
import Test from '../views/Test.vue';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
  },
  {
    path: '/words',
    name: 'WordList',
    component: WordListView,
    // meta: { requiresAuth: true } // 如果需要登录才能访问
  },
  {
    path: '/practice/:id?', // wordId 是可选参数，方便直接跳转到特定单词练习
    name: 'Practice',
    component: PracticeView,
    props: true, // 将路由参数作为 props 传递给组件
    // meta: { requiresAuth: true }
  },
  { 
    path: '/:pathMatch(.*)*', 
    name: 'NotFound', 
    component: NotFoundView 
  },
  {
    path: '/upload',
    name: 'UploadResource',
    component: UploadResource,
  },
  {
    path: '/resource-library',
    name: 'ResourceLibrary',
    component: ResourceLibrary,
  },
  {
    path: '/test',
    name: 'Test',
    component: Test,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 导航守卫 (示例)
// router.beforeEach((to, from, next) => {
//   const isAuthenticated = !!localStorage.getItem('user-token'); // 简单的token检查
//   if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
//     next({ name: 'Login' });
//   } else {
//     next();
//   }
// });

export default router;