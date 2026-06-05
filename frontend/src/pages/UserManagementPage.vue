<template>
  <div
    class="main-page-wrapper"
  >
    <header class="logo-header">
      <img :src="logoUrl" alt="Suntory Oceania" class="header-logo" />
    </header>
    <div class="page-container">
      <div class="main-header">
        <div class="header-left">
          <h1 class="page-title">User Management</h1>
          <p class="page-subtitle">Add, modify, and remove user accounts and permissions</p>
        </div>
        <div class="header-right">
          <el-button :icon="ArrowLeft" class="black-icon-btn" @click="router.push('/')">Back to Main</el-button>
          <el-button :icon="Plus" class="black-icon-btn" @click="openCreate">Add User</el-button>
        </div>
      </div>

      <div class="table-card">
        <el-table
          v-loading="loading"
          :data="users"
          stripe
          border
          style="width: 100%"
          :default-sort="{ prop: 'id', order: 'descending' }"
        >
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="email" label="Email" min-width="200" />
          <el-table-column prop="display_name" label="Display Name" min-width="150" />
          <el-table-column prop="role_name" label="Role" width="160" />
          <el-table-column label="Divisions" min-width="150">
            <template #default="{ row }">{{ formatList(row.division) }}</template>
          </el-table-column>
          <el-table-column label="Countries" min-width="140">
            <template #default="{ row }">{{ formatCountry(row.country) }}</template>
          </el-table-column>
          <el-table-column label="IBP Steps" min-width="180">
            <template #default="{ row }">{{ formatList(row.ibp_steps) || 'All' }}</template>
          </el-table-column>
          <el-table-column label="Active" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
                {{ row.is_active ? 'Yes' : 'No' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="130" align="center" fixed="right">
            <template #default="{ row }">
              <el-button size="small" :icon="Edit" @click="openEdit(row)" />
              <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Add/Edit Dialog -->
      <el-dialog
        v-model="dialogOpen"
        :title="editingUser ? 'Edit User' : 'Add User'"
        width="560px"
        :close-on-click-modal="false"
        @closed="resetForm"
      >
        <el-form ref="formRef" :model="form" :rules="rules" label-width="130px" label-position="left">
          <el-form-item label="Email" prop="email">
            <el-input v-model="form.email" placeholder="user@example.com" />
          </el-form-item>
          <el-form-item label="Display Name" prop="display_name">
            <el-input v-model="form.display_name" placeholder="Full name" />
          </el-form-item>
          <el-form-item label="Role" prop="role">
            <el-select v-model="form.role" placeholder="Select role" style="width: 100%" @change="onRoleChange">
              <el-option v-for="(name, val) in ROLE_OPTIONS" :key="val" :label="`${val} – ${name}`" :value="Number(val)" />
            </el-select>
          </el-form-item>
          <el-form-item label="Role Name">
            <el-input :model-value="form.role_name" disabled />
          </el-form-item>
          <el-form-item label="Divisions">
            <el-select v-model="form.division" multiple placeholder="Select divisions" style="width: 100%">
              <div class="select-all-container">
                <el-checkbox
                  :model-value="isAllDivisionsSelected"
                  :indeterminate="form.division.length > 0 && !isAllDivisionsSelected"
                  @change="toggleAllDivisions"
                >Select All</el-checkbox>
              </div>
              <el-option v-for="d in DIVISIONS" :key="d" :label="d" :value="d" />
            </el-select>
          </el-form-item>
          <el-form-item label="Countries">
            <el-select v-model="selectedCountries" multiple placeholder="Select countries" style="width: 100%">
              <div class="select-all-container">
                <el-checkbox
                  :model-value="isAllCountriesSelected"
                  :indeterminate="selectedCountries.length > 0 && !isAllCountriesSelected"
                  @change="toggleAllCountries"
                >Select All</el-checkbox>
              </div>
              <el-option v-for="c in COUNTRY_OPTIONS" :key="c.code" :label="c.name" :value="c.code" />
            </el-select>
          </el-form-item>
          <el-form-item label="IBP Steps">
            <el-select v-model="form.ibp_steps" multiple placeholder="Leave empty for all" style="width: 100%">
              <div class="select-all-container">
                <el-checkbox
                  :model-value="isAllIbpStepsSelected"
                  :indeterminate="form.ibp_steps.length > 0 && !isAllIbpStepsSelected"
                  @change="toggleAllIbpSteps"
                >Select All</el-checkbox>
              </div>
              <el-option v-for="s in IBP_STEPS" :key="s" :label="s" :value="s" />
            </el-select>
          </el-form-item>
          <el-form-item label="Active">
            <el-switch v-model="form.is_active" />
          </el-form-item>
        </el-form>
        <template #footer>
          <div class="dialog-footer-btns">
            <el-button @click="dialogOpen = false">Cancel</el-button>
            <el-button type="primary" :loading="saving" @click="handleSave">
              {{ editingUser ? 'Save Changes' : 'Create User' }}
            </el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Edit, Delete, ArrowLeft } from '@element-plus/icons-vue';
import type { FormInstance, FormRules } from 'element-plus';
import { userApi } from '@/services/api';
import type { AppUser } from '@/types';
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import backgroundImage from "@/assets/SuntoryOceania-Patterns-RGB-Blue-Water_Ripples.png";

const router = useRouter();

const ROLE_OPTIONS: Record<number, string> = {
  0: 'Admin',
  1: 'Creator/Owner',
  2: 'IBP-Step Approver',
  3: 'Finance Approver',
  4: 'Viewer',
};

const DIVISIONS = ['Alcohol', 'Non-Alcohol'];

const COUNTRY_OPTIONS = [
  { code: '0015', name: 'Australia' },
  { code: '0014', name: 'New Zealand' },
];

const IBP_STEPS = [
  'Demand Review',
  'Supply Review',
  'Portfolio Review',
  'Finance Review',
  'Executive S&OP',
];

// ── State ──────────────────────────────────────────────────────────────────────
const users = ref<AppUser[]>([]);
const loading = ref(false);
const dialogOpen = ref(false);
const saving = ref(false);
const editingUser = ref<AppUser | null>(null);
const formRef = ref<FormInstance>();
const selectedCountries = ref<string[]>([]);

const emptyForm = () => ({
  email: '',
  display_name: '',
  role: 4,
  role_name: 'Viewer',
  division: [] as string[],
  ibp_steps: [] as string[],
  is_active: true,
});

const form = ref(emptyForm());

const rules: FormRules = {
  email: [{ required: true, message: 'Email is required', trigger: 'blur' }],
  role: [{ required: true, message: 'Role is required', trigger: 'change' }],
};

// ── Helpers ────────────────────────────────────────────────────────────────────
function formatList(val: string[] | null | undefined): string {
  if (!val || val.length === 0) return '';
  return Array.isArray(val) ? val.join(', ') : String(val);
}

function formatCountry(val: Record<string, string> | string[] | null | undefined): string {
  if (!val) return '';
  if (Array.isArray(val)) return val.join(', ');
  if (typeof val === 'object') return Object.values(val).join(', ');
  return String(val);
}

function countryArrayToMap(codes: string[]): Record<string, string> {
  const map: Record<string, string> = {};
  for (const code of codes) {
    const found = COUNTRY_OPTIONS.find(c => c.code === code);
    if (found) map[code] = found.name;
  }
  return map;
}

function countryMapToArray(val: Record<string, string> | string[] | null | undefined): string[] {
  if (!val) return [];
  if (Array.isArray(val)) return val;
  return Object.keys(val);
}

const isAllDivisionsSelected = computed(() => form.value.division.length === DIVISIONS.length);
function toggleAllDivisions() {
  if (isAllDivisionsSelected.value) form.value.division = [];
  else form.value.division = [...DIVISIONS];
}

const isAllCountriesSelected = computed(() => selectedCountries.value.length === COUNTRY_OPTIONS.length);
function toggleAllCountries() {
  if (isAllCountriesSelected.value) selectedCountries.value = [];
  else selectedCountries.value = COUNTRY_OPTIONS.map(c => c.code);
}

const isAllIbpStepsSelected = computed(() => form.value.ibp_steps.length === IBP_STEPS.length);
function toggleAllIbpSteps() {
  if (isAllIbpStepsSelected.value) form.value.ibp_steps = [];
  else form.value.ibp_steps = [...IBP_STEPS];
}

function onRoleChange(val: number) {
  form.value.role_name = ROLE_OPTIONS[val] ?? '';
}

// ── CRUD ───────────────────────────────────────────────────────────────────────
async function fetchUsers() {
  loading.value = true;
  try {
    const data = await userApi.getAll();
    users.value = data.sort((a, b) => b.id - a.id);
  } catch {
    ElMessage.error('Failed to load users');
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingUser.value = null;
  form.value = emptyForm();
  selectedCountries.value = [];
  dialogOpen.value = true;
}

function openEdit(user: AppUser) {
  editingUser.value = user;
  form.value = {
    email: user.email,
    display_name: user.display_name ?? '',
    role: user.role,
    role_name: user.role_name ?? ROLE_OPTIONS[user.role] ?? '',
    division: Array.isArray(user.division) ? [...user.division] : [],
    ibp_steps: Array.isArray(user.ibp_steps) ? [...user.ibp_steps] : [],
    is_active: user.is_active ?? true,
  };
  selectedCountries.value = countryMapToArray(user.country as Record<string, string>);
  dialogOpen.value = true;
}

function resetForm() {
  formRef.value?.clearValidate();
  editingUser.value = null;
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false);
  if (!valid) return;

  saving.value = true;
  try {
    const payload = {
      ...form.value,
      country: countryArrayToMap(selectedCountries.value),
      ibp_steps: form.value.ibp_steps.length ? form.value.ibp_steps : null,
      division: form.value.division.length ? form.value.division : null,
    };

    if (editingUser.value) {
      await userApi.update(editingUser.value.id, payload);
      ElMessage.success('User updated');
    } else {
      await userApi.create(payload as Omit<AppUser, 'id'>);
      ElMessage.success('User created');
    }
    dialogOpen.value = false;
    await fetchUsers();
  } catch {
    ElMessage.error('Failed to save user');
  } finally {
    saving.value = false;
  }
}

async function handleDelete(user: AppUser) {
  try {
    await ElMessageBox.confirm(
      `Delete user "${user.email}"? This action cannot be undone.`,
      'Confirm Delete',
      { type: 'warning', confirmButtonText: 'Delete', confirmButtonClass: 'el-button--danger' }
    );
    await userApi.delete(user.id);
    ElMessage.success('User deleted');
    await fetchUsers();
  } catch {
    // cancelled
  }
}

onMounted(fetchUsers);
</script>

<style scoped>
.main-page-wrapper {
  min-height: 100vh;
  background-size: cover;
  background-attachment: fixed;
  background-repeat: repeat;
  background-position: center;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.logo-header {
  max-width: 1600px;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.header-logo {
  height: 40px;
  width: auto;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
  flex-wrap: wrap;
  /* background: var(--bg-primary); */
  border-radius: calc(var(--radius) + 4px);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}

.header-left { flex: 1; }

.page-title {
  font-family: 'Jost', Arial, sans-serif;
  font-size: 28px;
  font-weight: 500;
  margin: 0;
  color: var(--text-title-heading);
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 4px 0 0;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.header-right :deep(.el-button) {
  color: #000;
  border-color: var(--border-color);
}

.black-icon-btn :deep(.el-icon) {
  color: #000 !important;
}

.table-card {
  background: var(--bg-primary);
  border-radius: calc(var(--radius) + 4px);
  box-shadow: var(--shadow-sm);
  padding: 16px;
  color: #000 !important;
}

:deep(.el-table-column) {
  background-color: #f8f9fc !important;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 12px;
  font-family: 'Work Sans', Arial, sans-serif;
}

.dialog-footer-btns {
  display: flex;
  gap: 12px;
  width: 100%;
}

.dialog-footer-btns :deep(.el-button) {
  flex: 1;
  margin: 0;
}

.dialog-footer-btns :deep(.el-button--primary) {
  background-color: #000;
  border-color: #000;
  color: #fff;
}

.dialog-footer-btns :deep(.el-button--primary:hover) {
  background-color: #333;
  border-color: #333;
}

.select-all-container {
  padding: 10px 20px;
  border-bottom: 1px solid #f0f2f5;
  margin-bottom: 4px;
  background-color: #fafafa;
}
</style>
