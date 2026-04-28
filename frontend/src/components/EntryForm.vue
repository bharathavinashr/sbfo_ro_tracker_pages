<template>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-width="140px"
    label-position="top"
  >
    <el-divider content-position="left">Entry Owner</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Creator" prop="creator">
          <el-input v-model="formData.creator" disabled />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Owner" prop="owner">
          <el-select v-model="formData.owner" style="width: 100%" filterable>
            <el-option
              v-for="u in ownerOptions"
              :key="u.email"
              :value="u.email"
              :label="u.display_name ? `${u.display_name} (${u.email})` : u.email"
            />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Creation Period</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Period" prop="creationDatePeriod">
          <el-select v-model="formData.creationDatePeriod" style="width: 100%">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Year" prop="creationDateYear">
          <el-select v-model="formData.creationDateYear" style="width: 100%">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Add to Forecast By</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Period" prop="addToForecastByPeriod">
          <el-select v-model="formData.addToForecastByPeriod" style="width: 100%">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Year" prop="addToForecastByYear">
          <el-select v-model="formData.addToForecastByYear" style="width: 100%">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Organisation</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="Division" prop="division">
          <el-select v-model="formData.division" style="width: 100%">
            <el-option v-for="d in divisionOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Department" prop="department">
          <el-select v-model="formData.department" style="width: 100%">
            <el-option v-for="d in departmentOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Country" prop="country">
          <el-select v-model="formData.country" style="width: 100%">
            <el-option v-for="c in countryOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Customer</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="Channel" prop="channel">
          <el-select v-model="formData.channel" style="width: 100%">
            <el-option v-for="c in channelOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Sub-Channel" prop="subChannel">
          <el-select v-model="formData.subChannel" style="width: 100%">
            <el-option v-for="s in subChannelOptions" :key="s" :value="s" :label="s" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Account" prop="account">
          <el-select v-model="formData.account" style="width: 100%" clearable>
            <el-option v-for="a in accountOptions" :key="a" :value="a" :label="a" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Product</el-divider>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="Brand" prop="brand">
          <el-select v-model="formData.brand" style="width: 100%">
            <el-option v-for="b in brandOptions" :key="b" :value="b" :label="b" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="Brand Family" prop="brandFamily">
          <el-select v-model="formData.brandFamily" style="width: 100%" clearable>
            <el-option v-for="b in brandFamilyOptions" :key="b" :value="b" :label="b" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">Risk & Opportunity</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="R&O Type" prop="rAndO">
          <el-radio-group v-model="formData.rAndO">
            <el-radio-button value="Risk">Risk</el-radio-button>
            <el-radio-button value="Opportunity">Opportunity</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Probability" prop="probability">
          <el-radio-group v-model="formData.probability">
            <el-radio-button v-for="p in probabilityOptions" :key="p" :value="p">{{ p }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Categorisation" prop="categorisation" :required="categActive">
          <el-select
            v-model="formData.categorisation"
            style="width: 100%"
            :disabled="!categActive"
            :placeholder="categActive ? 'Select' : 'Only available for Marketing, Demand, or Supply'"
          >
            <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <el-form-item label="Description of Risk / Opportunity" prop="description" style="margin-top: 12px">
      <el-input v-model="formData.description" type="textarea" :rows="3" />
    </el-form-item>

    <el-divider content-position="left">Impact Details</el-divider>

    <!-- Impact locked until Country is selected -->
    <div v-if="!formData.country" class="impact-locked">
      <el-icon><InfoFilled /></el-icon>
      Please select a Country first to enable Impact Details.
    </div>

    <!-- Primary impact card -->
    <div v-else class="impact-card">
      <!-- Period / Year row -->
      <el-row :gutter="16">
        <el-col :span="12">
          <div class="impact-field-label">Period</div>
          <el-select v-model="formData.impactPeriod" :disabled="hasChildImpacts" style="width: 100%; margin-top: 8px">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-col>
        <el-col :span="12">
          <div class="impact-field-label">Year</div>
          <el-select v-model="formData.impactYear" :disabled="hasChildImpacts" style="width: 100%; margin-top: 8px">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-col>
      </el-row>

      <!-- Primary Impact row -->
      <el-row :gutter="16" style="margin-top: 14px">
        <el-col :span="24">
          <div class="impact-field-label">Primary Impact <span class="impact-required">*</span></div>
        </el-col>
        <el-col :span="8" style="margin-top: 8px">
          <el-select v-model="formData.primaryImpact" style="width: 100%">
            <el-option v-for="u in unitOptions" :key="u" :value="u" :label="unitLabels[u]" />
          </el-select>
        </el-col>
        <el-col :span="16" style="margin-top: 8px">
          <el-input
            :model-value="formData.impactValue"
            :disabled="hasChildImpacts"
            :placeholder="`Enter ${unitLabels[formData.primaryImpact]} value`"
            @input="formData.impactValue = cleanNumStr($event as string)"
            @blur="formData.impactValue = formatNumStr(formData.impactValue)"
            @focus="formData.impactValue = cleanNumStr(formData.impactValue)"
          />
        </el-col>
      </el-row>

      <!-- Secondary Impact row -->
      <el-row :gutter="16" style="margin-top: 14px">
        <el-col :span="24">
          <div class="impact-field-label">Secondary Impact</div>
        </el-col>
        <el-col :span="8" style="margin-top: 8px">
          <div class="unit-label-display">{{ unitLabels[formData.secondaryUnit] }}</div>
        </el-col>
        <el-col :span="16" style="margin-top: 8px">
          <el-input
            :model-value="formData.secondaryValue"
            :disabled="hasChildImpacts"
            :placeholder="`Enter ${unitLabels[formData.secondaryUnit]} value (optional)`"
            @input="formData.secondaryValue = cleanNumStr($event as string)"
            @blur="formData.secondaryValue = formatNumStr(formData.secondaryValue)"
            @focus="formData.secondaryValue = cleanNumStr(formData.secondaryValue)"
          />
        </el-col>
      </el-row>

      <div class="impact-add-btn">
        <el-button plain @click="addChild">+ Add Impact</el-button>
      </div>
    </div>

    <!-- Child impact rows -->
    <div
      v-for="(child, idx) in formData.childImpacts"
      :key="idx"
      class="impact-child-card"
    >
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="impact-field-label">Period <span class="impact-required">*</span></div>
          <el-select v-model="child.impactPeriod" placeholder="Period" style="width: 100%; margin-top: 8px">
            <el-option v-for="p in PERIODS" :key="p" :value="p" :label="p" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">Year</div>
          <el-select v-model="child.impactYear" style="width: 100%; margin-top: 8px">
            <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">{{ unitLabels[formData.primaryImpact] }}</div>
          <el-input
            :model-value="child.impactValue"
            :placeholder="`Enter value`"
            style="margin-top: 8px"
            @input="child.impactValue = cleanNumStr($event as string)"
            @blur="child.impactValue = formatNumStr(child.impactValue)"
            @focus="child.impactValue = cleanNumStr(child.impactValue)"
          />
        </el-col>
        <el-col :span="6">
          <div class="impact-field-label">{{ unitLabels[formData.secondaryUnit] }} <span style="color: var(--text-muted); font-weight:400">(optional)</span></div>
          <el-input
            :model-value="child.secondaryValue"
            :placeholder="`Enter value`"
            style="margin-top: 8px"
            @input="child.secondaryValue = cleanNumStr($event as string)"
            @blur="child.secondaryValue = formatNumStr(child.secondaryValue)"
            @focus="child.secondaryValue = cleanNumStr(child.secondaryValue)"
          />
        </el-col>
      </el-row>
      <div class="impact-remove-btn">
        <el-button type="danger" link @click="removeChild(idx)">
          <el-icon><Delete /></el-icon> Remove
        </el-button>
      </div>
    </div>

  </el-form>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, nextTick } from "vue";
