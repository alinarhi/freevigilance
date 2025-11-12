<script setup lang="ts">
import { FunnelIcon } from '@heroicons/vue/24/solid';
</script>

<template>
    <button @click="$emit('click')" title="Фильтры" class="cursor-pointer p-3 rounded-lg hover:bg-gray-200">
        <FunnelIcon class="size-7 text-teal-600 hover:text-teal-700" />
    </button>
</template>