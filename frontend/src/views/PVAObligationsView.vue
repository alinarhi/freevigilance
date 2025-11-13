<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'

import { type PVA, type Obligation, PVAStatusEnum } from '@/api-client'
import { PvasApi, ObligationsApi } from '@/api-client'
import { useRoute, useRouter } from 'vue-router'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import AppModal from '@/components/AppModal.vue'
import PVAForm from '@/components/PVAForm.vue'
import ObligationForm from '@/components/ObligationForm.vue'
import ButtonEdit from '@/components/ButtonEdit.vue'
import ButtonFilter from '@/components/ButtonFilter.vue'
import type { ObligationFilters } from '@/components/ObligationFiltersForm.vue'
import ObligationFiltersForm from '@/components/ObligationFiltersForm.vue'

const router = useRouter()
const route = useRoute()
const pvasApi = new PvasApi(undefined, undefined, apiAxios)
const obligationsApi = new ObligationsApi(undefined, undefined, apiAxios)
const ID = Number(router.currentRoute.value.params.id as string)
const pva = ref<PVA>()

const fetchedObligations = ref<Obligation[]>([])
const notFound = ref(false)
const showObligationModal = ref(false)
const showPvaModal = ref(false)
const showFiltersForm = ref(false)
const obligationFilters = ref<ObligationFilters>({})
const search = computed({
    get: () => route.query.search ?? '',
    set: (search) => router.replace({ query: { ...route.query, search: search } })
})

const obligations = computed(() => {
    return fetchedObligations.value.filter((obligation) => {
        const matchesSearch = obligation.title.toLowerCase().includes(search.value.toString().trim().toLowerCase())
            || obligation.description?.toLowerCase().includes(search.value.toString().toLowerCase())
        return matchesSearch
    })
})

