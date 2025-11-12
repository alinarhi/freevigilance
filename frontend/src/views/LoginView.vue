<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

const username = ref('')
const password = ref('')
const usernameEmpty = ref(false)
const passwordEmpty = ref(false)
const router = useRouter()
const userStore = useUserStore()

const onLogin = async () => {
  usernameEmpty.value = !username.value.trim()
  passwordEmpty.value = !password.value.trim()
  if (usernameEmpty.value || passwordEmpty.value) return
  try {
    await userStore.login(username.value, password.value)
    router.push({ name: 'tasks' })
  } catch (error) {
    if (isAxiosError(error)) {
      handleAxiosError(error)
    } else {
      alert((error as Error).message)
    }
  }
}
</script>

<template>
  <div class="flex justify-center items-center min-h-full bg-gray-100">
    <form @submit.prevent="onLogin" class="p-6 bg-white shadow-md rounded-lg w-sm">
      <h1 class="text-xl font-semibold">Вход</h1>
      <input v-model="username" placeholder="Имя пользователя" class="input w-full mt-4 p-2" />
      <p v-if="usernameEmpty" class="text-red-500 text-sm mt-1">Введите имя пользователя</p>
      <input v-model="password" type="password" placeholder="Пароль" class="input w-full mt-4 p-2" />
      <p v-if="passwordEmpty" class="text-red-500 text-sm mt-1">Введите пароль</p>
      <button type="submit" class="cursor-pointer w-full mt-2 text-teal-700 font-semibold">Войти</button>
    </form>
  </div>
</template>