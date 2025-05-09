import axios from 'axios'
import { useUserStore } from '@/stores/user'

const apiAxios = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

// REQUEST: Attach token if available
apiAxios.interceptors.request.use(req => {
  const store = useUserStore()
  if (store.accessToken && !store.isAccessTokenExpired) {
    req.headers.Authorization = `Bearer ${store.accessToken}`
  }
  return req
})

// RESPONSE: Try to refresh if 401
apiAxios.interceptors.response.use(
  res => res,
  async error => {
    const store = useUserStore()

    const originalRequest = error.config
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      store.refreshToken &&
      !store.isRefreshTokenExpired
    ) {
      originalRequest._retry = true
      try {
        await store.refresh()
        originalRequest.headers.Authorization = `Bearer ${store.accessToken}`
        return apiAxios(originalRequest)
      } catch (e) {
        store.logout()
      }
    }

    return Promise.reject(error)
  }
)

export default apiAxios
