<script setup lang="ts">
import { TasksApi, UsersApi, type Task, type User, type TaskStatus, TaskStatusEnum } from '@/api-client'
import apiAxios from '@/axios'
import { ref, computed, onMounted, watch } from 'vue'
import AppModal from '@/components/AppModal.vue'
import TaskCard from '@/components/TaskCard.vue'
import TaskForm from '@/components/TaskForm.vue'
import type { TaskFormMode } from '@/components/TaskForm.vue'
import TaskList from '@/components/TaskList.vue'
import { useUserStore } from '@/stores/user'
import { AxiosError, isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import { useRoute, useRouter } from 'vue-router';

const router = useRouter()
const route = useRoute()

const userStore = useUserStore()
const taskApi = new TasksApi(undefined, undefined, apiAxios)

const fetchedTasks = ref<Task[]>([])
const search = computed({
  get: () => route.query.search ?? '',
  set: (search) => router.replace({ query: { ...route.query, search: search } })
})

const assigned = computed({
  get: () => (route.query.assigned == 'my' || route.query.assigned == 'all') ? route.query.assigned : 'my',
  set: (value) => router.replace({ query: { ...route.query, assigned: value } })
})

const status = computed({
  get: () => (route.query.status == 'actual' || route.query.status == 'completed') ? route.query.status : 'actual',
  set: (value) => router.replace({ query: { ...route.query, status: value } })
})

const selectedTask = ref<Task | null>(null)
const showTaskForm = ref(false)
const formMode = ref<TaskFormMode>('create')

const fetchTasks = async () => {
  try {
    if (assigned.value === 'my' && status.value === 'actual') {
      fetchedTasks.value = (await taskApi.tasksMyList()).data
    } else if (assigned.value === 'my' && status.value === 'completed') {
      fetchedTasks.value = (await taskApi.tasksMyCompletedList()).data
    } else if (assigned.value === 'all' && status.value === 'actual') {
      fetchedTasks.value = (await taskApi.tasksList()).data.filter((task) => {
        return task.status !== TaskStatusEnum.Completed
      })
    } else if (assigned.value === 'all' && status.value === 'completed') {
      fetchedTasks.value = (await taskApi.tasksCompletedList()).data
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const postTask = async (task: Task) => {
  try {
    const res = await taskApi.tasksCreate(task)
    if (res.status === 201) {
      alert('Задача успешно создана')
      return res.data
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}


const patchTask = async (task: Task) => {
  try {
    const res = await taskApi.tasksPartialUpdate(task.id!, task)
    if (res.status === 200) {
      alert('Задача успешно обновлена')
      return res.data
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const taskChangeStatus = async (task: Task, status: TaskStatus) => {
  try {
    const res = await taskApi.tasksChangeStatusCreate(task.id!, status)
    if (res.status === 200) {
      alert('Статус задачи обновлен')
      await fetchTasks()
      restoreSelectedTaskFromRoute()
    }
    else if (res.status === 201) {
      const newTask = res.data as unknown as Task
      alert(`Задача завершена.\nСоздана новая итерация повторяющейся задачи: ID = ${newTask.id}`)
      await fetchTasks()
      onTaskSelected(newTask)
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const filteredTasks = computed(() => {
  return fetchedTasks.value.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(search.value.toString().trim().toLowerCase())
      || task.description?.toLowerCase().includes(search.value.toString().toLowerCase())
    return matchesSearch
  })
})

const onTaskSelected = (task: Task) => {
  if (selectedTask.value !== task) {
    selectedTask.value = task
    router.replace({ query: { ...route.query, selected: task.id } })
  } else {
    selectedTask.value = null
    router.replace({ query: { ...route.query, selected: undefined } })
  }
}

const onTaskCreate = () => {
  selectedTask.value = null
  showTaskForm.value = true
  formMode.value = 'create'
}

const onTaskEdit = () => {
  if (selectedTask.value) {
    showTaskForm.value = true
    formMode.value = 'edit'
  }
}

const onTaskOpen = (task: Task) => {
  router.push({ name: 'task', params: { id: task.id } })
}

const onTaskFormSubmit = async (task: Task) => {
  switch (formMode.value) {
    case 'create':
      const createdTask = await postTask(task)
      await fetchTasks()
      if (createdTask) {
        onTaskSelected(createdTask)
      }
      break
    case 'edit':
      await patchTask(task)
      await fetchTasks()
      restoreSelectedTaskFromRoute()
      break
    case 'readonly':
      break
  }
  showTaskForm.value = false
}

const restoreSelectedTaskFromRoute = () => {
  if (route.query.selected) {
    selectedTask.value = filteredTasks.value.find(t => t.id === Number(route.query.selected)) ?? null
    if (!selectedTask.value) {
      router.replace({ query: { ...route.query, selected: undefined } })
    }
  }
}

onMounted(async () => {
  await fetchTasks()
  restoreSelectedTaskFromRoute()
})

</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- Search Header -->
    <div class="flex gap-4 justify-end-safe items-center font-bold mb-6">
      <input v-model.trim="search" placeholder="Поиск по тексту"
        class="flex-1 font-normal input rounded-lg border-gray-500 p-4 bg-white shadow-md" />
      <select v-model="assigned" @change="fetchTasks" class="cursor-pointer p-3">
        <option value="my">мои</option>
        <option value="all">все</option>
      </select>
      <select v-model="status" @change="fetchTasks" class="cursor-pointer p-3">
        <option value="actual">актуальные</option>
        <option value="completed">завершенные</option>
      </select>
      <button @click="onTaskCreate"
        class="cursor-pointer text-white bg-teal-600 shadow-md rounded-lg py-3 px-10 font-bold hover:bg-teal-700">
        Создать
      </button>
    </div>

    <div class="flex-1 flex overflow-hidden gap-4">
      <!-- Task List -->
      <div class="size-full overflow-y-auto">
        <div v-if="filteredTasks.length == 0" class="text-2xl text-center text-gray-600 p-10">Задачи не найдены</div>
        <TaskList :tasks="filteredTasks" @select-task="onTaskSelected" @open-task="onTaskOpen" />
      </div>
      <!-- Task Card -->
      <TaskCard class="w-2/5 flex-none h-full rounded-lg shadow-md" v-if="selectedTask"
        :show-edit-button="selectedTask.status !== TaskStatusEnum.Completed" :show-details-button="true"
        :show-change-status-button="userStore.user?.id == selectedTask.assigned_to" :task="selectedTask"
        @edit="onTaskEdit" @open-details="onTaskOpen(selectedTask)" @close="onTaskSelected(selectedTask)"
        @change-status="(status) => taskChangeStatus(selectedTask!, status)" />
    </div>
  </div>


  <AppModal v-if="showTaskForm">
    <TaskForm :task="selectedTask" :mode="formMode" @close="showTaskForm = false" @submit="onTaskFormSubmit" />
  </AppModal>
</template>