<script setup lang="ts">
import TaskCard from '@/components/TaskCard.vue'
import { nextTick, onMounted, ref, useTemplateRef, watchEffect } from 'vue'

import type { Task, Comment, LogEntry, TaskStatus } from '@/api-client'
import { TaskStatusEnum, TasksApi } from '@/api-client'

import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import { useUserStore } from '@/stores/user'
import { ActionDisplay } from '@/utils/constants'
import { useRoute } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import TaskForm from '@/components/TaskForm.vue'
import LogEntryCard from '@/components/LogEntryCard.vue'

const route = useRoute()
const userStore = useUserStore()
const taskApi = new TasksApi(undefined, undefined, apiAxios)
const ID = Number(route.params.id)
const task = ref<Task>()

const comment = ref<Comment>({ text: '' })
const comments = ref<Comment[]>([])
const changelog = ref<LogEntry[]>([])
const notFound = ref(false)
const showTaskForm = ref(false)

const commentsListElement = useTemplateRef('comments-list')

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
            } else {
                handleAxiosError(error)
            }
        }
    }
}

const onTaskFormSubmit = async (task: Task) => {
    try {
        const res = await taskApi.tasksPartialUpdate(ID, task)
        if (res.status === 200) {
            alert('Задача успешно обновлена')
            await fetchData()
            showTaskForm.value = false
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const changeTaskStatus = async (status: TaskStatus) => {
    try {
        const res = await taskApi.tasksChangeStatusCreate(ID, status)
        if (res.status === 200) {
            alert('Статус задачи обновлен')
        }
        else if (res.status === 201) {
            const newTask = res.data as unknown as Task
            alert(`Задача завершена.\nСоздана новая итерация повторяющейся задачи: ID = ${newTask.id}`)
        }
        await fetchData()
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const postComment = async () => {
    try {
        const res = await taskApi.tasksCommentsCreate(ID, comment.value)
        if (res.status === 201) {
            comments.value.push(res.data)
            comment.value.text = ''
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

// Autoscroll to the latest comment
watchEffect(async () => {
    // Access comments to track changes
    comments.value.length
    await nextTick()
    if (commentsListElement.value) {
        commentsListElement.value.scrollTop = commentsListElement.value.scrollHeight
    }
})

onMounted(async () => {
    await fetchData()
})
</script>

<template>
    <div v-if="notFound" class="text-2xl text-center text-gray-600 p-10">
        <p>404</p>
        <p>Задача не найдена</p>
    </div>
    <div v-else class="h-full">
        <div v-if="task" class="flex h-full overflow-hidden gap-2">
            <!-- Left Column -->
            <div class="w-3/5 flex-none flex flex-col overflow-hidden gap-2">
                <!-- Task Card -->
                <div class="h-7/10 grow">
                    <TaskCard class="rounded-xl shadow-md" :show-edit-button="task.status != TaskStatusEnum.Completed"
                        :show-change-status-button="task.assigned_to === userStore.user?.id"
                        :show-details-button="false" :task="task" @edit="showTaskForm = true"
                        @change-status="changeTaskStatus" />
                </div>

                <!-- Comments -->
                <div
                    class="flex h-auto max-h-3/10 flex-col overflow-hidden bg-white rounded-xl shadow-md p-4 space-y-2">
                    <h2 class="text-lg font-semibold">Комментарии</h2>
                    <ul ref="comments-list" class="flex-1 overflow-y-auto bg-white rounded-xl p-2 space-y-3">
                        <li v-for="comment in comments" :key="comment.id">
                            <div v-if="comment.created_by! === userStore.user?.id" class="flex justify-end text-end">
                                <div class="w-fit">
                                    <div class="bg-teal-600/20 p-3 rounded-lg">{{ comment.text }}</div>
                                    <div class="text-sm text-gray-700">{{ comment.created_by_display }}</div>
                                    <div class="text-xs text-gray-500">{{ new
                                        Date(comment.created_at!).toLocaleString('ru-RU') }}</div>
                                </div>
                            </div>
                            <div v-else class="w-fit">
                                <div class="bg-gray-100 p-3 rounded-lg">{{ comment.text }}</div>
                                <div class="text-sm text-gray-700">{{ comment.created_by_display }}</div>
                                <div class="text-xs text-gray-500">{{ new
                                    Date(comment.created_at!).toLocaleString('ru-RU') }}</div>
                            </div>
                        </li>
                    </ul>
                    <!-- Add Comment Section -->
                    <form @submit.prevent="postComment" class="flex gap-2 items-center">
                        <input v-model="comment.text" placeholder="Комментарий..."
                            class="flex-1 input rounded-lg border border-gray-300 p-2 bg-gray-50 shadow-md" required />
                        <button
                            class="cursor-pointer text-lg px-6 py-2 rounded-lg shadow-md font-semibold text-white bg-teal-600 hover:bg-teal-700">Отправить</button>
                    </form>
                </div>
            </div>


            <!-- Right Column: Changelog -->
            <div class="w-2/5 flex flex-col overflow-hidden bg-white rounded-xl shadow-md p-4 wrap-anywhere">
                <h2 class="text-lg font-semibold mb-2">История изменений</h2>
                <ul class="flex-1 overflow-y-auto divide-y divide-gray-300">
                    <li v-for="log in changelog" :key="log.id" class="p-2 bg-gray-100 rounded-lg">
                        <LogEntryCard :log="log" :showType="false"/>
                    </li>
                </ul>
            </div>
        </div>
    </div>

    <AppModal v-if="showTaskForm">
        <TaskForm :task="task" :mode="'edit'" @close="showTaskForm = false" @submit="onTaskFormSubmit" />
    </AppModal>

</template>