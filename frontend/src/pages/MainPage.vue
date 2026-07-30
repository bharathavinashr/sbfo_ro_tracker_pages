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
        <div class="title-with-logo">
          <h1 class="page-title">Risk and Opportunities Tracker</h1>
        </div>
        <p class="page-subtitle">
          Create and manage Risks and Opportunities with comprehensive filtering capabilities
        </p>
      </div>
      <div class="header-right">
        <div class="role-switcher">
          <el-icon class="role-icon"><User /></el-icon>
          <div class="role-meta">
            <span class="role-label">User Type</span>
            <el-select
              key="local-dropdown"
              v-if="authMode === 'LOCAL'"
              v-model="store.currentUser"
              class="role-picker"
              size="default"
              value-key="id"
              placeholder="Select user email"
              clearable
            >
              <el-option
                v-for="u in store.users"
                :key="u.id"
                :value="u"
                :label="u.email"
              >
                <span>{{ u.email }}</span>
                <span class="user-role-tag">{{ ROLE_MAP[u.role] }}</span>
              </el-option>
            </el-select>
            <template v-else-if="authMode === 'DBX' && dbxAdminUser && Number(dbxAdminUser.role) === 0">
              <span class="role-email">{{ dbxAdminUser.email }}</span>
              <el-select
                key="dbx-dropdown"
                v-model="store.currentUser"
                class="role-picker"
                size="default"
                value-key="id"
                placeholder="Test as..."
                clearable
                style="margin-left: 8px;"
                @clear="store.currentUser = dbxAdminUser"
              >
                <el-option
                  v-for="u in impersonationUsers"
                  :key="u.id"
                  :value="u"
                  :label="u.email"
                >
                  <span>{{ u.email }}</span>
                  <span class="user-role-tag">{{ ROLE_MAP[u.role] }}</span>
                </el-option>
              </el-select>
            </template>
            <span v-else class="role-email">
              {{ store.currentUser?.email ?? "Resolving identity..." }}
            </span>
          </div>
        </div>

        <el-button
          v-if="[0, 2, 3].includes(Number(store.currentUser?.role)) || Number(dbxAdminUser?.role) === 0"
          :icon="Camera"
          class="black-icon-btn"
          @click="lockViewOpen = true"
        >
          Generate Snapshot
        </el-button>

        <el-button
          :icon="Search"
          class="black-icon-btn"
          @click="router.push('/snapshots')"
        >
          Browse Snapshots
        </el-button>

        <el-button
          v-if="Number(store.currentUser?.role) === 0 || Number(dbxAdminUser?.role) === 0"
          :icon="Setting"
          class="black-icon-btn"
          @click="router.push('/users')"
        >
          Manage Users
        </el-button>
      </div>
    </div>

    <EntriesTable
      :entries="store.displayEntries"
      :can-approve="store.canApprove"
      @add="openCreate"
      @edit="openEdit"
      @duplicate="openDuplicate"
      @delete="handleDelete"
      @history="goToHistory"
      @approve="handleApprove"
    />

    <el-dialog
      v-model="formOpen"
      width="90%"
      text-align="center"
      :close-on-click-modal="false"
      @closed="editingEntry = null"
    >
      <EntryForm :key="formKey" ref="formRef" :entry="editingEntry" />
      <template #footer>
        <div class="dialog-footer-btns">
          <el-button @click="formOpen = false">Cancel</el-button>
          <el-button type="primary" :loading="saving" @click="handleSave">
            {{ editingEntry ? "Save Changes" : "Create Entry" }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <LockView v-model="lockViewOpen" />

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, User, Camera, Search, Setting } from "@element-plus/icons-vue";
import { useEntryStore } from "@/stores/entryStore";
import { authApi, entryApi } from "@/services/api";
import EntriesTable from "@/components/EntriesTable.vue";
import EntryForm from "@/components/EntryForm.vue";
import LockView from "@/components/LockView.vue";
import type { Entry } from "@/types";
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import { ROLE_MAP } from "@/types";

