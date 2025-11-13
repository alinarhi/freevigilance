<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ResponsibilityTypesApi, TaskStatusEnum, UsersApi, type ResponsibilityType, type User } from '@/api-client';
import apiAxios from '@/axios';
import { isAxiosError } from 'axios';
import { handleAxiosError } from '@/utils/utils';
import { TaskStatusDisplay } from '@/utils/constants';

export interface TaskFilters {
    assignedTo?: number
    createdBy?: number
    deadlineGte?: string
    deadlineLte?: string
    responsibilityType?: string
    status?: TaskStatusEnum
}

const props = defineProps<{
    filters?: TaskFilters,
    excludeType?: boolean,
    excludeStatus?: boolean
}>()

const emit = defineEmits<{
    (e: 'submit', filters: TaskFilters): void
    (e: 'close'): void
}>()

const form = ref<TaskFilters>({})

const typesApi = new ResponsibilityTypesApi(undefined, undefined, apiAxios)
const types = ref<ResponsibilityType[]>([])
const fetchResponsibilityTypes = async () => {
    try {
        const res = await typesApi.responsibilityTypesList()
        types.value = res.data
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const usersApi = new UsersApi(undefined, undefined, apiAxios)
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

const reset = () => {
    form.value.assignedTo = undefined
    form.value.createdBy = undefined
    form.value.deadlineGte = undefined
    form.value.deadlineLte = undefined
    form.value.responsibilityType = undefined
    form.value.status = undefined
}


const handleSubmit = () => {
    if (form.value.deadlineGte && form.value.deadlineLte && new Date(form.value.deadlineGte) > new Date(form.value.deadlineLte)) {
        alert('Выбран некорректный интервал дат')
    } else {
        emit('submit', form.value)
    }
}

onMounted(async () => {
    if (props.filters) {
        form.value = {
            ...props.filters
        }
    }
    await fetchResponsibilityTypes()
    await fetchUsers()
})

</script>

<template>
    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4 bg-white rounded-2xl shadow-md py-4 px-10">
        <h1 class="text-xl text-teal-900 font-extrabold mb-2">Фильтры</h1>

        <div class="flex gap-4 items-center">
            <div v-if="!excludeType">
                <div class="text-gray-700 font-semibold mb-1">Тип обязательства</div>
                <select v-model="form.responsibilityType"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                    <option :value="undefined" selected>-- Не выбран --</option>
                    <option v-for="type in types" :key="type.id" :value="type.title">
                        {{ type.title }}
                    </option>
                </select>
            </div>

            <div v-if="!excludeStatus">
                <div class="text-gray-700 font-semibold mb-1">Статус</div>
                <select v-model="form.status"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                    <option :value="undefined" selected>-- Не выбран --</option>
                    <option v-for="status in Object.values(TaskStatusEnum)" :key="status" :value="status">
                        {{ TaskStatusDisplay[status] }}
                    </option>
                </select>
            </div>
        </div>

        <div>
            <div class="text-gray-700 font-semibold mb-1">Срок выполнения </div>
            <div class="flex items-center gap-2">
                <div>с</div>
                <input v-model="form.deadlineGte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
                <div>по</div>
                <input v-model="form.deadlineLte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
            </div>
        </div>

        <div>
            <div class="text-gray-700 font-semibold mb-1">Назначена</div>
            <select v-model="form.assignedTo"
                class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                <option :value="undefined" selected> -- Не выбран -- </option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                </option>
            </select>
        </div>


        <div>
            <div class="text-gray-700 font-semibold mb-1">Создана</div>
            <select v-model="form.createdBy"
                class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                <option :value="undefined" selected>-- Не выбран --</option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                </option>
            </select>
        </div>

        <div class="flex-none flex justify-between gap-4 font-semibold my-6">
            <div class="flex gap-4">
                <button type="submit"
                    class="cursor-pointer px-6 py-2 bg-teal-600 text-white font-bold rounded-lg shadow-md hover:bg-teal-700">
                    Применить
                </button>
                <button type="button" @click="reset" class="cursor-pointer text-gray-700">Сбросить</button>
            </div>

            <button type="button" @click="emit('close')" class="cursor-pointer text-gray-700">Отмена</button>
        </div>
    </form>
</template>