// In-browser stand-in for the FastAPI backend, used by the static GitHub Pages build
// (VITE_USE_MOCK=true). Mirrors the routes and response shapes in backend/app/api/*.
// State lives in memory, so any changes made in the demo are lost on reload.
import { AxiosError, AxiosHeaders, type AxiosResponse, type InternalAxiosRequestConfig } from "axios";
import {
  COUNTRY_CODES,
  CUSTOMERS,
  DESCRIPTIONS,
  KNOWN_IBP_STEPS,
  LOOKUP_OPTIONS,
  PRODUCTS,
  ROLE_NAMES,
  USERS,
  type UserRow,
} from "./data";

type Dict = Record<string, any>;
type Params = Record<string, string[]>;

interface EntryRow extends Dict {
  id: number;
  original_entry_id: number;
  version: number;
  status: string;
  last_modified: string;
  created_at: string;
}

interface ChildRow {
  id: number;
  entry_id: number;
  impact_year: string;
  impact_period: string;
  nsv_aud: string | null;
  nsv_nzd: string | null;
  volume_litres: string | null;
  volume_cases: string | null;
  volume_impact_value: string | null;
  gp_aud: string | null;
  gp_nzd: string | null;
}

interface SnapshotRow {
  id: number;
  snapshot_id: string;
  entry_id: number;
  period: string;
  year: string;
  ibp_step: string;
  entry_data: Dict;
  created_at: string;
  version: number;
  is_final: boolean;
  creator: string | null;
}

const ENTRY_FIELDS = [
  "creation_date", "creation_date_period", "creation_date_year",
  "add_to_forecast_by_period", "add_to_forecast_by_year", "division", "ibp_step",
  "country", "channel", "sub_channel", "account", "brand", "brand_family",
  "r_and_o", "probability", "categorisation", "impact_period", "impact_year",
  "nsv_aud", "nsv_nzd", "volume_litres", "primary_impact", "owner", "modified_user",
  "status", "short_description", "description", "financial_impact_type", "volume_cases",
  "volume_impact_type", "volume_impact_value", "fixed_nsv_gp_ratio", "fixed_nsv_vol_ratio",
  "net_financial_impact_value",
];
const CHILD_FIELDS = [
  "impact_year", "impact_period", "nsv_aud", "nsv_nzd", "volume_litres",
  "volume_cases", "volume_impact_value", "gp_aud", "gp_nzd",
] as const;

const ALL_IBP_STEP_NAME = "All";

// ---------------------------------------------------------------- state

let entries: EntryRow[] = [];
let children: ChildRow[] = [];
let snapshots: SnapshotRow[] = [];
let users: UserRow[] = USERS.map((u) => ({ ...u }));
let nextEntryId = 1;
let nextChildId = 1;
let nextSnapshotRowId = 1;

// During seeding the clock is moved manually so timestamps look like real history.
let clock: Date | null = null;
const now = () => (clock ?? new Date()).toISOString().slice(0, 19);

class HttpError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
  }
}

// ---------------------------------------------------------------- helpers

function normalizeDivision(value: unknown): string[] {
  if (value == null) return [];
  if (Array.isArray(value)) return value.map((v) => String(v).trim()).filter(Boolean);
  if (typeof value === "object") return Object.values(value as Dict).map((v) => String(v).trim()).filter(Boolean);
  const s = String(value).trim();
  return s ? [s] : [];
}

function sum(values: (string | null | undefined)[]): number {
  return values.reduce((acc, v) => {
    const n = parseFloat(v ?? "");
    return Number.isNaN(n) ? acc : acc + n;
  }, 0);
}

// Python's str(float) — whole numbers keep a trailing ".0"
const pyFloatStr = (n: number) => (Number.isInteger(n) ? `${n}.0` : String(n));

const childrenOf = (entryId: number) => children.filter((c) => c.entry_id === entryId);
const maxVersion = (originalId: number) =>
  Math.max(0, ...entries.filter((e) => e.original_entry_id === originalId).map((e) => e.version));

