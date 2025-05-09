<script setup lang="ts">
import TaskCard from '@/components/TaskCard.vue'
import { onMounted, ref } from 'vue'

import type { Task, Comment, LogEntry } from '@/api-client'
import { TasksApi } from '@/api-client'

import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import router from '@/router'
import { handleAxiosError } from '@/utils/utils'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const taskApi = new TasksApi(undefined, undefined, apiAxios)
const ID = Number(router.currentRoute.value.params.id as string)
// const ID = number(idParam)
const task = ref<Task | null>(null)

const comments = ref<Comment[]>([])
const changelog = ref<LogEntry[]>([])
const notFound = ref(false)

const actions = new Map();
actions.set('create', 'создал(-а)')
actions.set('update', 'изменил(-а)')
actions.set('delete', 'удалил(-а)')

const fetchData = async () => {
    try {
        const res = await taskApi.tasksRetrieve(ID)
        task.value = res.data
        const changelogRes = await taskApi.tasksChangelogList(ID)
        const commentsRes = await taskApi.tasksCommentsList(ID)
        changelog.value = changelogRes.data
        comments.value = commentsRes.data
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            if (error.response?.status === 404) {
                notFound.value = true
                //   router.push({ name: 'tasks' })
            } else {
                handleAxiosError(error)
            }
        }
    }
}


onMounted(() => {
    fetchData()
})
</script>

<template>
    <div v-if="notFound || !task" class="text-2xl text-center text-gray-600 p-10">404 Задача не найдена.</div>
    <div v-else class="flex h-screen gap-4">
        <!-- Left Column -->
        <div class="flex flex-col w-2/3 gap-4">
            <!-- Task Card -->
            <div class="rounded-xl shadow-md">
                <TaskCard :show-buttons="false" :task="task" />
            </div>

            <!-- Scrollable Comments -->
            <div class="flex-1 overflow-y-auto bg-white rounded-xl shadow-md p-4">
                <h2 class="text-lg font-semibold mb-2">Комментарии</h2>
                <ul class="space-y-3">
                    <li v-for="(comment, index) in comments" :key="index">
                        <div v-if="comment.created_by! === userStore.user?.id" class="text-end">
                            <div class="p-3 rounded-lg">{{ comment.text }}</div>
                            <div class="text-sm text-gray-700">{{ comment.created_by_display }}</div>
                            <div class="text-xs text-gray-500">{{ new
                                Date(comment.created_at!).toLocaleString('ru-RU') }}</div>
                        </div>
                        <div v-else class="w-fit">
                            <div class="p-3rounded-lg">{{ comment.text }}</div>
                            <div class="text-sm text-gray-700">{{ comment.created_by_display }}</div>
                            <div class="text-xs text-gray-500">{{ new
                                Date(comment.created_at!).toLocaleString('ru-RU') }}</div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>

        <!-- Right Column -->
        <div class="w-1/3 overflow-y-auto bg-white rounded-xl shadow-md p-4">
            <h2 class="text-lg font-semibold mb-2">История изменений</h2>
            <ul class="divide-y divide-gray-300">
                <li v-for="log in changelog" :key="log.id" class="p-2 bg-gray-100 rounded-lg">
                    <div class="flex flex-wrap gap-x-2 items-center">
                        <span class="font-semibold">{{ new Date(log.timestamp ?? "").toLocaleString('ru-RU') }}:</span>
                        <span>Пользователь #{{ log.actor }}</span>
                        <span class="italic">{{ log.actor_display }}</span>
                        <span>{{ actions.get(log.action_display) ?? log.action_display }}</span>
                        <span class="font-bold text-end">{{ log.object_repr }}</span>
                    </div>
                    <p v-if="log.changes_text">Описание изменений: {{ log.changes_text }}</p>
                    <br>
                    <p v-if="log.changes">ИЗМЕНЕНИЯ:</p>
                    <ul>
                        <li v-for="(values, field) in log.changes">
                            <div class="flex flex-wrap gap-x-2 items-center">
                                <span class="font-semibold">{{ field }}:</span>
                                <span class="italic">{{ values[0] }} -> {{ values[1] }}</span>
                            </div>
                        </li>
                    </ul>
                    <br>
                    <!-- <p>{{ log }}</p> -->
                </li>
            </ul>
        </div>
    </div>
</template>