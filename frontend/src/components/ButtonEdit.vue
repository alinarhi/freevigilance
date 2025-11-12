<script setup lang="ts">
import { PencilIcon } from '@heroicons/vue/24/solid';
</script>

<template>
    <button @click="$emit('click')" title="Редактировать"
        class="cursor-pointer p-3 rounded-lg hover:bg-gray-100">
        <PencilIcon class="size-5 text-teal-600 hover:text-teal-700" />
    </button>
</template>