function latestEntries(filters: Dict = {}, includeDeleted = false, ibpStepIn: string[] | null = null): EntryRow[] {
  const latest = new Map<number, EntryRow>();
  for (const e of entries) {
    const cur = latest.get(e.original_entry_id);
    if (!cur || e.version > cur.version) latest.set(e.original_entry_id, e);
  }
  let rows = [...latest.values()];
  if (!includeDeleted) rows = rows.filter((e) => e.status !== "Deleted");

  const stripZeros = (s: string) => s.replace(/^0+/, "") || "0";
  for (const [field, raw] of Object.entries(filters)) {
    if (!raw || (Array.isArray(raw) && raw.length === 0)) continue;
    const values: string[] = Array.isArray(raw) ? raw : [raw];
    if (field === "division") {
      rows = rows.filter((e) => normalizeDivision(e.division).some((d) => values.includes(d)));
    } else if (["channel", "sub_channel", "account", "brand", "brand_family", "country"].includes(field)) {
      // JSON map columns match on their keys (codes)
      const norm = field === "country" ? stripZeros : (s: string) => s;
      const wanted = new Set(values.map(norm));
      rows = rows.filter((e) => Object.keys(e[field] ?? {}).some((k) => wanted.has(norm(k))));
    } else if (field === "probability" && values.length === 1 && values[0].includes(" & ")) {
      // "High & Medium" quick filter
      const wanted = values[0].split(" & ");
      rows = rows.filter((e) => wanted.includes(e.probability));
    } else {
      rows = rows.filter((e) => values.includes(String(e[field] ?? "")));
    }
  }
  if (ibpStepIn) rows = rows.filter((e) => ibpStepIn.includes(e.ibp_step));
  return rows.sort((a, b) => b.last_modified.localeCompare(a.last_modified));
}

function calculateImpact(entry: EntryRow, cis: ChildRow[]) {
  const primary = entry.primary_impact ?? "";
  const currency = ["AUD", "NZD"].includes(primary) ? primary : null;
  if (cis.length === 0) {
    const impact = primary === "AUD" ? entry.nsv_aud || null : primary === "NZD" ? entry.nsv_nzd || null : null;
    return { impact, currency, vol: entry.volume_impact_value ?? null, gp: entry.net_financial_impact_value ?? null };
  }
  const fin = sum(cis.map((c) => (primary === "AUD" ? c.nsv_aud : primary === "NZD" ? c.nsv_nzd : null)));
  const vol = sum(cis.map((c) => c.volume_impact_value));
  const gp = sum(cis.map((c) => (primary === "NZD" ? c.gp_nzd : c.gp_aud)));
  return {
    impact: fin ? pyFloatStr(fin) : null,
    currency,
    vol: vol ? pyFloatStr(vol) : null,
    gp: gp ? pyFloatStr(gp) : null,
  };
}

function childToDict(entry: EntryRow, c: ChildRow) {
  const primary = entry.primary_impact ?? "";
  return {
    id: c.id,
    impactYear: c.impact_year,
    impactPeriod: c.impact_period,
    nsvAud: c.nsv_aud,
    nsvNzd: c.nsv_nzd,
    volumeLitres: c.volume_litres,
    volumeCases: c.volume_cases,
    volumeImpactType: entry.volume_impact_type,
    volumeImpactValue: c.volume_impact_value,
    impact: primary === "AUD" && c.nsv_aud ? c.nsv_aud : primary === "NZD" && c.nsv_nzd ? c.nsv_nzd : null,
    impactCurrency: ["AUD", "NZD"].includes(primary) ? primary : null,
    gpAud: c.gp_aud,
    gpNzd: c.gp_nzd,
  };
}

function entryToDict(entry: EntryRow, lastModifiedSuffix = "Z") {
  const cis = childrenOf(entry.id);
  const { impact, currency, vol, gp } = calculateImpact(entry, cis);
  return {
    id: entry.id,
    originalEntryId: entry.original_entry_id,
    version: entry.version,
    creationDate: entry.creation_date,
    creationDatePeriod: entry.creation_date_period,
    creationDateYear: entry.creation_date_year,
    addToForecastByPeriod: entry.add_to_forecast_by_period,
    addToForecastByYear: entry.add_to_forecast_by_year,
    division: normalizeDivision(entry.division),
    ibpStep: entry.ibp_step,
    country: entry.country,
    channel: entry.channel,
    subChannel: entry.sub_channel,
    account: entry.account,
    brand: entry.brand,
    brandFamily: entry.brand_family,
    rAndO: entry.r_and_o,
    probability: entry.probability,
    categorisation: entry.categorisation,
    impactPeriod: entry.impact_period,
    impactYear: entry.impact_year,
    nsvAud: entry.nsv_aud,
    nsvNzd: entry.nsv_nzd,
    volumeLitres: entry.volume_litres,
    primaryImpact: entry.primary_impact,
    owner: entry.owner,
    creator: entry.creator,
    modifiedUser: entry.modified_user,
    status: entry.status,
    shortDescription: entry.short_description,
    description: entry.description,
    financialImpactType: entry.financial_impact_type,
    volumeCases: entry.volume_cases,
    volumeImpactType: entry.volume_impact_type,
    volumeImpactValue: vol,
    impact,
    impactCurrency: currency,
    lastModified: entry.last_modified + lastModifiedSuffix,
    fixedNsvGpRatio: entry.fixed_nsv_gp_ratio,
    fixedNsvVolRatio: entry.fixed_nsv_vol_ratio,
    netFinancialImpactValue: gp,
    childImpacts: cis.map((c) => childToDict(entry, c)),
  };
}

