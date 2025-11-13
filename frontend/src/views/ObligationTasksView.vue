<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'

import { TaskStatusEnum, type Obligation, type Task } from '@/api-client'
import { ObligationsApi, TasksApi } from '@/api-client'
import { useRoute, useRouter } from 'vue-router'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import AppModal from '@/components/AppModal.vue'
import TaskForm from '@/components/TaskForm.vue'
import TaskList from '@/components/TaskList.vue'
import ObligationForm from '@/components/ObligationForm.vue'
import type { FormMode } from '@/components/ObligationForm.vue'
import ButtonEdit from '@/components/ButtonEdit.vue'
import ButtonFilter from '@/components/ButtonFilter.vue'
import type { TaskFilters } from '@/components/TaskFiltersForm.vue'
import TaskFiltersForm from '@/components/TaskFiltersForm.vue'

const router = useRouter()
const route = useRoute()

const obligationsApi = new ObligationsApi(undefined, undefined, apiAxios)
const tasksApi = new TasksApi(undefined, undefined, apiAxios)
const ID = Number(router.currentRoute.value.params.id as string)
const obligation = ref<Obligation>()

const fetchedTasks = ref<Task[]>([])
const notFound = ref(false)
const showObligationModal = ref(false)
const showTaskModal = ref(false)
const showFiltersForm = ref(false)
const taskFilters = ref<TaskFilters>({})

const search = computed({
    get: () => route.query.search ?? '',
    set: (search) => router.replace({ query: { ...route.query, search: search } })
})

const tasks = computed(() => {
    return fetchedTasks.value.filter((task) => {
        const matchesSearch = task.title.toLowerCase().includes(search.value.toString().trim().toLowerCase())
            || task.description?.toLowerCase().includes(search.value.toString().toLowerCase())
        return matchesSearch
    })
})

const fetchData = async () => {
    try {
        const res = await obligationsApi.obligationsRetrieve(ID)
        obligation.value = res.data
        const tasksRes = await tasksApi.obligationsTasksList(ID, {
            params: {
                assigned_to: taskFilters.value.assignedTo,
                created_by: taskFilters.value.createdBy,
                deadline__gte: taskFilters.value.deadlineGte,
                deadline__lte: taskFilters.value.deadlineLte,
                status: taskFilters.value.status
            }
        })
        fetchedTasks.value = tasksRes.data
        console.log(obligation.value)
        console.log(fetchedTasks.value)
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

const onFiltersFormSubmit = async (filters: TaskFilters) => {
    taskFilters.value = { ...filters }
    await router.replace({ query: { ...route.query, ...filters } })
    await fetchData()
    showFiltersForm.value = false
}

const onObligationFormSubmit = async (obligation: Obligation) => {
    try {
        const res = await obligationsApi.obligationsPartialUpdate(obligation.id!, obligation)
        if (res.status === 200) {
            alert('Обязательство успешно обновлено')
            showObligationModal.value = false
            await fetchData()
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const onTaskFormOpen = () => {
    if (obligation) {
        const emptyTask: Task = { title: '', deadline: '', obligation: obligation.value!.id! }
    }
}

const onTaskFormSubmit = async (task: Task) => {
    try {
        const res = await tasksApi.tasksCreate(task)
        if (res.status === 201) {
            alert('Задача успешно создана')
            showTaskModal.value = false
            await fetchData()
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const openTaskPage = (task: Task) => {
    router.push({ name: 'task', params: { id: task.id } })
}

onMounted(async () => {
    taskFilters.value = {
        assignedTo: isNaN(Number(route.query.assignedTo)) ? undefined : Number(route.query.assignedTo),
        createdBy: isNaN(Number(route.query.createdBy)) ? undefined : Number(route.query.createdBy),
        deadlineGte: route.query.deadlineGte?.toString(),
        deadlineLte: route.query.deadlineLte?.toString(),
        status: route.query.status?.toString() as TaskStatusEnum
    }
    await fetchData()
})
</script>

<template>
    <div v-if="notFound" class="text-2xl text-center text-gray-600 p-10">404 Договор не найден.</div>
    <!-- <div v-else v-if="obligation" class="h-full w-2/3 min-w-min flex flex-col overflow-hidden wrap-anywhere gap-4"> -->
    <div v-else v-if="obligation" class="h-full flex overflow-hidden wrap-anywhere gap-4">

        <!-- Tasks -->
        <div class="h-full flex-3/5 flex flex-col gap-4 m-1 py-4">
            <!-- Header -->
            <div class="flex items-center gap-2 justify-between wrap-normal text-lg font-semibold mb-4">
                <div class="text-2xl font-bold text-gray-800 px-4"> Задачи </div>
                <ButtonFilter @click="showFiltersForm = true" />
                <input v-model="search" placeholder="Поиск по тексту"
                    class="flex-1 font-normal input rounded-lg border-gray-500 p-3 bg-white shadow-md" />
                <button @click="showTaskModal = true"
                    class="cursor-pointer bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg">Добавить</button>
            </div>
            <!-- List -->
            <div class="flex-1 overflow-y-auto">
                <div v-if="tasks.length === 0" class="text-2xl text-center text-gray-600 p-10">Задачи не найдены</div>
                <TaskList :tasks="tasks" @open-task="openTaskPage" />
            </div>
        </div>

        <!-- Obligation Card -->
        <div class="flex-2/5 flex flex-col overflow-hidden rounded-xl shadow-md bg-white p-4 mb-1">
            <div class="flex items-start justify-between">
                <div class="mb-4">
                    <div class="text-sm text-gray-600"> {{ obligation.pva_display }}</div>
                    <div class="text-2xl font-bold"> {{ obligation.title }}</div>
                </div>
                <ButtonEdit @click="showObligationModal = true" />
            </div>

            <div class="text-sm text-gray-600"> ID: {{ obligation.id }}</div>

            <div v-if="obligation.responsibility_type" class="font font-semibold">Тип: <span class="text-teal-700">{{
                obligation.responsibility_type }}</span></div>
            <div><span class="font-semibold">Сроки: </span> с {{ new
                Date(obligation.start_date).toLocaleDateString('ru-RU') }} по {{ new
                    Date(obligation.end_date).toLocaleDateString('ru-RU') }}</div>
            <br>
            <br>
            <div class="flex-1 overflow-y-auto whitespace-pre-wrap text-gray-700 italic">{{ obligation.description }}
            </div>
        </div>

        <AppModal v-if="showObligationModal">
            <ObligationForm :pva_id="obligation.pva" :obligation="obligation" :mode="'edit'"
                @close="showObligationModal = false" @submit="onObligationFormSubmit" />
        </AppModal>

        <AppModal v-if="showTaskModal">
            <TaskForm :obligationId="obligation.id" :mode="'create'" @close="showTaskModal = false" @submit="onTaskFormSubmit" />
        </AppModal>

        <AppModal v-if="showFiltersForm">
            <TaskFiltersForm :filters="taskFilters" :excludeType="true" @close="showFiltersForm = false" @submit="onFiltersFormSubmit" />
        </AppModal>
    </div>
</template>