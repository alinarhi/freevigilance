<script setup lang="ts">
import apiAxios from '@/axios'
import { ActionEnum, AuditlogApi, type LogEntry } from '@/api-client'
import { onMounted, ref, computed } from 'vue'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import LogEntryCard from '@/components/LogEntryCard.vue'
import ButtonFilter from '@/components/ButtonFilter.vue'
import { useRoute, useRouter } from 'vue-router'
import type { LogFilters } from '@/components/LogFiltersForm.vue'
import LogFiltersForm from '@/components/LogFiltersForm.vue'
import AppModal from '@/components/AppModal.vue'

const router = useRouter()
const route = useRoute()
const logsApi = new AuditlogApi(undefined, undefined, apiAxios)
const logs = ref<LogEntry[]>([])
const showFiltersForm = ref(false)
const logFilters = ref<LogFilters>()


const fetchLogs = async () => {
  try {
    const res = await logsApi.auditlogList(
      logFilters.value?.action,
      logFilters.value?.actor,
      undefined,
      undefined,
      logFilters.value?.contentType,
      logFilters.value?.objectId,
      logFilters.value?.timestampGte,
      logFilters.value?.timestampLte
    )
    logs.value = res.data.filter(log => log.content_type != 'user' && log.content_type != 'session')
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const onFiltersFormSubmit = async (filters: LogFilters) => {
  logFilters.value = { ...filters }
  await router.replace({ query: { ...route.query, ...filters } })
  await fetchLogs()
  showFiltersForm.value = false
}

onMounted(async () => {
  logFilters.value = {
    action: isNaN(Number(route.query.action)) ? undefined : Number(route.query.action) as ActionEnum,
    actor: isNaN(Number(route.query.actor)) ? undefined : Number(route.query.actor),
    contentType: route.query.contentType?.toString(),
    objectId: isNaN(Number(route.query.objectId)) ? undefined : Number(route.query.objectId),
    timestampGte: route.query.timestampGte?.toString(),
    timestampLte: route.query.timestampLte?.toString(),
  }
  console.log(logFilters.value)
  await fetchLogs()
})
</script>

<template>
  <div class="flex items-center gap-4 mb-6">
    <ButtonFilter @click="showFiltersForm = true" />
    <div class="text-2xl text-gray-800 font-bold">Журнал действий</div>
  </div>
  <div v-if="logs.length === 0" class="text-2xl text-center text-gray-600 p-10">Записи не найдены</div>
  <div v-else class="h-full overflow-y-auto wrap-anywhere">
    <ul class="divide-y divide-gray-300 mb-10">
      <li v-for="log in logs" :key="log.id" class="p-2">
        <LogEntryCard :log="log" :showType="true" />
      </li>
    </ul>
  </div>

  <AppModal v-if="showFiltersForm">
    <LogFiltersForm :filters="logFilters" @close="showFiltersForm = false" @submit="onFiltersFormSubmit" />
  </AppModal>
</template>