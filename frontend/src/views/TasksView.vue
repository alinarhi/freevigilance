<script setup lang="ts">
import { TasksApi, type Task, type TaskStatus, TaskStatusEnum } from '@/api-client'
import apiAxios from '@/axios'
import { ref, computed, onMounted } from 'vue'
import AppModal from '@/components/AppModal.vue'
import TaskCard from '@/components/TaskCard.vue'
import TaskForm from '@/components/TaskForm.vue'
import TaskFiltersForm, { type TaskFilters } from '@/components/TaskFiltersForm.vue'
import type { TaskFormMode } from '@/components/TaskForm.vue'
import TaskList from '@/components/TaskList.vue'
import { useUserStore } from '@/stores/user'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import { useRoute, useRouter } from 'vue-router';
import ButtonFilter from '@/components/ButtonFilter.vue'

const router = useRouter()
const route = useRoute()

const userStore = useUserStore()
const taskApi = new TasksApi(undefined, undefined, apiAxios)

const fetchedTasks = ref<Task[]>([])
const tasks = computed(() => {
  return fetchedTasks.value.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(search.value.toString().trim().toLowerCase())
      || task.description?.toLowerCase().includes(search.value.toString().toLowerCase())
    return matchesSearch
  })
})

const search = computed({
  get: () => route.query.search ?? '',
  set: (search) => router.replace({ query: { ...route.query, search: search } })
})

const assigned = computed({
  get: () => (route.query.assigned == 'my' || route.query.assigned == 'all') ? route.query.assigned : 'my',
  set: async (value) => {
    if (value == 'my') {
      taskFilters.value.assignedTo = undefined
    }
    await router.replace({ query: { ...route.query, assigned: value, assignedTo: taskFilters.value.assignedTo } })
  }
})

const relevance = computed({
  get: () => (route.query.relevance == 'actual' || route.query.relevance == 'completed' || route.query.relevance == 'overdue') ? route.query.relevance : 'actual',
  set: async (value) => await router.replace({ query: { ...route.query, relevance: value } })
})

const selectedTask = ref<Task>()
const showTaskForm = ref(false)
const showFiltersForm = ref(false)
const formMode = ref<TaskFormMode>('create')
const taskFilters = ref<TaskFilters>({})
// IMPORTANT: filter args order may change if the API schema changes
type TaskListArgs = Parameters<typeof taskApi.tasksList>
const filtersArgs = computed<TaskListArgs>(() =>
  [taskFilters.value.assignedTo, , , taskFilters.value.createdBy, , , taskFilters.value.deadlineGte, taskFilters.value.deadlineLte, , , taskFilters.value.responsibilityType]
)