// ---------------------------------------------------------------- entries

function addChildren(entryId: number, list: Dict[] = []) {
  for (const ci of list) {
    const row = { id: nextChildId++, entry_id: entryId } as ChildRow;
    for (const f of CHILD_FIELDS) (row as Dict)[f] = ci[f] ?? null;
    children.push(row);
  }
}

function pickEntryFields(body: Dict): Dict {
  const data: Dict = {};
  for (const f of ENTRY_FIELDS) data[f] = body[f] ?? null;
  data.status ??= "Open";
  data.financial_impact_type ??= "NSV";
  data.division = normalizeDivision(body.division);
  return data;
}

function createEntry(body: Dict): EntryRow {
  const id = nextEntryId++;
  const data = pickEntryFields(body);
  const entry: EntryRow = {
    ...data,
    status: data.status,
    creator: body.creator ?? null,
    id,
    original_entry_id: id,
    version: 1,
    last_modified: now(),
    created_at: now(),
  };
  entries.push(entry);
  addChildren(id, body.child_impacts);
  return entry;
}

function updateEntry(entryId: number, body: Dict): EntryRow {
  const current = entries.find((e) => e.id === entryId);
  if (!current) throw new HttpError(404, "Entry not found");
  const data = pickEntryFields(body);
  const entry: EntryRow = {
    ...data,
    status: data.status,
    creator: current.creator,
    id: nextEntryId++,
    original_entry_id: current.original_entry_id,
    version: maxVersion(current.original_entry_id) + 1,
    last_modified: now(),
    created_at: now(),
  };
  entries.push(entry);
  addChildren(entry.id, body.child_impacts);
  return entry;
}

function newVersionWithStatus(entryId: number, status: string, modifiedUser: string | null): EntryRow {
  const current = entries.find((e) => e.id === entryId);
  if (!current) throw new HttpError(404, "Entry not found");
  const entry: EntryRow = {
    ...structuredClone(current),
    id: nextEntryId++,
    version: maxVersion(current.original_entry_id) + 1,
    status,
    modified_user: modifiedUser,
    last_modified: now(),
    created_at: now(),
  };
  entries.push(entry);
  addChildren(entry.id, childrenOf(current.id));
  return entry;
}

// ---------------------------------------------------------------- snapshots

function snapshotEntryData(entry: EntryRow) {
  const cis = childrenOf(entry.id);
  const { impact, vol } = snapshotImpacts(entry, cis);
  return {
    id: entry.id,
    original_entry_id: entry.original_entry_id,
    version: entry.version,
    creation_date: entry.creation_date,
    creation_date_period: entry.creation_date_period,
    creation_date_year: entry.creation_date_year,
    division: normalizeDivision(entry.division),
    ibp_step: entry.ibp_step,
    country: entry.country,
    channel: entry.channel,
    sub_channel: entry.sub_channel,
    account: entry.account,
    brand: entry.brand,
    brand_family: entry.brand_family,
    r_and_o: entry.r_and_o,
    probability: entry.probability,
    categorisation: entry.categorisation,
    impact_period: entry.impact_period,
    impact_year: entry.impact_year,
    nsv_aud: entry.nsv_aud,
    nsv_nzd: entry.nsv_nzd,
    volume_litres: entry.volume_litres,
    volume_cases: entry.volume_cases,
    owner: entry.owner,
    creator: entry.creator,
    status: entry.status,
    short_description: entry.short_description,
    description: entry.description,
    primary_impact: entry.primary_impact,
    volume_impact_type: entry.volume_impact_type,
    volume_impact_value: vol,
    impact,
    child_impacts: cis.map((c) => ({
      id: c.id,
      impact_year: c.impact_year,
      impact_period: c.impact_period,
      nsv_aud: c.nsv_aud,
      nsv_nzd: c.nsv_nzd,
      volume_litres: c.volume_litres,
      volume_cases: c.volume_cases,
      volume_impact_value: c.volume_impact_value,
    })),
  };
}

// snapshots.py variant: "Volume" primary impact falls back to the volume value
function snapshotImpacts(entry: EntryRow, cis: ChildRow[]) {
  const base = calculateImpact(entry, cis);
  let impact = base.impact;
  if (entry.primary_impact === "Volume") {
    impact = cis.length ? base.vol : entry.volume_impact_value || entry.volume_litres || null;
  }
  return { impact, vol: base.vol };
}

const randomHex = () => Math.floor(Math.random() * 0xffffffff).toString(16).padStart(8, "0");

