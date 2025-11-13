<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { ActionEnum, UsersApi, type User } from '@/api-client';
import apiAxios from '@/axios';
import { isAxiosError } from 'axios';
import { handleAxiosError } from '@/utils/utils';
import { ActionDisplay, ContentTypeDisplay } from '@/utils/constants';

export interface LogFilters {
    action?: ActionEnum,
    actor?: number,
    contentType?: string,
    objectId?: number,
    timestampGte?: string,
    timestampLte?: string
}

const props = defineProps<{
    filters?: LogFilters,
}>()

const emit = defineEmits<{
    (e: 'submit', filters: LogFilters): void
    (e: 'close'): void
}>()

const form = ref<LogFilters>({})

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
    form.value.action = undefined,
        form.value.actor = undefined,
        form.value.contentType = undefined,
        form.value.objectId = undefined,
        form.value.timestampGte = undefined,
        form.value.timestampLte = undefined
}


const handleSubmit = () => {
    if (form.value.timestampGte && form.value.timestampLte && new Date(form.value.timestampGte) > new Date(form.value.timestampLte)) {
        alert('Выбран некорректный интервал дат')
    } else if (form.value.objectId && !form.value.contentType) {
        alert('Не выбран тип объекта')
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
    await fetchUsers()
})

</script>

<template>
    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4 bg-white rounded-2xl shadow-md py-4 px-10">
        <h1 class="text-xl text-teal-900 font-extrabold mb-2">Фильтры</h1>

        <div class="flex gap-4">
            <div class="w-1/2">
                <div class="text-gray-700 font-semibold mb-1">Объект</div>
                <select v-model="form.contentType"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                    <option :value="undefined" selected>-- Не выбран --</option>
                    <option v-for="type in Object.keys(ContentTypeDisplay)" :key="type" :value="type">
                        {{ ContentTypeDisplay[type] }}
                    </option>
                </select>
            </div>
            <div class="w-1/2">
                <div class="text-gray-700 font-semibold mb-1">ID объекта</div>
                <input v-model="form.objectId" type="number" min="1" :disabled="!form.contentType"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
            </div>
        </div>


        <div class="flex gap-4">
            <div class="w-1/2">
                <div class="text-gray-700 font-semibold mb-1">Действие</div>
                <select v-model="form.action"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                    <option :value="undefined" selected>-- Не выбран --</option>
                    <option v-for="action in Object.values(ActionEnum)" :key="action" :value="action">
                        {{ ActionDisplay[action] }}
                    </option>
                </select>
            </div>
            <div class="w-1/2">
                <div class="text-gray-700 font-semibold mb-1">Пользователь</div>
                <select v-model="form.actor"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                    <option :value="undefined" selected> -- Не выбран -- </option>
                    <option v-for="user in users" :key="user.id" :value="user.id">
                        {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                    </option>
                </select>
            </div>
        </div>


        <div>
            <div class="text-gray-700 font-semibold mb-1">Дата</div>
            <div class="flex items-center gap-2">
                <div>с</div>
                <input v-model="form.timestampGte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
                <div>по</div>
                <input v-model="form.timestampLte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
            </div>
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