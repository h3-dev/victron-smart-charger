<script setup>
import { ref, onMounted } from 'vue'
// SVG Icon component and MDI paths
import SvgIcon from '@jamescoyle/vue-icon'
import {
  mdiBatteryHigh,
  mdiFlagCheckered,
  mdiCurrentAc,
  mdiArrowUpDropCircleOutline,
  mdiArrowUpDropCircle,
  mdiArrowDownDropCircleOutline,
  mdiArrowDownDropCircle,
  mdiLightningBolt
} from '@mdi/js'

const status = ref({})
const forecast = ref([])
const plan = ref({})

async function load() {
  status.value = await fetch('/api/status').then(r => r.json())
  forecast.value = await fetch('/api/forecast').then(r => r.json())
  plan.value = await fetch('/api/charging-plan').then(r => r.json())
}

async function changeTarget(delta) {
  const current = status.value.target_soc ?? 0
  const newTarget = Math.max(0, Math.min(100, current + delta))
  await fetch('/api/target-soc', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_soc: newTarget })
  })
  await load()
}

onMounted(() => {
  load()
  setInterval(load, 60000)
})
</script>

<template>
  <div class="min-h-screen bg-neutral-100 text-neutral-900">
    <div class="max-w-5xl mx-auto p-6">
      <h1 class="text-4xl font-extrabold mb-8 text-center">Victron Smart Charger</h1>

      <!-- Live Status Card -->
      <div class="mb-6 rounded-2xl bg-white shadow p-6">
        <!-- Responsive layout: column on mobile, row on md+ -->
        <div class="flex flex-col space-y-6 md:flex-row md:space-y-0 md:space-x-16 justify-center">
          <!-- Current SOC -->
          <div class="flex flex-col items-center">
            <SvgIcon type="mdi" :path="mdiBatteryHigh" class="w-6 h-6 text-gray-500" />
            <span class="text-lg font-normal mt-1">{{ status.current_soc ?? '–' }} %</span>
            <span class="text-xs text-gray-500 mt-1">current soc</span>
          </div>
          <!-- Target SOC with stepper -->
          <div class="flex flex-col items-center">
            <SvgIcon type="mdi" :path="mdiFlagCheckered" class="w-6 h-6 text-gray-500" />
            <div class="flex items-center space-x-2 mt-1">
              <button @click="changeTarget(-1)" class="p-1 rounded group hover:bg-gray-200">
                <SvgIcon
                  type="mdi"
                  :path="mdiArrowDownDropCircleOutline"
                  class="w-5 h-5 text-gray-700 group-hover:hidden"
                />
                <SvgIcon
                  type="mdi"
                  :path="mdiArrowDownDropCircle"
                  class="w-5 h-5 text-gray-700 hidden group-hover:block"
                />
              </button>
              <span class="text-lg font-normal">{{ status.target_soc ?? '–' }} %</span>
              <button @click="changeTarget(1)" class="p-1 rounded group hover:bg-gray-200">
                <SvgIcon
                  type="mdi"
                  :path="mdiArrowUpDropCircleOutline"
                  class="w-5 h-5 text-gray-700 group-hover:hidden"
                />
                <SvgIcon
                  type="mdi"
                  :path="mdiArrowUpDropCircle"
                  class="w-5 h-5 text-gray-700 hidden group-hover:block"
                />
              </button>
            </div>
            <span class="text-xs text-gray-500 mt-1">target soc</span>
          </div>
          <!-- Current Charge -->
          <div class="flex flex-col items-center">
            <SvgIcon type="mdi" :path="mdiCurrentAc" class="w-6 h-6 text-gray-500" />
            <span class="text-lg font-normal mt-1">{{ status.current_a ?? '–' }} A</span>
            <span class="text-xs text-gray-500 mt-1">charge limit</span>
          </div>
        </div>
      </div>

      <!-- Combined Forecast & Charging Plan Table -->
      <div class="rounded-2xl bg-white shadow p-6 overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 table-fixed">
          <colgroup>
            <col class="w-1/3" />
            <col class="w-1/3" />
            <col class="w-1/3" />
          </colgroup>
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Forecast (kWh)</th>
              <th class="px-4 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Charge (A)</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr
              v-for="([ts, wh]) in forecast"
              :key="ts"
              :class="{ 'font-semibold': new Date(ts).getHours() === new Date().getHours() }"
              class="odd:bg-white even:bg-gray-50 hover:bg-gray-100"
            >
              <!-- Time cell with lightning icon -->
              <td class="relative px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                <SvgIcon
                  v-if="new Date(ts).getHours() === new Date().getHours()"
                  type="mdi"
                  :path="mdiLightningBolt"
                  class="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-blue-500"
                />
                <div>{{ new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</div>
              </td>
              <!-- Forecast -->
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                {{ (Math.ceil((wh/1000)*10)/10).toFixed(1) }}
              </td>
              <!-- Charge -->
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                {{ plan[ts] ?? 0 }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* optional custom styles */
</style>
