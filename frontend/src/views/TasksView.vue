<script setup lang="ts">
import { TasksApi, UsersApi, type Task, type User, TaskStatusEnum } from '@/api-client'
import apiAxios from '@/axios'
import { ref, computed, onMounted, watch } from 'vue'
import TaskCard from '@/components/TaskCard.vue'
import TaskForm from '@/components/TaskForm.vue'
import type { TaskFormMode } from '@/components/TaskForm.vue'
import TaskList from '@/components/TaskList.vue'
import { useUserStore } from '@/stores/user'
import { AxiosError, isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import router from '@/router'

const userStore = useUserStore()
const taskApi = new TasksApi(undefined, undefined, apiAxios)

const fetchedTasks = ref<Task[]>([])
const search = ref('')

const myAllOption = ref<'my' | 'all'>('my')
const actualArchivedOption = ref<'actual' | 'completed'>('actual')

const selectedTask = ref<Task | null>(null)
const showModal = ref(false)
const formMode = ref<TaskFormMode>('create')

const fetchTasks = async () => {
  try {
    if (myAllOption.value === 'my' && actualArchivedOption.value === 'actual') {
      fetchedTasks.value = (await taskApi.tasksMyList()).data
    } else if (myAllOption.value === 'my' && actualArchivedOption.value === 'completed') {
      fetchedTasks.value = (await taskApi.tasksMyCompletedList()).data
    } else if (myAllOption.value === 'all' && actualArchivedOption.value === 'actual') {
      fetchedTasks.value = (await taskApi.tasksList()).data.filter((task) => {
        return task.status !== TaskStatusEnum.Completed
      })
    } else if (myAllOption.value === 'all' && actualArchivedOption.value === 'completed') {
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
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

onMounted(fetchTasks)


const filteredTasks = computed(() => {
  return fetchedTasks.value.filter((task) => {
    const matchesSearch = task.title.toLowerCase().includes(search.value.trim().toLowerCase())
      || task.description?.toLowerCase().includes(search.value.toLowerCase())
    return matchesSearch
  })
})

const onTaskSelected = (task: Task) => {
  if (!selectedTask.value) {
    selectedTask.value = task
  } else {
    selectedTask.value = null
  }
}

const onCreate = () => {
  selectedTask.value = null
  showModal.value = true
  formMode.value = 'create'
}

const onEdit = () => {
  if (selectedTask.value) {
    showModal.value = true
    formMode.value = 'edit'
  }
}

const onDetails = () => {
  if (selectedTask.value) {
    router.push({ name: 'task', params: { id: selectedTask.value.id } })
    // showModal.value = true
    // formMode.value = 'readonly'
  }
}

const onSubmit = async (task: Task) => {
  switch (formMode.value) {
    case 'create':
      await postTask(task)
      await fetchTasks()
      break
    case 'edit':
      await patchTask(task)
      await fetchTasks()
      break
    case 'readonly':
      break
  }
  selectedTask.value = null
  showModal.value = false
}


</script>

<template>
  <div class="flex gap-4 max-w-screen justify-stretch">
    <div class="flex-3/5">
      <!-- Header -->
      <div class="flex gap-4 justify-end-safe items-center font-bold mb-6">
        <input v-model="search" placeholder="Поиск по тексту"
          class="flex-1 font-normal input rounded-lg border-gray-500 p-4 bg-white shadow-md" />
        <select v-model="myAllOption" @change="fetchTasks" class="flex-none cursor-pointer p-2">
          <option value="my">мои</option>
          <option value="all">все</option>
        </select>
        <select v-model="actualArchivedOption" @change="fetchTasks" class="flex-none cursor-pointer p-2">
          <option value="actual">актуальные</option>
          <option value="completed">завершенные</option>
        </select>
        <button @click="onCreate"
          class="cursor-pointer text-white bg-teal-600 shadow-md rounded-lg py-2 px-10 font-bold hover:bg-teal-700">
          Создать
        </button>
      </div>
      <!-- Task List -->
      <div v-if="filteredTasks.length == 0" class="text-2xl text-center text-gray-600 p-10">Задачи не найдены</div>
      <TaskList class="flex-3/5" :tasks="filteredTasks" @select-task="onTaskSelected" />
    </div>

    <TaskCard class="flex-2/5 h-fit rounded-lg shadow-md" v-if="selectedTask" :show-buttons="true" :task="selectedTask"
    @close="selectedTask = null"
    @edit="onEdit"
    @details="onDetails" />
  </div>

  <Teleport to="body" v-if="showModal">
    <div class="overlay">
      <div class="modal">
        <TaskForm :task="selectedTask" :mode="formMode" @close="showModal = false" @submit="onSubmit" />
      </div>
    </div>
  </Teleport>
</template>


<style scoped>
.overlay {
  position: fixed;
  z-index: 998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
}

.modal {
  position: fixed;
  z-index: 999;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  /* height: 80%; */
  max-height: min-content;
  min-width: min-content;
  width: 40%;
}
</style>