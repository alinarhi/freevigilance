import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiAxios from '@/axios'
import { jwtDecode } from 'jwt-decode'
import type { User } from '@/api-client'
import { AxiosError, isAxiosError } from 'axios'


function isTokenExpired(token: string) {
    const decoded = jwtDecode(token)
    if (!decoded.exp) return true
    const now = Math.floor(Date.now() / 1000)
    return decoded.exp < now
}

export const useUserStore = defineStore('user', () => {
    const accessToken = ref(localStorage.getItem('access_token'))
    const refreshToken = ref(localStorage.getItem('refresh_token'))
    const user = ref<User | null>(JSON.parse(localStorage.getItem("user") || "null"))
    

    const isAuthenticated = computed(() => !!accessToken.value && !isAccessTokenExpired.value && !isRefreshTokenExpired.value)
    const isAccessTokenExpired = computed(() => {
        if (!accessToken.value) return true
        return isTokenExpired(accessToken.value!)
    })
    const isRefreshTokenExpired = computed(() => {
        if (!refreshToken.value) return true
        return isTokenExpired(refreshToken.value!)
    })

    const fetchUser = async () => {
        try {
            const response = await apiAxios.get('api/users/me/', {
                headers: {
                    Authorization: `Bearer ${accessToken.value}`,
                },
            })
            user.value = response.data
            localStorage.setItem('user', JSON.stringify(user.value))
            console.log('Fetched user:', response.data)
        } catch (err) {
            console.error('Failed to fetch user:', err)
        }
    }

    const login = async (username: string, password: string) => {
        logout()
        try {
            console.log('Trying to log in with username:', username)
            const response = await apiAxios.post('api/token/', { username: username, password: password })
            accessToken.value = response.data.access
            refreshToken.value = response.data.refresh
            localStorage.setItem('access_token', response.data.access)
            localStorage.setItem('refresh_token', response.data.refresh)

            await fetchUser()
            console.log('Logged in as:', user)
        } catch (err) {
            if (isAxiosError(err)) {
                const axiosError = err as AxiosError
                if (axiosError.status === 401) {
                    throw new Error('Ошибка входа: неверные данные')
                } else {
                    throw new Error('Ошибка при обращении к серверу')
                }
            } else {
                throw new Error('Неизвестная ошибка')
            }
        }
    }

    const refresh = async () => {
        if (!refreshToken.value) {
            logout()
            throw new Error('Отсутствует refresh_token')
        }

        try {
            console.log('Trying to refresh token')
            const response = await apiAxios.post('api/token/refresh', { refresh: refreshToken.value })
            accessToken.value = response.data.access
            localStorage.setItem('access_token', response.data.access)

        } catch (err) {
            logout()
            throw new Error('Ошибка обновления токена')
        }
    }

    const logout = () => {
        accessToken.value = null
        refreshToken.value = null
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        console.log('Logged out')
    }

    return {
        accessToken,
        refreshToken,
        user,
        isAuthenticated,
        isAccessTokenExpired,
        isRefreshTokenExpired,
        login,
        refresh,
        logout,
        fetchUser
    }
})
