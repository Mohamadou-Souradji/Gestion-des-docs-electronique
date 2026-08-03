<template>
  <div>
    <label style="font-weight:600;font-size:13px;display:block;margin-bottom:4px">
      Modules accessibles
    </label>
    <small style="color:#666;font-size:12px;display:block;margin-bottom:10px">
      Un utilisateur nouvellement créé n'a aucun module actif. Cochez ceux dont il a besoin.
    </small>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px">
      <label v-for="m in modulesDisponibles" :key="m.code"
        style="display:flex;align-items:flex-start;gap:8px;font-size:13px;cursor:pointer;padding:10px;border:1px solid #eee;border-radius:6px;background:#fafafa">
        <input type="checkbox" :value="m.code" :checked="modelValue.includes(m.code)"
          @change="toggle(m.code)" style="accent-color:#1565C0;width:15px;height:15px;margin-top:2px" />
        <div>
          <div style="font-weight:600"><i :class="m.icone"></i> {{ m.label }}</div>
          <div style="font-size:11px;color:#888">{{ m.description }}</div>
        </div>
      </label>
    </div>
  </div>
</template>

<script setup>
import { MODULES_DISPONIBLES } from './modulesDisponibles'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})
const emit = defineEmits(['update:modelValue'])

const modulesDisponibles = MODULES_DISPONIBLES

function toggle(code) {
  const liste = [...props.modelValue]
  const idx   = liste.indexOf(code)
  if (idx >= 0) liste.splice(idx, 1)
  else liste.push(code)
  emit('update:modelValue', liste)
}
</script>
