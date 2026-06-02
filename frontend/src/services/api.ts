import axios from "axios";
import type { Entry, AppUser } from "@/types";

const api = axios.create({
  baseURL: "/",
  timeout: 30000,
});

export const entryApi = {
  getAll: (params?: Record<string, string>) =>
    api
      .get<{ entries: Entry[] }>("/api/entries", { params })
      .then((r) => r.data),

  getHistory: (originalEntryId: number) =>
    api
      .get<{ versions: Entry[] }>(`/api/entries/${originalEntryId}/history`)
      .then((r) => r.data),

  create: (data: Partial<Entry> & { childImpacts?: unknown[] }) =>
    api.post<{ id: number; version: number }>("/api/entries", data).then((r) => r.data),

  update: (id: number, data: Partial<Entry> & { childImpacts?: unknown[] }) =>
    api
      .put<{ id: number; version: number }>(`/api/entries/${id}`, data)
      .then((r) => r.data),

  delete: (id: number, modifiedUser?: string) =>
    api.delete(`/api/entries/${id}`, { params: { modified_user: modifiedUser } }).then((r) => r.data),

  approve: (id: number, modifiedUser?: string) =>
    api.patch(`/api/entries/${id}/approve`, { status: "Approved", modified_user: modifiedUser ?? null }).then((r) => r.data),

  updateStatus: (id: number, status: string, modifiedUser?: string) =>
    api.patch(`/api/entries/${id}/status`, { status, modified_user: modifiedUser ?? null }).then((r) => r.data),

  getStatus: (id: number): Promise<{ id: number; status: string }> =>
    api.get(`/api/entries/${id}/status`).then((r) => r.data),
};

export const userApi = {
  getAll: (): Promise<AppUser[]> =>
    api.get<{ users: AppUser[] }>("/api/users").then((r) => r.data.users),

  create: (data: Omit<AppUser, 'id'>): Promise<AppUser> =>
    api.post<AppUser>("/api/users", data).then((r) => r.data),

  update: (id: number, data: Partial<Omit<AppUser, 'id'>>): Promise<AppUser> =>
    api.put<AppUser>(`/api/users/${id}`, data).then((r) => r.data),

  delete: (id: number): Promise<void> =>
    api.delete(`/api/users/${id}`).then(() => undefined),
};

export const authApi = {
  getConfig: (): Promise<{ auth_mode: "LOCAL" | "DBX" }> =>
    api.get("/api/auth/config").then((r) => r.data),
  getMe: (): Promise<AppUser> =>
    api.get("/api/auth/me").then((r) => r.data),
};

export const lookupApi = {
  get: (category: string, parentValue?: string): Promise<string[]> =>
    api
      .get<{ options: { value: string; label: string }[] }>("/api/lookups", {
        params: { category, ...(parentValue ? { parent_value: parentValue } : {}) },
      })
      .then((r) => r.data.options.map((o) => o.value)),
  
  getDivisions: (): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/divisions")
      .then((r) => r.data),
  
  getBrands: (division: string, country?: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/brands", {
        params: { division, country },
      })
      .then((r) => r.data),

  getCountries: (division: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/countries", {
        params: { division },
      })
      .then((r) => r.data),
  
  getBrandFamilies: (brandNames: string[], country?: string, division?: string): Promise<{ options: { value: string; label: string }[] }> => {
    const params = new URLSearchParams();
    brandNames.forEach((n) => params.append("brand_names", n));
    if (country) params.append("country", country);
    if (division) params.append("division", division);
    return api
      .get("/api/lookups/brand-families", { params })
      .then((r) => r.data);
  },

  getChannels: (division: string, country?: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/channels", {
        params: { division, country },
      })
      .then((r) => r.data),

  getSubchannels: (division: string, channelCode: string, country?: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/subchannels", {
        params: { division, channel_code: channelCode, country },
      })
      .then((r) => r.data),

  getAccounts: (division: string, subchannelCode: string, country?: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/accounts", {
        params: { division, subchannel_code: subchannelCode, country },
      })
      .then((r) => r.data),

  getAccountDetails: (division: string, accountCode: string, country?: string): Promise<{ channel: { code: string; name: string } | null; subchannel: { code: string; name: string } | null }> =>
    api
      .get("/api/lookups/account-details", {
        params: { division, account_code: accountCode, country },
      })
      .then((r) => r.data),

  getSubchannelDetails: (division: string, subchannelCode: string, country?: string): Promise<{ channel: { code: string; name: string } | null }> =>
    api
      .get("/api/lookups/subchannel-details", {
        params: { division, subchannel_code: subchannelCode, country },
      })
      .then((r) => r.data),

  getBrandFamilyDetails: (division: string, brandFamilyCode: string, country?: string): Promise<{ brand: { code: string; name: string } | null }> =>
    api
      .get("/api/lookups/brand-family-details", {
        params: { division, brand_family_code: brandFamilyCode, country },
      })
      .then((r) => r.data),

  getBrandFamiliesByBrand: (division: string, brandCode: string, country?: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/brand-families-by-brand", {
        params: { division, brand_code: brandCode, country },
      })
      .then((r) => r.data),
};

export const snapshotApi = {
  create: (data: { period: string; year: string; ibp_step: string; is_final: boolean}) =>
    api.post("/api/snapshots", data).then((r) => r.data),
  getAll: () =>
    api.get<{ snapshots: any[] }>("/api/snapshots").then((r) => r.data),
  getById: (snapshotId: string) =>
    api.get(`/api/snapshots/${snapshotId}`).then((r) => r.data),
  delete: (snapshotId: string) =>
    api.delete(`/api/snapshots/${snapshotId}`).then((r) => r.data),
  updateFinal: (snapshotId: string, isFinal: boolean) =>
    api.patch(`/api/snapshots/${snapshotId}/final`, { isFinal }).then((r) => r.data),
};
