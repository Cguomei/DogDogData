import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API error:', error.message)
    return Promise.reject(error)
  }
)

export function fetchDashboardStats() {
  return api.get('/dashboard/stats')
}

export function fetchChartHtml(name) {
  return api.get(`/chart/${name}`)
}

export function fetchFoodStats() {
  return api.get('/food/statistics')
}

export function fetchFoodList(params) {
  return api.get('/food/list', { params })
}

export default api