function createSnapshot(body: Dict) {
  const { period, year, ibp_step } = body;
  const isFinal = Boolean(body.is_final);
  const same = (s: SnapshotRow) => s.period === period && s.year === year && s.ibp_step === ibp_step;
  if (snapshots.some((s) => same(s) && s.is_final)) {
    throw new HttpError(400, `A final version for ${ibp_step} in ${period} ${year} already exists. No new snapshots can be created for this period.`);
  }
  const version = Math.max(0, ...snapshots.filter(same).map((s) => s.version)) + 1;
  const snapshotId = `SNAP-${year}-${period}-${ibp_step.replace(/ /g, "_")}-${randomHex()}`.toUpperCase();
  const rows = latestEntries({ ibp_step });
  if (rows.length === 0) throw new HttpError(404, "No entries found for the specified filters");

  const createdAt = now();
  for (const entry of rows) {
    snapshots.push({
      id: nextSnapshotRowId++,
      snapshot_id: snapshotId,
      entry_id: entry.id,
      period,
      year,
      ibp_step,
      entry_data: snapshotEntryData(entry),
      created_at: createdAt,
      version,
      is_final: isFinal,
      creator: body.creator_email ?? null,
    });
  }
  if (isFinal && KNOWN_IBP_STEPS.includes(ibp_step)) reconcileAllIbpSnapshot(period, year);
  return {
    snapshot_id: snapshotId,
    name: `${ibp_step} - ${period} ${year}`,
    version,
    entries_count: rows.length,
    created_at: createdAt,
  };
}

function reconcileAllIbpSnapshot(period: string, year: string) {
  const finals = snapshots.filter((s) => s.period === period && s.year === year && s.is_final);
  const individual = finals.filter((s) => s.ibp_step !== ALL_IBP_STEP_NAME);
  const finalSteps = new Set(individual.map((s) => s.ibp_step));
  const isAll = (s: SnapshotRow) => s.period === period && s.year === year && s.ibp_step === ALL_IBP_STEP_NAME;

  if (!KNOWN_IBP_STEPS.every((step) => finalSteps.has(step))) {
    const existing = snapshots.filter((s) => isAll(s) && s.is_final).sort((a, b) => b.version - a.version)[0];
    if (existing) snapshots.filter((s) => s.snapshot_id === existing.snapshot_id).forEach((s) => (s.is_final = false));
    return;
  }
  const version = Math.max(0, ...snapshots.filter(isAll).map((s) => s.version)) + 1;
  const snapshotId = `SNAP-${year}-${period}-${ALL_IBP_STEP_NAME}-${randomHex()}`.toUpperCase();
  snapshots = snapshots.filter((s) => !isAll(s));
  for (const rec of individual) {
    snapshots.push({
      ...rec,
      id: nextSnapshotRowId++,
      snapshot_id: snapshotId,
      ibp_step: ALL_IBP_STEP_NAME,
      is_final: true,
      version,
      created_at: now(),
      creator: null,
    });
  }
}

function listSnapshots() {
  const groups = new Map<string, SnapshotRow[]>();
  for (const s of snapshots) {
    const key = [s.snapshot_id, s.is_final, s.version, s.creator].join("|");
    groups.set(key, [...(groups.get(key) ?? []), s]);
  }
  return [...groups.values()]
    .map((rows) => {
      const s = rows[0];
      const createdAt = rows.map((r) => r.created_at).sort()[0];
      return {
        snapshot_id: s.snapshot_id,
        name: `${s.ibp_step} - ${s.period} ${s.year}`,
        period: s.period,
        year: s.year,
        ibp_step: s.ibp_step,
        is_final: s.is_final,
        entries_count: rows.length,
        version: s.version,
        created_at: createdAt,
        creator: s.creator,
      };
    })
    .sort((a, b) => b.created_at.localeCompare(a.created_at));
}

function getSnapshot(snapshotId: string) {
  const rows = snapshots.filter((s) => s.snapshot_id === snapshotId);
  if (rows.length === 0) throw new HttpError(404, "Snapshot not found");
  const first = rows[0];
  const ids = new Set(rows.map((r) => r.entry_id));
  const snapEntries = entries
    .filter((e) => ids.has(e.id))
    .map((e) => {
      const d = entryToDict(e, "");
      const { impact, vol } = snapshotImpacts(e, childrenOf(e.id));
      return { ...d, division: e.division, impact, volumeImpactValue: vol };
    });
  return {
    snapshot: {
      snapshot_id: snapshotId,
      name: `${first.ibp_step} - ${first.period} ${first.year}`,
      period: first.period,
      year: first.year,
      ibp_step: first.ibp_step,
      version: first.version,
      created_at: first.created_at,
      entries: snapEntries,
    },
  };
}

// ---------------------------------------------------------------- lookups