const fetchData = async () => {
    try {
        const res = await pvasApi.pvasRetrieve(ID)
        pva.value = res.data
        const obligationsRes = await obligationsApi.pvasObligationsList(ID, {
            params: {
                start_date__gte: obligationFilters.value.startDateGte,
                start_date__lte: obligationFilters.value.startDateLte,
                end_date__gte: obligationFilters.value.endDateGte,
                end_date__lte: obligationFilters.value.endDateLte,
                responsibility_type__title__iexact: obligationFilters.value.responsibilityType
            }
        })
        fetchedObligations.value = obligationsRes.data
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

const onObligationFormSubmit = async (obligation: Obligation) => {
    try {
        const res = await obligationsApi.obligationsCreate(obligation)
        if (res.status === 201) {
            alert('Обязательство успешно создано')
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

const onPvaFormSubmit = async (pva: PVA) => {
    try {
        const res = await pvasApi.pvasPartialUpdate(pva.id!, pva)
        if (res.status === 200) {
            alert('Договор успешно обновлен')
            showPvaModal.value = false
            await fetchData()
        }
    } catch (error) {
        console.error(error)
        if (isAxiosError(error)) {
            handleAxiosError(error)
        }
    }
}

const onFiltersFormSubmit = async (filters: ObligationFilters) => {
    obligationFilters.value = { ...filters }
    await router.replace({ query: { ...route.query, ...filters } })
    await fetchData()
    showFiltersForm.value = false
}

const openObligationPage = (obligation: Obligation) => {
    router.push({ name: 'obligation', params: { id: obligation.id } })
}

onMounted(async () => {
    obligationFilters.value = {
        startDateGte: route.query.startDateGte?.toString(),
        startDateLte: route.query.startDateLte?.toString(),
        endDateGte: route.query.endDateGte?.toString(),
        endDateLte: route.query.endDateLte?.toString(),
        responsibilityType: route.query.status?.toString()
    }
    await fetchData()
})
</script>

<template>
    <div v-if="notFound" class="text-2xl text-center text-gray-600 p-10">404 Договор не найден.</div>
    <!-- <div v-else v-if="pva" class="h-full w-2/3 min-w-max flex flex-col overflow-hidden wrap-anywhere gap-4"> -->
    <div v-else v-if="pva" class="h-full flex overflow-hidden wrap-anywhere gap-2">

        <!-- Obligations -->
        <div class="h-full flex-3/5 flex flex-col gap-4 m-1 py-4">
            <!-- Header -->
            <div class="flex items-center gap-2 justify-between wrap-normal text-lg font-semibold mb-4">
                <div class="text-2xl font-bold text-gray-800 px-4"> Обязательства </div>
                <ButtonFilter @click="showFiltersForm = true" />
                <input v-model="search" placeholder="Поиск по тексту"
                    class="flex-1 font-normal input rounded-lg border-gray-500 p-3 bg-white shadow-md" />
                <button @click="showObligationModal = true"
                    class="cursor-pointer bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg">Добавить</button>
            </div>
            <!-- List -->
            <!-- <div v-if="obligations.length === 0" class="text-2xl text-center text-gray-600 p-10">Обязательства не найдены</div> -->
            <div class="flex-1 overflow-y-auto">
                <ul class="space-y-3">
                    <li v-for="obligation in obligations" :key="obligation.id"
                        @dblclick="openObligationPage(obligation)"
                        class="flex text-end gap-2 cursor-pointer wrap-normal font-semibold bg-white rounded-lg shadow-md mb-2 p-4">
                        <div class="flex-1 text-start">
                            <div> {{ obligation.title }}</div>
                            <div class="text-teal-700">{{ obligation.responsibility_type }}</div>
                            <div class="text-gray-700 w-md font-normal truncate"> {{ obligation.description }}</div>
                        </div>
                        <div class="w-max">c {{ new Date(obligation.start_date).toLocaleDateString('ru-RU') }}</div>
                        <div>по {{ new Date(obligation.end_date).toLocaleDateString('ru-RU') }}</div>
                    </li>
                </ul>
            </div>
        </div>


        <!-- PVA Card -->
        <div class="flex-2/5 flex flex-col overflow-hidden rounded-xl shadow-md bg-white p-4 m-1">
            <div class="flex items-center justify-between mb-4">
                <div class="text-2xl font-bold"> {{ pva.requisites }}</div>
                <ButtonEdit @click="showPvaModal = true" />
            </div>
            <div class="text-sm text-gray-600"> ID: {{ pva.id }}</div>

            <div><span class="font-semibold">Статус: </span>{{ pva.status_display }}</div>
            <div><span class="font-semibold">Действует</span> с {{ pva.start_date ? new
                Date(pva.start_date).toLocaleDateString('ru-RU') : '_' }} по {{ pva.end_date ? new
                    Date(pva.end_date).toLocaleDateString('ru-RU') : '_' }}</div>
            <div class="max-w-2/3 truncate font-semibold">Основной контракт: <a v-if="pva.main_contract_link"
                    :title="pva.main_contract_link" :href="pva.main_contract_link">{{ pva.main_contract_link }}</a>
                <span v-else class="font-normal">не указано</span>
            </div>
            <div class="max-w-xl truncate font-semibold">Контракт по фармакобезопасности: <a v-if="pva.pva_link"
                    :href="pva.pva_link">{{ pva.pva_link }}</a><span v-else class="font-normal">не указано</span>
            </div>
            <div><span class="font-semibold">Список лекарственных препаратов: </span> {{
                pva.medicinal_products?.join(', ') }}</div>
            <br>
            <br>
            <div class="flex-1 overflow-y-auto text-gray-700 italic whitespace-pre-wrap p-1">{{ pva.description }}</div>
            <br>
        </div>


        <AppModal v-if="showObligationModal">
            <ObligationForm :pva_id="pva.id!" :mode="'create'" @close="showObligationModal = false"
                @submit="onObligationFormSubmit" />
        </AppModal>

        <AppModal v-if="showPvaModal">
            <PVAForm :pva="pva" :mode="'edit'" @close="showPvaModal = false" @submit="onPvaFormSubmit" />
        </AppModal>

        <AppModal v-if="showFiltersForm">
            <ObligationFiltersForm :filters="obligationFilters" @close="showFiltersForm = false"
                @submit="onFiltersFormSubmit" />
        </AppModal>
    </div>
</template>


<style scoped>
@reference "tailwindcss";

a {
    @apply text-teal-600 hover:text-teal-700 underline;
}
</style>