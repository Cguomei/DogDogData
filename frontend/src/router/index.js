import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/charts',
    name: 'Charts',
    component: () => import('../views/ChartsList.vue'),
  },
  {
    path: '/food',
    name: 'Food',
    component: () => import('../views/FoodPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