const uniqBy = <T>(rows: T[], key: (r: T) => string) => [...new Map(rows.map((r) => [key(r), r])).values()];
const options = (rows: { value: string; label: string }[]) => ({ options: rows });

function customers(p: { country?: string; channel_code?: string; subchannel_code?: string; account_code?: string }) {
  return CUSTOMERS.filter(
    (c) =>
      (!p.country || c.country === p.country) &&
      (!p.channel_code || c.channel_code === p.channel_code) &&
      (!p.subchannel_code || c.subchannel_code === p.subchannel_code) &&
      (!p.account_code || c.account_code === p.account_code)
  );
}

function byName<T>(rows: T[], code: (r: T) => string, name: (r: T) => string) {
  return uniqBy(rows, code)
    .sort((a, b) => name(a).localeCompare(name(b)))
    .map((r) => ({ value: code(r), label: name(r) }));
}

// ---------------------------------------------------------------- router

type Handler = (m: RegExpMatchArray, q: (k: string) => string | undefined, params: Params, body: Dict) => unknown;

const routes: [method: string, pattern: RegExp, handler: Handler][] = [
  ["get", /^\/health$/, () => ({ status: "ok" })],

  // auth: the demo signs everyone in as the demo admin, who can "Test as" any other user
  ["get", /^\/api\/auth\/config$/, () => ({ auth_mode: "DBX" })],
  ["get", /^\/api\/auth\/me$/, () => {
    const u = users.find((x) => x.role === 0 && x.is_active) ?? users[0];
    const { id, email, display_name, role, ibp_steps, country, division } = u;
    return { id, email, display_name, role, ibp_steps, country, division };
  }],

  // users
  ["get", /^\/api\/users$/, () => ({ users: [...users].sort((a, b) => a.email.localeCompare(b.email)) })],
  ["post", /^\/api\/users$/, (_m, _q, _p, body) => {
    const user: UserRow = {
      id: Math.max(0, ...users.map((u) => u.id)) + 1,
      email: body.email,
      display_name: body.display_name ?? null,
      role: body.role,
      role_name: body.role_name || ROLE_NAMES[body.role] || null,
      ibp_steps: body.ibp_steps ?? null,
      is_active: body.is_active ?? true,
      country: body.country ?? null,
      division: body.division ?? null,
    };
    users.push(user);
    return user;
  }],
  ["put", /^\/api\/users\/(\d+)$/, (m, _q, _p, body) => {
    const user = users.find((u) => u.id === Number(m[1]));
    if (!user) throw new HttpError(404, "User not found");
    if (body.role != null && body.role_name == null) body.role_name = ROLE_NAMES[body.role];
    Object.assign(user, body);
    return user;
  }],
  ["delete", /^\/api\/users\/(\d+)$/, (m) => {
    const before = users.length;
    users = users.filter((u) => u.id !== Number(m[1]));
    if (users.length === before) throw new HttpError(404, "User not found");
    return "";
  }],

  // entries
  ["get", /^\/api\/entries$/, (_m, q, params) => {
    const filters: Dict = {};
    for (const f of ["division", "ibp_step", "country", "channel", "sub_channel", "account", "brand",
      "brand_family", "categorisation", "r_and_o", "probability", "status",
      "creation_date_period", "creation_date_year"]) {
      filters[f] = params[f];
    }
    filters.owner = q("owner");
    const ibpIn = q("role") === "IBP Step Approver" && q("user_ibp_steps")
      ? q("user_ibp_steps")!.split(",").map((s) => s.trim()).filter(Boolean)
      : null;
    return { entries: latestEntries(filters, false, ibpIn).map((e) => entryToDict(e)) };
  }],
  ["post", /^\/api\/entries$/, (_m, _q, _p, body) => {
    const e = createEntry(body);
    return { id: e.id, originalEntryId: e.original_entry_id, version: e.version };
  }],
  ["put", /^\/api\/entries\/(\d+)$/, (m, _q, _p, body) => {
    const e = updateEntry(Number(m[1]), body);
    return { id: e.id, originalEntryId: e.original_entry_id, version: e.version };
  }],
  ["delete", /^\/api\/entries\/(\d+)$/, (m, q) => {
    newVersionWithStatus(Number(m[1]), "Deleted", q("modified_user") ?? null);
    return { success: true };
  }],
  ["patch", /^\/api\/entries\/(\d+)\/status$/, (m, _q, _p, body) => {
    const e = newVersionWithStatus(Number(m[1]), body.status, body.modified_user ?? null);
    return { id: e.id, status: e.status };
  }],
  ["patch", /^\/api\/entries\/(\d+)\/approve$/, (m, _q, _p, body) => {
    const e = newVersionWithStatus(Number(m[1]), "Approved", body?.modified_user ?? null);
    return { id: e.id, status: e.status };
  }],
  ["get", /^\/api\/entries\/(\d+)\/status$/, (m) => {
    const entry = entries.find((e) => e.id === Number(m[1]));
    if (!entry) throw new HttpError(404, "Entry not found");
    const latest = latestEntries({}, true).find((e) => e.original_entry_id === entry.original_entry_id)!;
    return { id: entry.id, status: latest.status };
  }],
  ["get", /^\/api\/entries\/(\d+)\/history$/, (m) => ({
    versions: entries
      .filter((e) => e.original_entry_id === Number(m[1]))
      .sort((a, b) => b.version - a.version)
      .map((e) => entryToDict(e)),
  })],

  // lookups
  ["get", /^\/api\/lookups$/, (_m, q) => {
    // Every demo lookup option is top level, so a parent filter matches nothing (as in crud.py)
    const values = q("parent_value") ? [] : LOOKUP_OPTIONS[q("category") ?? ""] ?? [];
    return options(values.map((v) => ({ value: v, label: v })));
  }],
  ["get", /^\/api\/lookups\/divisions$/, () =>
    options([...new Set(PRODUCTS.map((p) => p.division))].sort().map((d) => ({ value: d, label: d })))],
  ["get", /^\/api\/lookups\/countries$/, (_m, q) =>
    options(byName(CUSTOMERS.filter((c) => c.division === q("division")), (c) => c.company_code, (c) => c.country))],
  ["get", /^\/api\/lookups\/brands$/, (_m, q) =>
    options(byName(PRODUCTS.filter((p) => p.division === q("division")), (p) => p.brand_code, (p) => p.brand_name))],
  ["get", /^\/api\/lookups\/brand-families$/, (_m, q, params) => {
    const names = params.brand_names ?? [];
    const rows = PRODUCTS.filter((p) => names.includes(p.brand_name) && (!q("division") || p.division === q("division")));
    return options(byName(rows, (p) => p.brand_family_code, (p) => p.brand_family_name));
  }],
  ["get", /^\/api\/lookups\/channels$/, (_m, q) =>
    options(byName(customers({ country: q("country") }), (c) => c.channel_code, (c) => c.channel_name))],
  ["get", /^\/api\/lookups\/subchannels$/, (_m, q) =>
    options(byName(customers({ country: q("country"), channel_code: q("channel_code") }), (c) => c.subchannel_code, (c) => c.subchannel_name))],
  ["get", /^\/api\/lookups\/accounts$/, (_m, q) =>
    options(byName(customers({ country: q("country"), subchannel_code: q("subchannel_code") }), (c) => c.account_code, (c) => c.account_name))],
  ["get", /^\/api\/lookups\/subchannel-details$/, (_m, q) => {
    const c = customers({ country: q("country"), subchannel_code: q("subchannel_code") ?? "\0" })[0];
    return { channel: c ? { code: c.channel_code, name: c.channel_name } : null };
  }],
  ["get", /^\/api\/lookups\/account-details$/, (_m, q) => {
    const c = customers({ country: q("country"), account_code: q("account_code") ?? "\0" })[0];
    return c
      ? { channel: { code: c.channel_code, name: c.channel_name }, subchannel: { code: c.subchannel_code, name: c.subchannel_name } }
      : { channel: null, subchannel: null };
  }],
  ["get", /^\/api\/lookups\/brand-family-details$/, (_m, q) => {
    const p = PRODUCTS.find((x) => x.division === q("division") && x.brand_family_code === q("brand_family_code"));
    return { brand: p ? { code: p.brand_code, name: p.brand_name } : null };
  }],
  ["get", /^\/api\/lookups\/brand-families-by-brand$/, (_m, q) => {
    const rows = PRODUCTS.filter((p) => p.division === q("division") && p.brand_code === q("brand_code"));
    return options(byName(rows, (p) => p.brand_family_code, (p) => p.brand_family_name));
  }],

  // snapshots
  ["get", /^\/api\/snapshots$/, () => ({ snapshots: listSnapshots() })],
  ["post", /^\/api\/snapshots$/, (_m, _q, _p, body) => createSnapshot(body)],
  ["patch", /^\/api\/snapshots\/([^/]+)\/final$/, (m, _q, _p, body) => {
    const id = decodeURIComponent(m[1]);
    const rows = snapshots.filter((s) => s.snapshot_id === id);
    if (rows.length === 0) throw new HttpError(404, "Snapshot not found");
    const first = rows[0];
    const isFinal = Boolean(body.isFinal ?? body.is_final);
    if (isFinal && snapshots.some((s) => s.period === first.period && s.year === first.year &&
      s.ibp_step === first.ibp_step && s.is_final && s.snapshot_id !== id)) {
      throw new HttpError(400, `A final version for ${first.ibp_step} in ${first.period} ${first.year} already exists.`);
    }
    rows.forEach((s) => (s.is_final = isFinal));
    reconcileAllIbpSnapshot(first.period, first.year);
    return { success: true, is_final: isFinal };
  }],
  ["get", /^\/api\/snapshots\/([^/]+)$/, (m) => getSnapshot(decodeURIComponent(m[1]))],
  ["delete", /^\/api\/snapshots\/([^/]+)$/, (m) => {
    const id = decodeURIComponent(m[1]);
    const rows = snapshots.filter((s) => s.snapshot_id === id);
    if (rows.length === 0) throw new HttpError(404, "Snapshot not found");
    snapshots = snapshots.filter((s) => s.snapshot_id !== id);
    const first = rows[0];
    if (KNOWN_IBP_STEPS.includes(first.ibp_step)) reconcileAllIbpSnapshot(first.period, first.year);
    return { message: "Snapshot deleted successfully", deleted_entries: rows.length };
  }],
];

