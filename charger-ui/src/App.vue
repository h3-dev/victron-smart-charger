<script setup>
import { ref, onMounted } from 'vue'
import { BatteryMedium, PlugZap, Zap } from 'lucide-vue-next'

const status = ref({})
const forecast = ref([])
const plan = ref({})

async function load() {
  status.value = await fetch('/api/status').then(r => r.json())
  forecast.value = await fetch('/api/forecast').then(r => r.json())
  plan.value = await fetch('/api/charging-plan').then(r => r.json())
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
        <h2 class="text-2xl font-semibold text-center mb-4">Live Status</h2>
        <div class="flex justify-center space-x-4">
          <div class="flex flex-col items-center">
            <BatteryMedium class="w-6 h-6 text-gray-500 mb-1" />
            <p class="text-lg font-normal text-center">{{ status.current_soc ?? '–' }} %</p>
          </div>
          <div class="flex flex-col items-center">
            <PlugZap class="w-6 h-6 text-gray-500 mb-1" />
            <p class="text-lg font-normal text-center">{{ status.current_a ?? '–' }} A</p>
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
              <!-- Time cell with centered arrow -->
              <td class="relative px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                <Zap
                  v-if="new Date(ts).getHours() === new Date().getHours()"
                  class="absolute left-2 top-1/2 transform -translate-y-1/2 w-5 h-5 text-yellow-500"
                />
                <div class="text-center">
                  {{ new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                </div>
              </td>
              <!-- Forecast value center-aligned -->
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-700 text-center">
                {{ (Math.ceil((wh/1000)*10)/10).toFixed(1) }}
              </td>
              <!-- Charge current center-aligned -->
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
