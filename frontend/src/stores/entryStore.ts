import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { entryApi, userApi } from "@/services/api";
import type { Entry, AppUser } from "@/types";
import { ROLE_MAP } from "@/types";

export const useEntryStore = defineStore("entry", () => {
  const entries = ref<Entry[]>([]);
  const loading = ref(false);
  const users = ref<AppUser[]>([]);
  const currentUser = ref<AppUser | null>(null);

  const userRole = computed(() =>
    currentUser.value != null ? ROLE_MAP[currentUser.value.role] ?? "User" : "User"
  );

  const filters = ref({
    division: [] as string[],
    department: "",
    country: [] as string[],
    channel: [] as string[],
    sub_channel: [] as string[],
    account: [] as string[],
    brand: "",
    brand_family: "",
    categorisation: "",
    r_and_o: "",
    probability: "",
    status: [] as string[],
    owner: "",
    ibp_step: [] as string[],
    creation_date_period: "",
    creation_date_year: "",
  });

  const displayEntries = computed(() => {
    const email = currentUser.value?.email ?? "";
    const isUser = userRole.value === "User";
    return entries.value
      .filter((e) => !isUser || e.owner === email || e.creator === email)
      .map((e) => ({
        ...e,
        customer: [
          Array.isArray(e.channel) ? e.channel.join(", ") : (e.channel && typeof e.channel === 'object' ? Object.values(e.channel).join(", ") : e.channel),
          Array.isArray(e.subChannel) ? e.subChannel.join(", ") : (e.subChannel && typeof e.subChannel === 'object' ? Object.values(e.subChannel).join(", ") : e.subChannel),
          Array.isArray(e.account) ? e.account.join(", ") : (e.account && typeof e.account === 'object' ? Object.values(e.account).join(", ") : e.account),
        ].filter(Boolean).join(" / "),
        product: [
          e.brand && typeof e.brand === 'object' ? Object.values(e.brand).join(", ") : e.brand,
          e.brandFamily && typeof e.brandFamily === 'object' ? Object.values(e.brandFamily).join(", ") : e.brandFamily,
        ]
          .filter(Boolean)
          .join(" - "),
      }));
  });

  const canCreate = computed(() =>
    ["User", "IBP Step Approver", "System Admin"].includes(userRole.value)
  );
  const canApprove = computed(() =>
    ["IBP Step Approver", "Finance Approver", "System Admin"].includes(userRole.value)
  );

  async function fetchUsers() {
    users.value = await userApi.getAll();
  }

  function normalizeCountryCode(code: string | number): string {
    const value = String(code).trim();
    const stripped = value.replace(/^0+/, "");
    return stripped.length > 0 ? stripped : value;
  }

  async function fetchEntries() {
    loading.value = true;
    try {
      const activeFilters: any = Object.fromEntries(
        Object.entries(filters.value).filter(([, v]) => {
          if (Array.isArray(v)) return v.length > 0;
          return v !== "";
        })
      );
      if (Array.isArray(activeFilters.country)) {
        activeFilters.country = activeFilters.country.map(normalizeCountryCode);
      }
      if (userRole.value) activeFilters.role = userRole.value;
      // Pass department restriction for IBP Step Approver (null = all, array = restricted)
      if (userRole.value === "IBP Step Approver") {
        const depts = currentUser.value?.ibp_steps;
        if (depts && depts.length > 0) {
          activeFilters.user_departments = depts.join(",");
        }
      }
      const data = await entryApi.getAll(activeFilters);
      entries.value = data.entries;
    } finally {
      loading.value = false;
    }
  }

  async function createEntry(data: Partial<Entry> & { childImpacts?: unknown[] }) {
    await entryApi.create(data);
    await fetchEntries();
  }

  async function updateEntry(id: number, data: Partial<Entry> & { childImpacts?: unknown[] }) {
    await entryApi.update(id, data);
    await fetchEntries();
  }

  async function deleteEntry(id: number) {
    await entryApi.delete(id, currentUser.value?.email);
    await fetchEntries();
  }

  async function approveEntry(id: number, modifiedUser?: string) {
    await entryApi.approve(id, modifiedUser);
    await fetchEntries();
  }

  function resetFilters() {
    filters.value = {
      division: [],
      department: "",
      country: [],
      channel: [],
      sub_channel: [],
      account: [],
      brand: "",
      brand_family: "",
      categorisation: "",
      r_and_o: "",
      probability: "",
      status: [],
      owner: "",
      ibp_step: [],
      creation_date_period: "",
      creation_date_year: "",
    };
  }

  return {
    entries,
    loading,
    users,
    currentUser,
    userRole,
    filters,
    displayEntries,
    canCreate,
    canApprove,
    fetchUsers,
    fetchEntries,
    createEntry,
    updateEntry,
    deleteEntry,
    approveEntry,
    resetFilters,
  };
});
