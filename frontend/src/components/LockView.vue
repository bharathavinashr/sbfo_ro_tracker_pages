<template>
  <el-dialog v-model="visible" title="Lock IBP Step View" width="500px" @close="handleClose">
    <p class="dialog-description">
      Create a locked snapshot of database entries filtered by IBP Step for the selected period.
    </p>
    
    <el-form :model="form" label-width="140px" class="lock-form">
      <el-form-item label="Snapshot Period">
        <div class="period-row">
          <el-select v-model="form.period" placeholder="Period" class="period-select">
            <el-option
              v-for="period in periods"
              :key="period"
              :value="period.value"
              :label="period.label"
            />
          </el-select>
          <el-select v-model="form.year" placeholder="Year" class="year-select">
            <el-option
              v-for="year in years"
              :key="year"
              :value="year"
              :label="year"
            />
          </el-select>
        </div>
        <p class="form-hint">
          This will snapshot {{ totalEntries }} {{ totalEntries === 1 ? 'entry' : 'entries' }}
        </p>
      </el-form-item>

      <el-form-item label="IBP Step" required>
        <el-select v-model="form.ibpStep" placeholder="Select IBP Step" class="full-width">
          <el-option
            v-for="step in ibpSteps"
            :key="step"
            :value="step"
            :label="step"
          />
        </el-select>
        <p v-if="form.ibpStep" class="form-hint">
          {{ filteredCount }} {{ filteredCount === 1 ? 'entry' : 'entries' }} will be locked for {{ form.ibpStep }}
        </p>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.isFinal">Mark as Final Version</el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose" :disabled="loading">Cancel</el-button>
      <el-button 
        type="primary" 
        :loading="loading" 
        :disabled="!form.period || !form.year || !form.ibpStep"
        @click="handleCreateSnapshot"
      >
        {{ loading ? 'Creating...' : 'Create Snapshot' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { ElMessage } from "element-plus";
import { snapshotApi } from "@/services/api";
import { useEntryStore } from "@/stores/entryStore";

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
}>();

const store = useEntryStore();
const visible = ref(props.modelValue);
const loading = ref(false);

const currentYear = new Date().getFullYear();
const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const periods = monthNames.map((name, index) => ({
  value: `F${String(index + 1).padStart(2, "0")}`, label: name
}));
const years = Array.from({ length: 10 }, (_, i) => (currentYear - 5 + i).toString());
const ibpSteps = ["Portfolio Review", "Supply Review", "Demand Review", "A&P (Pre-Exec)", "Overheads (Pre-Exec)"];

const form = ref({
  period: "",
  year: currentYear.toString(),
  ibpStep: "",
  isFinal: false,
});

const totalEntries = computed(() => store.displayEntries.length);

const filteredCount = computed(() => {
  if (!form.value.ibpStep) return 0;
  return store.displayEntries.filter(e => e.ibpStep === form.value.ibpStep).length;
});

watch(() => props.modelValue, (val) => {
  visible.value = val;
});

watch(visible, (val) => {
  emit("update:modelValue", val);
});

function handleClose() {
  visible.value = false;
  // Reset form on close
  form.value = { period: "", year: currentYear.toString(), ibpStep: "", isFinal: false };
}

async function handleCreateSnapshot() {
  if (!form.value.period || !form.value.year || !form.value.ibpStep) {
    ElMessage.warning("Please select period, year, and IBP Step");
    return;
  }

  loading.value = true;
  try {
    const snapshotName = `${form.value.ibpStep} - ${form.value.period} ${form.value.year}`;
    const result = await snapshotApi.create({
      period: form.value.period,
      year: form.value.year,
      ibp_step: form.value.ibpStep,
      is_final: form.value.isFinal,
    });
    ElMessage.success(`Locked view created: ${snapshotName} (${result.entries_count} entries)`);
    handleClose();
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "Failed to create snapshot");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.dialog-description {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-bottom: 20px;
  line-height: 1.5;
}

.lock-form {
  margin-top: 16px;
}

.period-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.period-select,
.year-select {
  flex: 1;
}

.full-width {
  width: 100%;
}

.form-hint {
  margin-top: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