const fetchTasks = async () => {
  try {
    if (assigned.value === 'my' && (relevance.value === 'actual' || relevance.value === 'overdue')) {
      const data = (await taskApi.tasksMyList(...filtersArgs.value)).data
      const firstActualIdx = data.findIndex(t => new Date(t.deadline) >= new Date())
      if (firstActualIdx === -1) {
        fetchedTasks.value = relevance.value === 'actual' ? [] : data
      } else {
        fetchedTasks.value = relevance.value === 'actual' ? data.slice(firstActualIdx) : data.slice(0, firstActualIdx)
      }
    } else if (assigned.value === 'my' && relevance.value === 'completed') {
      fetchedTasks.value = (await taskApi.tasksMyCompletedList(...filtersArgs.value)).data
    } else if (assigned.value === 'all' && (relevance.value === 'actual' || relevance.value === 'overdue')) {
      const data = (await taskApi.tasksList(...filtersArgs.value)).data.filter((task) => task.status !== TaskStatusEnum.Completed)
      const firstActualIdx = data.findIndex(t => new Date(t.deadline) >= new Date())
      if (firstActualIdx === -1) {
        fetchedTasks.value = relevance.value === 'actual' ? [] : data
      } else {
        fetchedTasks.value = relevance.value === 'actual' ? data.slice(firstActualIdx) : data.slice(0, firstActualIdx)
      }
    } else if (assigned.value === 'all' && relevance.value === 'completed') {
      fetchedTasks.value = (await taskApi.tasksCompletedList(...filtersArgs.value)).data
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

const changeTaskStatus = async (task: Task, status: TaskStatus) => {
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
      selectTask(newTask)
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const selectTask = (task?: Task) => {
  if (task && selectedTask.value !== task) {
    selectedTask.value = task
    router.replace({ query: { ...route.query, selected: task.id } })
  } else {
    selectedTask.value = undefined
    router.replace({ query: { ...route.query, selected: undefined } })
  }
}

const onTaskCreate = () => {
  selectedTask.value = undefined
  showTaskForm.value = true
  formMode.value = 'create'
}

const onTaskEdit = () => {
  if (selectedTask.value) {
    showTaskForm.value = true
    formMode.value = 'edit'
  }
}

const openTaskPage = (task: Task) => {
  router.push({ name: 'task', params: { id: task.id } })
}

const onFilterFormSubmit = async (filters: TaskFilters) => {
  taskFilters.value = {...filters}
  if (filters.assignedTo && filters.assignedTo !== userStore.user?.id) {
    await router.replace({ query: { ...route.query, assigned: 'all', ...filters } })
  } else {
    await router.replace({ query: { ...route.query, ...filters } })
  }
  await fetchTasks()
  restoreSelectedTaskFromRoute()
  showFiltersForm.value = false
}

const onTaskFormSubmit = async (task: Task) => {
  switch (formMode.value) {
    case 'create':
      const createdTask = await postTask(task)
      await fetchTasks()
      if (createdTask) {
        selectTask(createdTask)
      }
      break
    case 'edit':
      await patchTask(task)
      await fetchTasks()
      restoreSelectedTaskFromRoute()
      break
  }
  showTaskForm.value = false
}

const restoreSelectedTaskFromRoute = () => {
  if (route.query.selected) {
    selectedTask.value = tasks.value.find(t => t.id === Number(route.query.selected))
    if (!selectedTask.value) {
      router.replace({ query: { ...route.query, selected: undefined } })
    }
  }
}

onMounted(async () => {
  taskFilters.value = {
    assignedTo: isNaN(Number(route.query.assignedTo)) ? undefined : Number(route.query.assignedTo),
    createdBy: isNaN(Number(route.query.createdBy)) ? undefined : Number(route.query.createdBy),
    deadlineGte: route.query.deadlineGte?.toString(),
    deadlineLte: route.query.deadlineLte?.toString(),
    responsibilityType: route.query.responsibilityType?.toString(),
  }
  await fetchTasks()
  restoreSelectedTaskFromRoute()
})

</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- Search Header -->
    <div class="flex gap-4 justify-end-safe items-center font-bold mb-6">
      <ButtonFilter @click="showFiltersForm = true" />
      <input v-model.trim="search" placeholder="Поиск по тексту"
        class="flex-1 font-normal input rounded-lg border-gray-500 p-4 bg-white shadow-md" />
      <select v-model="assigned" @change="fetchTasks" class="cursor-pointer px-3 py-4 rounded-lg hover:bg-gray-200">
        <option value="my">мои</option>
        <option value="all">все</option>
      </select>
      <select v-model="relevance" @change="fetchTasks" class="cursor-pointer px-3 py-4 rounded-lg hover:bg-gray-200">
        <option value="actual">актуальные</option>
        <option value="overdue">просроченные</option>
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
        <div v-if="tasks.length === 0" class="text-2xl text-center text-gray-600 p-10">Задачи не найдены</div>
        <TaskList :tasks="tasks" @select-task="selectTask" @open-task="openTaskPage" />
      </div>
      <!-- Task Card -->
      <TaskCard class="w-2/5 flex-none h-full rounded-lg shadow-md mb-1" v-if="selectedTask"
        :show-edit-button="selectedTask.status !== TaskStatusEnum.Completed" :show-details-button="true"
        :show-change-status-button="userStore.user?.id == selectedTask.assigned_to" :task="selectedTask"
        @edit="onTaskEdit" @open-details="openTaskPage(selectedTask)" @close="selectTask(undefined)"
        @change-status="(status) => changeTaskStatus(selectedTask!, status)" />
    </div>
  </div>


  <AppModal v-if="showTaskForm">
    <TaskForm :task="selectedTask" :mode="formMode" @close="showTaskForm = false" @submit="onTaskFormSubmit" />
  </AppModal>

  <AppModal v-if="showFiltersForm">
    <TaskFiltersForm :filters="taskFilters" :excludeStatus="true" @close="showFiltersForm = false" @submit="onFilterFormSubmit" />
  </AppModal>
</template>