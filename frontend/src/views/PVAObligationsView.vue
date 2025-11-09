<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { type PVA, type Obligation, PVAStatusEnum } from '@/api-client'
import { PvasApi, ObligationsApi } from '@/api-client'
import { useRouter } from 'vue-router'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import AppModal from '@/components/AppModal.vue'
import ObligationForm from '@/components/ObligationForm.vue'

const status_types = new Map()
status_types.set(PVAStatusEnum.Active, 'Заключен')
status_types.set(PVAStatusEnum.Planned, 'Планируемый')
status_types.set(PVAStatusEnum.Ending, 'Завершающийся')
status_types.set(PVAStatusEnum.Completed, 'Завершен')

const router = useRouter()
const pvasApi = new PvasApi(undefined, undefined, apiAxios)
const obligationsApi = new ObligationsApi(undefined, undefined, apiAxios)
const ID = Number(router.currentRoute.value.params.id as string)
const pva = ref<PVA | null>(null)

const obligations = ref<Obligation[]>([])
const notFound = ref(false)
const showModal = ref(false)

const fetchData = async () => {
    try {
        const res = await pvasApi.pvasRetrieve(ID)
        pva.value = res.data
        const obligationsRes = await obligationsApi.pvasObligationsList(ID)
        obligations.value = obligationsRes.data
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

const onSubmit = async (obligation: Obligation) => {
    try {
        const res = await obligationsApi.obligationsCreate(obligation)
        if (res.status === 201) {
            alert('Обязательство успешно создано')
            showModal.value = false
            await fetchData()
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}


onMounted(() => {
    fetchData()
})
</script>

<template>
    <div v-if="notFound || !pva" class="text-2xl text-center text-gray-600 p-10">404 Договор не найден.</div>
    <div v-else class="flex h-screen gap-4">
        <!-- Left Column -->
        <div class="flex flex-col w-2/3 gap-4">
            <!-- PVA Card -->
            <div class="rounded-xl shadow-md bg-white p-4">
                <div class="font-bold">{{ pva.requisites }}</div>
                <div>{{ status_types.get(pva.status) }}</div>
                <div>Действует с {{ pva.start_date }} по {{ pva.end_date }}</div>
                <div>Ссылка на основной контракт: {{ pva.main_contract_link }}</div>
                <div>Ссылка на контракт по фармакобезопасности: {{ pva.pva_link }}</div>
                <br>
                <div class="text-gray-700">{{ pva.description }}</div>
            </div>

            <div>
                <button @click="showModal = true"
                    class="cursor-pointer bg-teal-600 text-white font-bold px-6 py-2 rounded-lg">Добавить
                    обязательство</button>
            </div>

            <!-- Obligations -->
            <div class="flex-1 overflow-y-auto p-4">
                <h2 class="text-lg font-semibold mb-2">Обязательства</h2>
                <ul class="space-y-3">
                    <li v-for="obligation in obligations" :key="obligation.id"
                        class="bg-white rounded-lg shadow-md mb-2 p-4">
                        <div>
                            <div> #{{ obligation.id }}: {{ obligation.title }}</div>
                            <div> {{ obligation.responsibility_type }}</div>
                            <div class="text-gray-700"> {{ obligation.description }}</div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>

        <AppModal v-if="showModal">
            <ObligationForm :pva_id="pva.id!" :mode="'create'" @close="showModal = false" @submit="onSubmit" />
        </AppModal>
    </div>
</template>