import { Delete, InfoFilled } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import type { Entry } from "@/types";
import { PERIODS } from "@/types";
import { useLookupStore } from "@/stores/lookupStore";
import { useEntryStore } from "@/stores/entryStore";

const lookupStore = useLookupStore();
const entryStore = useEntryStore();
const currentUserEmail = computed(() => entryStore.currentUser?.email ?? "");
const ownerOptions = computed(() =>
  entryStore.users.filter((u) => u.role === 0 || u.role === 1)
);
onMounted(() => {
  lookupStore.preload();
  if (entryStore.users.length === 0) entryStore.fetchUsers();
});

const divisionOptions    = computed(() => lookupStore.getCached("division"));
const countryOptions     = computed(() => lookupStore.getCached("country"));
const channelOptions     = computed(() => lookupStore.getCached("channel"));
const probabilityOptions = computed(() => lookupStore.getCached("probability"));
const categOptions       = computed(() => lookupStore.getCached("categorisation"));
const brandOptions        = computed(() => lookupStore.getCached("brand"));
const brandFamilyOptions  = computed(() =>
  formData.value.brand
    ? lookupStore.getCached("brand_family", formData.value.brand)
    : lookupStore.getCached("brand_family")
);
const departmentOptions   = computed(() => lookupStore.getCached("department"));