function readParams(config: InternalAxiosRequestConfig, url: URL): Params {
  const out: Params = {};
  const add = (k: string, v: unknown) => {
    if (v == null || v === "") return;
    const key = k.replace(/\[\]$/, "");
    (out[key] ??= []).push(String(v));
  };
  url.searchParams.forEach((v, k) => add(k, v));
  const p = config.params;
  if (p instanceof URLSearchParams) p.forEach((v, k) => add(k, v));
  else if (p) for (const [k, v] of Object.entries(p)) (Array.isArray(v) ? v : [v]).forEach((x) => add(k, x));
  return out;
}

export async function mockAdapter(config: InternalAxiosRequestConfig): Promise<AxiosResponse> {
  const url = new URL(config.url ?? "/", "http://mock.local");
  const method = (config.method ?? "get").toLowerCase();
  const params = readParams(config, url);
  const q = (k: string) => params[k]?.[0];
  const body = typeof config.data === "string" && config.data ? JSON.parse(config.data) : config.data ?? {};

  // Small delay so loading states behave like they do against the real API
  await new Promise((r) => setTimeout(r, 120));

  const respond = (status: number, data: unknown): AxiosResponse => ({
    data,
    status,
    statusText: String(status),
    headers: new AxiosHeaders({ "content-type": "application/json" }),
    config,
    request: null,
  });

  try {
    for (const [m, pattern, handler] of routes) {
      const match = m === method ? url.pathname.match(pattern) : null;
      if (match) {
        // Deep copy so callers can't mutate the in-memory store through responses
        const data = structuredClone(handler(match, q, params, body));
        return respond(method === "delete" && data === "" ? 204 : 200, data);
      }
    }
    throw new HttpError(404, "Not Found");
  } catch (e) {
    if (!(e instanceof HttpError)) throw e;
    const response = respond(e.status, { detail: e.detail });
    throw new AxiosError(`Request failed with status code ${e.status}`,
      e.status >= 500 ? AxiosError.ERR_BAD_RESPONSE : AxiosError.ERR_BAD_REQUEST, config, null, response);
  }
}