const router = useRouter();
const store = useEntryStore();

const impersonationUsers = computed(() => {
  return store.users.filter(u => {
    const email = u.email?.toLowerCase().trim() || "";
    const isNotInternal = !['@suntory.com', '@beamsuntory.com'].some(domain => email.endsWith(domain));
    return isNotInternal;
  });
});

const formOpen = ref(false);
const editingEntry = ref<Entry | null>(null);
const saving = ref(false);
const formRef = ref<InstanceType<typeof EntryForm> | null>(null);
const authMode = ref<"LOCAL" | "DBX" | "">("");
const dbxAdminUser = ref<import("@/types").AppUser | null>(null);
const lockViewOpen = ref(false);
const formKey = ref(0);

onMounted(async () => {
  try {
    const { auth_mode } = await authApi.getConfig();
    authMode.value = auth_mode;
  } catch {
    authMode.value = "LOCAL";
  }
  if (authMode.value === "DBX") {
    try {
      const me = await authApi.getMe();
      store.currentUser = me;
      if (Number(me.role) === 0) {
        dbxAdminUser.value = me;
        await store.fetchUsers();
      }
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      ElMessage.error(msg ?? "Your account is not registered. Please contact your administrator.");
    }
  } else {
    await store.fetchUsers();
  }
  store.fetchEntries();
});

watch(() => store.currentUser, () => { store.fetchEntries(); });

function openCreate() {
  editingEntry.value = null;
  formKey.value++; 
  formOpen.value = true;
}

function openEdit(entry: Entry) {
  editingEntry.value = { ...entry };
  formOpen.value = true;
}

function openDuplicate(entry: Entry) {
  editingEntry.value = null;
  formOpen.value = true;
  setTimeout(() => {
    const hasChildren = entry.childImpacts && entry.childImpacts.length > 0;
    const copy = {
      ...entry,
      id: 0,
      version: 0,
      originalEntryId: undefined,
      status: "Open",
      ...(hasChildren ? { impactPeriod: undefined, impactYear: undefined, impactValue: undefined, secondaryValue: undefined } : {}),
    };
    editingEntry.value = copy;
  }, 10);
}

async function handleSave() {
  if (!formRef.value) return;
  const data = await formRef.value.validate();
  if (!data) return;

  saving.value = true;
  try {
    const payload = {
      creation_date: editingEntry.value?.creationDate ?? new Date().toISOString().slice(0, 10),
      creation_date_period: data.creationDatePeriod,
      creation_date_year: data.creationDateYear,
      add_to_forecast_by_period: data.addToForecastByPeriod,
      add_to_forecast_by_year: data.addToForecastByYear,
      division: data.division,
      ibp_step: data.ibpStep,
      country: data.country,
      channel: data.channel,
      sub_channel: data.subChannel,
      account: data.account,
      brand: data.brand,
      brand_family: data.brandFamily,
      r_and_o: data.rAndO,
      probability: data.probability,
      categorisation: data.categorisation,
      impact_period: data.impactPeriod,
      impact_year: data.impactYear,
      nsv_aud: data.nsvAud,
      nsv_nzd: data.nsvNzd,
      volume_litres: data.volumeLitres,
      primary_impact: data.primaryImpact,
      owner: data.owner,
      creator: data.creator,
      modified_user: store.currentUser?.email ?? null,
      status: data.status,
      short_description: data.shortDescription,
      description: data.detailedDescription,          
      financial_impact_type: data.financialImpactType,
      volume_cases: (data as any).volumeCases ?? null, 
      volume_impact_type: data.volumeImpactType,
      volume_impact_value: (data as any).volumeImpactValue,
      
      // NEW FIELDS mapped here
      fixed_nsv_gp_ratio: (data as any).fixedNsvGpRatio ?? null,
      fixed_nsv_vol_ratio: (data as any).fixedNsvVolRatio ?? null,
      net_financial_impact_value: (data as any).netFinancialImpactValue ?? null,

      child_impacts: data.childImpacts.map((ci: any) => ({
        impact_year: ci.impactYear,
        impact_period: ci.impactPeriod,
        nsv_aud: ci.nsvAud,
        nsv_nzd: ci.nsvNzd,
        volume_litres: ci.volumeLitres,
        volume_cases: ci.volumeCases ?? null,
        volume_impact_value: ci.volumeImpactValue,
        gp_aud: ci.gp_aud ?? null,
        gp_nzd: ci.gp_nzd ?? null,
      })),
    };

    if (editingEntry.value && editingEntry.value.id) {
      await store.updateEntry(editingEntry.value.id, payload as unknown as Partial<Entry>);
      ElMessage.success("Entry updated");
    } else {
      await store.createEntry(payload as unknown as Partial<Entry>);
      ElMessage.success("Entry created");
    }
    formOpen.value = false;
  } catch {
    ElMessage.error("Failed to save entry");
  } finally {
    saving.value = false;
  }
}