const CATEG_ACTIVE_DEPTS  = ["Marketing", "Demand", "Supply"];
const categActive         = computed(() => CATEG_ACTIVE_DEPTS.includes(formData.value.department));

interface ChildImpactForm {
  impactYear: string;
  impactPeriod: string;
  impactValue: string;
  impactUnit: string;       // "AUD" | "NZD" | "Volume"
  secondaryValue: string;
  secondaryUnit: string;    // "AUD" | "NZD" | "Volume", must differ from impactUnit
}

interface FormData {
  creationDatePeriod: string;
  creationDateYear: string;
  addToForecastByPeriod: string;
  addToForecastByYear: string;
  division: string;
  department: string;
  country: string;
  channel: string;
  subChannel: string;
  account: string;
  brand: string;
  brandFamily: string;
  rAndO: string;
  probability: string;
  categorisation: string;
  impactPeriod: string;
  impactYear: string;
  impactValue: string;
  primaryImpact: string;   // "AUD" | "NZD" | "Volume"
  secondaryValue: string;
  secondaryUnit: string;   // "AUD" | "NZD" | "Volume", differs from primaryImpact
  owner: string;
  creator: string;
  status: string;
  description: string;
  childImpacts: ChildImpactForm[];
}

const props = defineProps<{ entry?: Entry | null }>();

const formRef = ref<FormInstance>();
const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;
const currentPeriod = `F${String(currentMonth).padStart(2, "0")}`;
const yearOptions = Array.from({ length: 10 }, (_, i) => currentYear - 2 + i);

function defaultForm(): FormData {
  const email = currentUserEmail.value;
  return {
    creationDatePeriod: currentPeriod,
    creationDateYear: String(currentYear),
    addToForecastByPeriod: currentPeriod,
    addToForecastByYear: String(currentYear),
    division: "",
    department: "",
    country: "",
    channel: "",
    subChannel: "",
    account: "",
    brand: "",
    brandFamily: "",
    rAndO: "Risk",
    probability: "",
    categorisation: "",
    impactPeriod: currentPeriod,
    impactYear: String(currentYear),
    impactValue: "",
    primaryImpact: "AUD",
    secondaryValue: "",
    secondaryUnit: "Volume",
    owner: email,
    creator: email,
    status: "Open",
    description: "",
    childImpacts: [],
  };
}

const formData = ref<FormData>(defaultForm());
const isLoadingEntry = ref(false);
const hasChildImpacts = computed(() => formData.value.childImpacts.length > 0);

// Always sync creator/owner to current user when in new-entry mode
watch(currentUserEmail, (email) => {
  if (email && !props.entry) {
    formData.value.creator = email;
    formData.value.owner = email;
  }
});