// ---------------------------------------------------------------- seed data

// Deterministic PRNG so the demo looks the same on every load
function mulberry32(seed: number) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function seed() {
  const rand = mulberry32(20260930);
  const pick = <T>(arr: readonly T[]) => arr[Math.floor(rand() * arr.length)];
  const between = (lo: number, hi: number) => lo + Math.floor(rand() * (hi - lo + 1));
  const period = (m: number) => `F${String(m).padStart(2, "0")}`;
  const owners = users.filter((u) => [1, 2].includes(u.role));
  const admin = users.find((u) => u.role === 0)!;
  const setClock = (month: number, day: number) => {
    clock = new Date(Date.UTC(2026, month - 1, day, between(8, 17), between(0, 59), between(0, 59)));
  };

  function buildEntry(month: number): Dict {
    const division = pick(["Alcohol", "Alcohol", "Non-Alcohol"]);
    const country = pick(Object.keys(COUNTRY_CODES));
    const currency = country === "Australia" ? "AUD" : "NZD";
    const cust = pick(CUSTOMERS.filter((c) => c.division === division && c.country === country));
    const prod = pick(PRODUCTS.filter((p) => p.division === division));
    const rAndO = rand() < 0.55 ? "Risk" : "Opportunity";
    const [shortDesc, longDesc] = pick(DESCRIPTIONS[rAndO]);
    const owner = pick(owners);
    const gpRatio = 0.35 + rand() * 0.2;
    const pricePerCase = between(30, 60);
    const money = (n: number) => String(Math.round(n));

    const base: Dict = {
      creation_date: `2026-${String(month).padStart(2, "0")}-${String(between(1, 25)).padStart(2, "0")}`,
      creation_date_period: period(month),
      creation_date_year: "2026",
      add_to_forecast_by_period: period(Math.min(12, month + 1)),
      add_to_forecast_by_year: "2026",
      division: [division],
      ibp_step: pick(KNOWN_IBP_STEPS.slice(0, 3)),
      country: { [COUNTRY_CODES[country]]: country },
      channel: { [cust.channel_code]: cust.channel_name },
      sub_channel: { [cust.subchannel_code]: cust.subchannel_name },
      account: { [cust.account_code]: cust.account_name },
      brand: { [prod.brand_code]: prod.brand_name },
      brand_family: { [prod.brand_family_code]: prod.brand_family_name },
      r_and_o: rAndO,
      probability: pick(LOOKUP_OPTIONS.probability),
      categorisation: pick(LOOKUP_OPTIONS.categorisation),
      primary_impact: currency,
      owner: owner.email,
      creator: owner.email,
      modified_user: owner.email,
      status: "Open",
      short_description: shortDesc,
      description: longDesc,
      financial_impact_type: "NSV",
      volume_impact_type: "Cases",
      fixed_nsv_gp_ratio: gpRatio.toFixed(4),
      fixed_nsv_vol_ratio: String(pricePerCase),
    };

    const phases = rand() < 0.5 ? 1 : between(2, 6);
    const start = Math.min(12, month + between(0, 2));
    const nsvFor = () => between(10, 250) * 1000;
    if (phases === 1) {
      const nsv = nsvFor();
      return {
        ...base,
        impact_period: period(start),
        impact_year: "2026",
        nsv_aud: currency === "AUD" ? money(nsv) : null,
        nsv_nzd: currency === "NZD" ? money(nsv) : null,
        volume_cases: money(nsv / pricePerCase),
        volume_impact_value: money(nsv / pricePerCase),
        net_financial_impact_value: money(nsv * gpRatio),
        child_impacts: [],
      };
    }
    const childImpacts = Array.from({ length: phases }, (_, i) => {
      const m = start + i;
      const nsv = nsvFor() / 2;
      return {
        impact_year: m > 12 ? "2027" : "2026",
        impact_period: period(((m - 1) % 12) + 1),
        nsv_aud: currency === "AUD" ? money(nsv) : null,
        nsv_nzd: currency === "NZD" ? money(nsv) : null,
        volume_cases: money(nsv / pricePerCase),
        volume_impact_value: money(nsv / pricePerCase),
        gp_aud: currency === "AUD" ? money(nsv * gpRatio) : null,
        gp_nzd: currency === "NZD" ? money(nsv * gpRatio) : null,
      };
    });
    return { ...base, impact_period: null, impact_year: null, child_impacts: childImpacts };
  }

  // Jul–Aug: initial entries, then an August snapshot cycle
  for (let i = 0; i < 18; i++) {
    const month = i < 9 ? 7 : 8;
    setClock(month, between(1, 25));
    createEntry(buildEntry(month));
  }
  setClock(8, 28);
  for (const step of KNOWN_IBP_STEPS.slice(0, 3)) {
    createSnapshot({ period: "F08", year: "2026", ibp_step: step, is_final: true, creator_email: admin.email });
  }

  // September: approvals, edits, dismissals and new entries, then a draft snapshot
  setClock(9, 3);
  for (const e of latestEntries().slice(0, 6)) newVersionWithStatus(e.id, "Approved", "jordan.ibp@example.com");
  setClock(9, 8);
  for (const e of latestEntries().filter((x) => x.status === "Approved").slice(0, 3)) {
    newVersionWithStatus(e.id, "Included in Forecast", "taylor.finance@example.com");
  }
  setClock(9, 12);
  for (const e of latestEntries().filter((x) => x.status === "Open").slice(0, 3)) {
    const body: Dict = { ...structuredClone(e), child_impacts: childrenOf(e.id), modified_user: e.owner };
    body.probability = body.probability === "High" ? "Medium" : "High";
    for (const f of ["nsv_aud", "nsv_nzd", "net_financial_impact_value"]) {
      if (body[f]) body[f] = String(Math.round(Number(body[f]) * 1.2));
    }
    updateEntry(e.id, body);
  }
  setClock(9, 15);
  const toDismiss = latestEntries().find((x) => x.status === "Open");
  if (toDismiss) newVersionWithStatus(toDismiss.id, "Dismissed", "jordan.ibp@example.com");
  for (let i = 0; i < 8; i++) {
    setClock(9, between(16, 26));
    createEntry(buildEntry(9));
  }
  setClock(9, 29);
  createSnapshot({ period: "F09", year: "2026", ibp_step: "Demand Review", is_final: false, creator_email: admin.email });

  clock = null;
}

seed();