async function handleDelete(entry: Entry) {
  try {
    await ElMessageBox.confirm(
      "This will delete all versions of this entry. Continue?",
      "Confirm Delete",
      { type: "warning", confirmButtonText: "Delete", confirmButtonClass: "el-button--danger" }
    );
    await store.deleteEntry(entry.id);
    ElMessage.success("Entry deleted");
  } catch {
  }
}

async function handleApprove(entry: Entry) {
  try {
    const { status: latestStatus } = await entryApi.getStatus(entry.id);
    if (latestStatus !== entry.status) {
      ElMessage.warning(`This entry's status has changed to "${latestStatus}". Please review the latest state.`);
      await store.fetchEntries();
      return;
    }
    await store.approveEntry(entry.id, store.currentUser?.email);
    ElMessage.success("Entry approved");
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
  }
}

function goToHistory(entry: Entry) {
  router.push(`/entry/${entry.originalEntryId ?? entry.id}/history`);
}
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
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 24px;
}

.logo-header {
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2px;
  gap: 16px;
  flex-wrap: wrap;
  background: rgba(255, 255, 255, 0.5);
  border-radius: calc(var(--radius) + 4px);
  box-shadow: var(--shadow-sm);
  padding: 20px;
}

.header-left {
  flex: 1;
  min-width: 320px;
}

.title-with-logo {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.header-logo {
  height: 40px;
  width: auto;
}

.page-title {
  font-family: 'Jost', Arial, sans-serif;
  font-size: 28px;
  font-weight: 500;
  margin: 0;
  color: var(--text-title-heading);
  line-height: 1.2;
}

.page-subtitle {
  font-family: 'Work Sans', Arial, sans-serif;
  font-weight: 400;
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}

.header-right {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: flex-end;
  flex-wrap: nowrap;
  justify-content: flex-start;
}

.role-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
}

.role-icon {
  color: var(--text-muted);
}

.role-meta {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.role-label {
  font-size: 11px;
  line-height: 1;
  color: var(--text-muted);
}

.role-picker {
  width: 220px;
}

.user-role-tag {
  float: right;
  font-size: 11px;
  color: var(--text-muted);
  margin-left: 8px;
}

.role-email {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  padding: 0 4px;
}

.header-right :deep(.el-button) {
  width: 200px;
  color: #000;
  border-color: var(--border-color);
}

.black-icon-btn :deep(.el-icon) {
  color: #000 !important;
}

@media (max-width: 768px) {
  .main-header {
    align-items: flex-start;
    padding: 16px;
  }

  .page-title {
    font-size: 22px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
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

.dialog-footer-btns :deep(.el-button) {
  background-color: #000;
  border-color: #000;
  color: #fff;
}

.dialog-footer-btns :deep(.el-button:hover) {
  background-color: #333;
  border-color: #333;
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
</style>