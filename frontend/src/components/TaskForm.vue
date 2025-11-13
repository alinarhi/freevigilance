<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import type { Task, Obligation, PVA, User, TaskSchedule } from '@/api-client'
import { FrequencyTypeEnum, TaskStatusEnum, UsersApi, ObligationsApi, PvasApi } from '@/api-client'
import { FrequencyTypeDisplay, TaskStatusDisplay } from '@/utils/constants'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

export type TaskFormMode = 'create' | 'edit'
const usersApi = new UsersApi(undefined, undefined, apiAxios)
const obligationsApi = new ObligationsApi(undefined, undefined, apiAxios)
const pvasApi = new PvasApi(undefined, undefined, apiAxios)

const props = defineProps<{
  mode: TaskFormMode
  task?: Task,
  obligationId?: number
}>()

const emit = defineEmits<{
  (e: 'submit', data: Task): void
  (e: 'close'): void
}>()

const localDeadline = ref<string>('')
const pvaID = ref<number | undefined>()
const includePvaObligation = ref(true)

const form = ref<Task>({
  title: '',
  deadline: '',
  obligation: 0,
  description: '',
  status: TaskStatusEnum.NotStarted,
  is_recurring: false,
  assigned_to: undefined,
  schedule: {
    frequency_type: undefined,
    start_date: new Date().toISOString().slice(0, 10),
    end_date: ''
  }
})

const users = ref<User[]>([])
const fetchUsers = async () => {
  try {
    const res = await usersApi.usersList()
    users.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const obligations = ref<Obligation[]>([])
const fetchObligations = async (id: number) => {
  try {
    const res = await obligationsApi.pvasObligationsList(id)
    obligations.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const pvas = ref<PVA[]>([])
const fetchPvas = async () => {
  try {
    const res = await pvasApi.pvasList()
    pvas.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

watch(localDeadline, (newValue) => {
  if (newValue) {
    form.value.deadline = new Date(newValue).toISOString()
  }
})

const handleSubmit = () => {
  if (!form.value.is_recurring) {
    form.value.schedule = undefined
  } else if (new Date(form.value.schedule!.end_date) <= new Date(form.value.deadline)) {
    alert('Дата окончания повторения не может быть раньше срока выполнения')
    return
  }
  console.log('Task Form Submit', form.value)
  emit('submit', form.value)
}

onMounted(async () => {
  if (props.task) {
    const deadlineDate = new Date(props.task.deadline)
    localDeadline.value = new Date(deadlineDate.getTime() - deadlineDate.getTimezoneOffset() * 60000).toISOString().slice(0, 16)

    form.value = {
      ...props.task,
    }
    if (!props.task.schedule) {
      form.value.schedule = {
        frequency_type: undefined,
        start_date: new Date().toISOString().slice(0, 10),
        end_date: ''
      }
    }
  }
  if (props.obligationId) {
    form.value.obligation = props.obligationId
    includePvaObligation.value = false
  }
  if (props.mode === 'edit') {
    includePvaObligation.value = false
  }
  await fetchUsers()
  if (includePvaObligation.value) {
    await fetchPvas()
  }
})
</script>

<template>
  <form @submit.prevent="handleSubmit" class="h-full overflow-hidden flex flex-col p-6 bg-white rounded-2xl shadow-md">
    <div class="flex-none text-xl mb-4 font-extrabold text-teal-900">{{ mode === 'create' ? 'Создание' :
      'Редактирование'
    }} задачи</div>

    <div class="flex-1 space-y-6 overflow-y-auto">
      <div v-if="includePvaObligation">
        <label class="block mb-1 font-semibold text-gray-700">Договор</label>
        <div class="flex gap-4 items-center">
          <div class="flex-1">
            <select v-model="pvaID" @change="fetchObligations(pvaID!)"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
              required>
              <option value="" disabled selected>Выберите договор</option>
              <option v-for="pva in pvas" :key="pva.id" :value="pva.id">
                {{ pva.requisites }} (#{{ pva.id }})
              </option>
            </select>
          </div>
          <!-- <div class="flex-none">
            <button type="button" class="cursor-pointer font-semibold text-teal-700">
              Добавить
            </button>
          </div> -->
        </div>
      </div>

      <div v-if="includePvaObligation">
        <label class="block mb-1 font-semibold text-gray-700">Обязательство</label>
        <div class="flex gap-4 items-center">
          <div class="flex-1">
            <select v-model="form.obligation" :disabled="!pvaID"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
              required>
              <option value="" disabled selected>Выберите обязательство</option>
              <option v-for="obligation in obligations" :key="obligation.id" :value="obligation.id">
                {{ obligation.title }} (#{{ obligation.id }})
              </option>
            </select>
          </div>
          <!-- <div class="flex-none">
            <button type="button" class="cursor-pointer font-semibold text-teal-700">
              Добавить
            </button>
          </div> -->
        </div>
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Название</label>
        <input v-model="form.title" type="text"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          required />
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Описание</label>
        <textarea v-model="form.description"
          class="resize-none w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          rows="5" />
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Срок выполнения</label>
        <input v-model="localDeadline" type="datetime-local"
          class="w-fit border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          required />
      </div>

      <div class="flex justify-stretch items-center gap-2">
        <div class="flex items-center gap-2">
          <label for="recurring" class="text-gray-700">Повторять</label>
          <input v-model="form.is_recurring" type="checkbox" id="recurring"
            class="rounded border-gray-300 focus:ring-blue-300" />
        </div>

        <div v-if="form.is_recurring">
          <select v-model="form.schedule!.frequency_type"
            class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
            required>
            <option value="">Выберите тип повторения</option>
            <option v-for="type in Object.values(FrequencyTypeEnum)" :key="type" :value="type">
              {{ FrequencyTypeDisplay[type] }}
            </option>
          </select>
        </div>

        <label v-if="form.is_recurring" class="text-gray-700">до:</label>

        <div v-if="form.is_recurring">
          <input v-model="form.schedule!.end_date" type="date"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
            required />
        </div>
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Назначена</label>
        <select v-model="form.assigned_to"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
          <option value="">Выберите исполнителя</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.last_name }} {{ user.first_name }} ({{ user.username }})
          </option>
        </select>
      </div>

    </div>


    <div class="flex-none flex gap-4 font-semibold my-6">
      <button type="submit"
        class="cursor-pointer px-6 py-2 bg-teal-600 text-white font-bold rounded-lg shadow-md hover:bg-teal-700">
        Сохранить
      </button>
      <button @click="emit('close')" class="cursor-pointer text-gray-700">Отмена</button>
    </div>
  </form>
</template>