// Sub-Channel options cascade from selected Channel
const subChannelOptions = computed(() =>
  formData.value.channel
    ? lookupStore.getCached("sub_channel", formData.value.channel)
    : lookupStore.getCached("sub_channel")
);

// Account options cascade from selected Sub-Channel
const accountOptions = computed(() =>
  formData.value.subChannel
    ? lookupStore.getCached("account", formData.value.subChannel)
    : lookupStore.getCached("account")
);

watch(() => formData.value.channel, (val) => {
  if (!isLoadingEntry.value) {
    formData.value.subChannel = "";
    formData.value.account = "";
  }
  if (val) lookupStore.loadChildren("sub_channel", val);
});

watch(() => formData.value.subChannel, (val) => {
  if (!isLoadingEntry.value) formData.value.account = "";
  if (val) lookupStore.loadChildren("account", val);
});

watch(() => formData.value.brand, (val) => {
  if (!isLoadingEntry.value) formData.value.brandFamily = "";
  if (val) lookupStore.loadChildren("brand_family", val);
});

watch(() => formData.value.department, (val) => {
  if (!CATEG_ACTIVE_DEPTS.includes(val)) formData.value.categorisation = "";
});

// Unit options based on country: AU → AUD only, NZ → NZD only, else both
function getUnitOptions(country: string): string[] {
  if (country === "Australia") return ["AUD", "Volume"];
  if (country === "New Zealand") return ["NZD", "Volume"];
  return ["AUD", "NZD", "Volume"];
}
const unitOptions = computed(() => getUnitOptions(formData.value.country));

// 9L cases conversion: when division is "Alcohol", Volume label changes and values are stored ×9
const isAlcohol = computed(() => {
  const d = formData.value.division.toLowerCase();
  return d.includes("alcohol") && !d.includes("non-alcohol");
});
const unitLabels = computed<Record<string, string>>(() => ({
  AUD: "NSV (AUD)",
  NZD: "NSV (NZD)",
  Volume: isAlcohol.value ? "Vol. (9L)" : "Vol. (L)",
}));

