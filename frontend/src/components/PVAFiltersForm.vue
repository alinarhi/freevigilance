<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { PVAStatusEnum, MedicinalProductsApi, type MedicinalProduct } from '@/api-client';
import apiAxios from '@/axios';
import { isAxiosError } from 'axios';
import { handleAxiosError } from '@/utils/utils';
import { PVAStatusDisplay } from '@/utils/constants';

export interface PvaFilters {
    startDateGte?: string,
    startDateLte?: string,
    endDateGte?: string,
    endDateLte?: string,
    medicinalProduct?: string,
    status?: PVAStatusEnum,
}

const props = defineProps<{
    filters?: PvaFilters,
}>()

const emit = defineEmits<{
    (e: 'submit', filters: PvaFilters): void
    (e: 'close'): void
}>()

const form = ref<PvaFilters>({})

const medsApi = new MedicinalProductsApi(undefined, undefined, apiAxios)
const meds = ref<MedicinalProduct[]>([])
const fetchMeds = async () => {
    try {
        const res = await medsApi.medicinalProductsList()
        meds.value = res.data
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const reset = () => {
    form.value = {
        startDateGte: undefined,
        startDateLte: undefined,
        endDateGte: undefined,
        endDateLte: undefined,
        medicinalProduct: undefined,
        status: undefined,
    }
}


const handleSubmit = () => {
    if (form.value.startDateGte && form.value.startDateLte && new Date(form.value.startDateGte) > new Date(form.value.startDateLte)
        || form.value.endDateGte && form.value.endDateLte && new Date(form.value.endDateGte) > new Date(form.value.endDateLte)) {
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
    await fetchMeds()
})

</script>

<template>
    <form @submit.prevent="handleSubmit" class="flex flex-col gap-4 bg-white rounded-2xl shadow-md py-4 px-10">
        <h1 class="text-xl text-teal-900 font-extrabold mb-2">Фильтры</h1>

        <div class="w-1/2">
            <div class="text-gray-700 font-semibold mb-1">Статус</div>
            <select v-model="form.status"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                <option :value="undefined" selected>-- Не выбран --</option>
                <option v-for="status in Object.values(PVAStatusEnum)" :key="status" :value="status">
                    {{ PVAStatusDisplay[status] }}
                </option>
            </select>
        </div>

        <div class="w-1/2">
            <div class="text-gray-700 font-semibold mb-1">Лекарственный препарат</div>
            <select v-model="form.medicinalProduct"
                class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
                <option :value="undefined" selected> -- Не выбран -- </option>
                <option v-for="med in meds" :key="med.id" :value="med.title">
                    {{ med.title }}
                </option>
            </select>
        </div>

        <div>
            <div class="text-gray-700 font-semibold mb-1">Дата начала действия</div>
            <div class="flex items-center gap-2">
                <div>с</div>
                <input v-model="form.startDateGte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
                <div>по</div>
                <input v-model="form.startDateLte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
            </div>
        </div>

        <div>
            <div class="text-gray-700 font-semibold mb-1">Дата окончания действия</div>
            <div class="flex items-center gap-2">
                <div>с</div>
                <input v-model="form.endDateGte" type="date"
                    class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
                <div>по</div>
                <input v-model="form.endDateLte" type="date"
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