<script setup>
import { ref, onMounted } from 'vue'
import { BatteryMedium, PlugZap } from 'lucide-vue-next'

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
      <h1 class="text-4xl font-extrabold mb-8">Victron Smart Charger</h1>

      <!-- Live Status Card -->
      <div class="mb-6 rounded-2xl bg-white shadow p-6">
        <h2 class="text-2xl font-semibold text-center mb-4">Live Status</h2>
        <div class="flex justify-center space-x-5">
          <div class="flex flex-col items-center">
            <BatteryMedium class="w-6 h-6 text-gray-500 mb-1" />
            <p class="text-lg font-normal">{{ status.soc ?? '–' }} %</p>
          </div>
          <div class="flex flex-col items-center">
            <PlugZap class="w-6 h-6 text-gray-500 mb-1" />
            <p class="text-lg font-normal">{{ status.current_a ?? '–' }} A</p>
          </div>
        </div>
      </div>

      <div class="grid gap-6 md:grid-cols-2">
        <!-- Forecast Card -->
        <div class="rounded-2xl bg-white shadow p-6 overflow-x-auto">
          <h2 class="text-xl font-semibold mb-4">PV Forecast (Wh)</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  <th class="px-4 py-2 text-left pl-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Yield</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="[ts, wh] in forecast" :key="ts" class="odd:bg-white even:bg-gray-50 hover:bg-gray-100">
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{{ new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm font-normal text-gray-900 text-left pl-4">{{ wh }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Charging Plan Card -->
        <div class="rounded-2xl bg-white shadow p-6 overflow-x-auto">
          <h2 class="text-xl font-semibold mb-4">Charging Plan (A)</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  <th class="px-4 py-2 text-left pl-4 text-xs font-medium text-gray-500 uppercase tracking-wider">Ampere</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-100">
                <tr v-for="(amp, ts) in plan" :key="ts" class="odd:bg-white even:bg-gray-50 hover:bg-gray-100">
                  <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{{ new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</td>
                  <td class="px-4 py-3 whitespace-nowrap text-sm font-normal text-gray-900 text-left pl-4">{{ amp }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* optional custom styles */
</style>
