<script setup lang="ts">
import apiAxios from '@/axios'
import { AuditlogApi, type LogEntry } from '@/api-client'
import { onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import { ActionDisplay } from '@/utils/constants'
import LogEntryCard from '@/components/LogEntryCard.vue'

const logsApi = new AuditlogApi(undefined, undefined, apiAxios)
const logs = ref<LogEntry[]>([])

const fetchLogs = async () => {
  try {
    const res = await logsApi.auditlogList()
    logs.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

onMounted(async () => {
  await fetchLogs()
})
</script>

<template>
  <div class="h-full overflow-y-auto wrap-anywhere">
    <ul class="divide-y divide-gray-300">
      <li v-for="log in logs" :key="log.id" class="p-2">
        <LogEntryCard :log="log" :showType="true" />
      </li>
    </ul>
  </div>

</template>