watch(() => formData.value.country, (country) => {
  const opts = getUnitOptions(country);
  if (!opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = opts[0];
  const secOpts = opts.filter(u => u !== formData.value.primaryImpact);
  if (!secOpts.includes(formData.value.secondaryUnit)) formData.value.secondaryUnit = secOpts[0] ?? "";
  formData.value.childImpacts.forEach((ci) => {
    if (!opts.includes(ci.impactUnit)) ci.impactUnit = opts[0];
    const cs = opts.filter(u => u !== ci.impactUnit);
    if (!cs.includes(ci.secondaryUnit)) ci.secondaryUnit = cs[0] ?? "";
  });
});

// When primary unit changes: swap values so the user doesn't lose what they typed
watch(() => formData.value.primaryImpact, (newUnit, oldUnit) => {
  if (!oldUnit || newUnit === oldUnit || isLoadingEntry.value) return;

  // Build a value map from current state
  const vals: Record<string, string> = {
    [oldUnit]: formData.value.impactValue,
    [formData.value.secondaryUnit]: formData.value.secondaryValue,
  };

  // New primary gets its previously-stored value
  formData.value.impactValue = vals[newUnit] ?? "";

  // New secondary: prefer old primary unit, else first available non-primary
  const secOpts = unitOptions.value.filter(u => u !== newUnit);
  const newSecUnit = secOpts.includes(oldUnit) ? oldUnit : (secOpts[0] ?? "");
  formData.value.secondaryUnit = newSecUnit;
  formData.value.secondaryValue = vals[newSecUnit] ?? "";

  // Sync children: swap their values too
  formData.value.childImpacts.forEach(ci => {
    const ciVals: Record<string, string> = {
      [ci.impactUnit]: ci.impactValue,
      [ci.secondaryUnit]: ci.secondaryValue,
    };
    ci.impactUnit = newUnit;
    ci.impactValue = ciVals[newUnit] ?? "";
    ci.secondaryUnit = newSecUnit;
    ci.secondaryValue = ciVals[newSecUnit] ?? "";
  });
});

// Sync secondary unit to children
watch(() => formData.value.secondaryUnit, (val) => {
  if (isLoadingEntry.value) return;
  formData.value.childImpacts.forEach(ci => { ci.secondaryUnit = val; });
});

watch(
  () => props.entry,
  async (entry) => {
    if (entry) {
      isLoadingEntry.value = true;
      const _d = (entry.division || "").toLowerCase();
      const entryIsAlcohol = _d.includes("alcohol") && !_d.includes("non-alcohol");
      const fromStorage = (unit: string, val: string): string => {
        if (!val || unit !== "Volume" || !entryIsAlcohol) return val;
        const n = parseFloat(val);
        return isNaN(n) ? val : String(n / 9);
      };
      formData.value = {
        creationDatePeriod: entry.creationDatePeriod || currentPeriod,
        creationDateYear: entry.creationDateYear || String(currentYear),
        addToForecastByPeriod: entry.addToForecastByPeriod || currentPeriod,
        addToForecastByYear: entry.addToForecastByYear || String(currentYear),
        division: entry.division || "",
        department: entry.department || "",
        country: entry.country || "",
        channel: entry.channel || "",
        subChannel: entry.subChannel || "",
        account: entry.account || "",
        brand: entry.brand || "",
        brandFamily: Array.isArray(entry.brandFamily)
          ? entry.brandFamily[0] ?? ""
          : entry.brandFamily ?? "",
        rAndO: entry.rAndO || "Risk",
        probability: entry.probability || "",
        categorisation: entry.categorisation || "",
        impactPeriod: entry.impactPeriod || "",
        impactYear: entry.impactYear || (entry.childImpacts?.length ? "" : String(currentYear)),
        primaryImpact: entry.primaryImpact || "AUD",
        impactValue: formatNumStr(
          entry.primaryImpact === "NZD" ? (entry.nsvNzd || "")
          : entry.primaryImpact === "Volume" ? fromStorage("Volume", entry.volumeLitres || "")
          : (entry.nsvAud || "")
        ),
        ...((): { secondaryUnit: string; secondaryValue: string } => {
          const pi = entry.primaryImpact || "AUD";
          const candidates = [
            { unit: "AUD", val: entry.nsvAud || "" },
            { unit: "NZD", val: entry.nsvNzd || "" },
            { unit: "Volume", val: fromStorage("Volume", entry.volumeLitres || "") },
          ].filter(c => c.unit !== pi);
          const found = candidates.find(c => c.val) ?? candidates[0];
          return { secondaryUnit: found.unit, secondaryValue: formatNumStr(found.val) };
        })(),
        owner: entry.owner || "",
        creator: entry.id === 0 ? (currentUserEmail.value || entry.creator || "") : (entry.creator || ""),
        status: entry.status || "Open",
        description: entry.description || "",
        childImpacts: (entry.childImpacts || []).map((ci) => {
          // Use parent's primaryImpact — child rows always share the same unit as parent
          const primary = entry.primaryImpact || "AUD";
          const secondaryCandidates = [
            { unit: "AUD", val: ci.nsvAud || "" },
            { unit: "NZD", val: ci.nsvNzd || "" },
            { unit: "Volume", val: fromStorage("Volume", ci.volumeLitres || "") },
          ].filter(c => c.unit !== primary);
          const sec = secondaryCandidates.find(c => c.val) ?? secondaryCandidates[0];
          return {
            impactYear: ci.impactYear || "",
            impactPeriod: ci.impactPeriod || "",
            impactUnit: primary,
            impactValue: formatNumStr(
              primary === "NZD" ? (ci.nsvNzd || "")
              : primary === "Volume" ? fromStorage("Volume", ci.volumeLitres || "")
              : (ci.nsvAud || "")
            ),
            secondaryUnit: sec.unit,
            secondaryValue: formatNumStr(sec.val),
          };
        }),
      };
      if (entry.channel) lookupStore.loadChildren("sub_channel", entry.channel);
      if (entry.subChannel) lookupStore.loadChildren("account", entry.subChannel);
      if (entry.brand) lookupStore.loadChildren("brand_family", entry.brand);
      await nextTick();
      isLoadingEntry.value = false;
    } else {
      formData.value = defaultForm();
    }
  },
  { immediate: true }
);

const rules: FormRules = {
  creationDatePeriod: [{ required: true, message: "Required", trigger: "change" }],
  creationDateYear:   [{ required: true, message: "Required", trigger: "change" }],
  division: [{ required: true, message: "Required", trigger: "change" }],
  department: [{ required: true, message: "Required", trigger: "change" }],
  country: [{ required: true, message: "Required", trigger: "change" }],
  channel: [{ required: true, message: "Required", trigger: "change" }],
  subChannel: [{ required: true, message: "Required", trigger: "change" }],
  account: [{ required: true, message: "Required", trigger: "blur" }],
  brand: [{ required: true, message: "Required", trigger: "change" }],
  brandFamily: [{ required: true, message: "Required", trigger: "change" }],
  rAndO: [{ required: true, message: "Required", trigger: "change" }],
  probability: [{ required: true, message: "Required", trigger: "change" }],
  categorisation: [{
    validator: (_rule: unknown, value: string, callback: (e?: Error) => void) => {
      if (categActive.value && !value) callback(new Error("Required"));
      else callback();
    },
    trigger: "change",
  }],
  owner: [{ required: true, message: "Required", trigger: "change" }],
  creator: [{ required: true, message: "Required", trigger: "blur" }],
  description: [{ required: true, message: "Required", trigger: "blur" }],
};

function addChild() {
  const isFirst = formData.value.childImpacts.length === 0;
  if (isFirst) {
    formData.value.impactPeriod = "";
    formData.value.impactYear = "";
    formData.value.impactValue = "";
    formData.value.secondaryValue = "";
  }
  const count = isFirst ? 2 : 1;
  for (let i = 0; i < count; i++) {
    formData.value.childImpacts.push({
      impactYear: String(currentYear),
      impactPeriod: "",
      impactValue: "",
      impactUnit: formData.value.primaryImpact,
      secondaryValue: "",
      secondaryUnit: formData.value.secondaryUnit,
    });
  }
}

function removeChild(idx: number) {
  formData.value.childImpacts.splice(idx, 1);
  if (formData.value.childImpacts.length === 1) {
    // Promote the last remaining child back to parent fields
    const last = formData.value.childImpacts[0];
    formData.value.impactPeriod = last.impactPeriod || currentPeriod;
    formData.value.impactYear = last.impactYear || String(currentYear);
    formData.value.impactValue = last.impactValue;
    formData.value.secondaryValue = last.secondaryValue;
    formData.value.childImpacts = [];
  } else if (formData.value.childImpacts.length === 0) {
    formData.value.impactPeriod = currentPeriod;
    formData.value.impactYear = String(currentYear);
  }
}

function toStorage(unit: string, val: string): string {
  if (!val || unit !== "Volume" || !isAlcohol.value) return val;
  const n = parseFloat(val);
  return isNaN(n) ? val : String(n * 9);
}

function mapToFields(primaryUnit: string, primaryVal: string, secUnit: string, secVal: string) {
  const set = (unit: string) =>
    unit === primaryUnit ? toStorage(unit, primaryVal)
    : unit === secUnit   ? toStorage(unit, secVal)
    : "";
  return { nsvAud: set("AUD"), nsvNzd: set("NZD"), volumeLitres: set("Volume") };
}

function cleanNumStr(val: string): string {
  let s = val.replace(/,/g, "").replace(/[^\d.]/g, "");
  const d = s.indexOf(".");
  if (d !== -1) s = s.slice(0, d + 1) + s.slice(d + 1).replace(/\./g, "");
  return s;
}
function formatNumStr(val: string): string {
  const s = cleanNumStr(val);
  if (!s) return "";
  const parts = s.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.join(".");
}

function isValidNum(val: string): boolean {
  const s = cleanNumStr(val).trim();
  return s !== "" && !isNaN(Number(s));
}

async function validate() {
  try {
    await formRef.value!.validate();

    if (hasChildImpacts.value) {
      for (let i = 0; i < formData.value.childImpacts.length; i++) {
        const ci = formData.value.childImpacts[i];
        if (!ci.impactPeriod) {
          ElMessage.error(`Row ${i + 1}: Impact Period is required.`);
          return null;
        }
        if (!ci.impactYear) {
          ElMessage.error(`Row ${i + 1}: Impact Year is required.`);
          return null;
        }
        if (!ci.impactValue.trim()) {
          ElMessage.error(`Row ${i + 1}: Primary Impact value is required.`);
          return null;
        }
        if (!isValidNum(ci.impactValue)) {
          ElMessage.error(`Row ${i + 1}: Primary Impact must be a valid number.`);
          return null;
        }
        if (ci.secondaryValue.trim() && !isValidNum(ci.secondaryValue)) {
          ElMessage.error(`Row ${i + 1}: Secondary Impact must be a valid number.`);
          return null;
        }
        ci.impactValue = cleanNumStr(ci.impactValue);
        ci.secondaryValue = cleanNumStr(ci.secondaryValue);
      }
    } else {
      if (!formData.value.impactPeriod) {
        ElMessage.error("Impact Period is required.");
        return null;
      }
      if (!formData.value.impactYear) {
        ElMessage.error("Impact Year is required.");
        return null;
      }
      if (!formData.value.impactValue.trim()) {
        ElMessage.error("Primary Impact value is required.");
        return null;
      }
      if (!isValidNum(formData.value.impactValue)) {
        ElMessage.error("Primary Impact must be a valid number.");
        return null;
      }
      if (formData.value.secondaryValue.trim() && !isValidNum(formData.value.secondaryValue)) {
        ElMessage.error("Secondary Impact must be a valid number.");
        return null;
      }
      formData.value.impactValue = cleanNumStr(formData.value.impactValue);
      formData.value.secondaryValue = cleanNumStr(formData.value.secondaryValue);
    }

    const { nsvAud, nsvNzd, volumeLitres } = mapToFields(
      formData.value.primaryImpact, formData.value.impactValue,
      formData.value.secondaryUnit,  formData.value.secondaryValue,
    );
    return {
      ...formData.value,
      nsvAud, nsvNzd, volumeLitres,
      childImpacts: formData.value.childImpacts.map((ci) => {
        const m = mapToFields(ci.impactUnit, ci.impactValue, ci.secondaryUnit, ci.secondaryValue);
        return { impactYear: ci.impactYear, impactPeriod: ci.impactPeriod, ...m };
      }),
    };
  } catch {
    return null;
  }
}

function reset() {
  formData.value = defaultForm();
  formRef.value?.clearValidate();
}

defineExpose({ validate, reset });
</script>

<style scoped>
.impact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border: 1px dashed var(--border-color);
  border-radius: 0.625rem;
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 12px;
}

.impact-card {
  border: 1px solid var(--border-color);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--bg-secondary);
}

.impact-child-card {
  border: 1px solid var(--border-color);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--el-bg-color);
}

.impact-field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.impact-required {
  color: #d4183d;
}

.impact-add-btn {
  text-align: right;
  margin-top: 16px;
}

.impact-remove-btn {
  text-align: right;
  margin-top: 12px;
}

.unit-label-display {
  height: 32px;
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  padding: 0 4px;
}


.input-group {
  display: flex;
  gap: 0;
}
.input-group :deep(.el-select .el-input__wrapper) {
  border-radius: 4px 0 0 4px;
}
.input-group :deep(.el-input .el-input__wrapper) {
  border-radius: 0 4px 4px 0;
  border-left: none;
}
</style>
