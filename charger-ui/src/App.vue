<script setup>
import { ref, onMounted } from 'vue'

const status   = ref({})
const forecast = ref([])
const plan     = ref({})

async function load() {
  status.value   = await fetch('/api/status').then(r => r.json())
  forecast.value = await fetch('/api/forecast').then(r => r.json())
  plan.value     = await fetch('/api/charging-plan').then(r => r.json())
}
onMounted(() => { load(); setInterval(load, 60_000) })
</script>

<template>
  <div class="min-h-screen bg-neutral-100 text-neutral-900">
    <div class="max-w-5xl mx-auto p-6">
      <h1 class="text-4xl font-extrabold mb-8">Victron Smart Charger</h1>

      <!-- Live Status Card -->
      <div class="mb-6 rounded-2xl bg-white shadow p-6">
        <h2 class="text-2xl font-semibold mb-4">Live Status</h2>
        <div class="flex space-x-8">
          <div>
            <p class="text-sm text-neutral-500">SOC</p>
            <p class="text-3xl font-bold">{{ status.soc ?? '–' }} %</p>
          </div>
          <div>
            <p class="text-sm text-neutral-500">Current</p>
            <p class="text-3xl font-bold">{{ status.current_a ?? '–' }} A</p>
          </div>
        </div>
      </div>

      <div class="grid gap-6 md:grid-cols-2">
        <!-- Forecast Card -->
        <div class="rounded-2xl bg-white shadow p-6">
          <h2 class="text-2xl font-semibold mb-4">PV Forecast (Wh)</h2>
          <table class="w-full text-left">
            <thead>
              <tr class="border-b">
                <th class="py-2">Time</th><th class="py-2">Yield</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="[ts,wh] in forecast" :key="ts" class="hover:bg-neutral-50">
                <td class="py-1">{{ new Date(ts).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) }}</td>
                <td class="py-1 text-right font-medium">{{ wh }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Charging Plan Card -->
        <div class="rounded-2xl bg-white shadow p-6">
          <h2 class="text-2xl font-semibold mb-4">Charging Plan (A)</h2>
          <table class="w-full text-left">
            <thead>
              <tr class="border-b">
                <th class="py-2">Time</th><th class="py-2">Ampere</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(amp,ts) in plan" :key="ts" class="hover:bg-neutral-50">
                <td class="py-1">{{ new Date(ts).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) }}</td>
                <td class="py-1 text-right font-medium">{{ amp }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
