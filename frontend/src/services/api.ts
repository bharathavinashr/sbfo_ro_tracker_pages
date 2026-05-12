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
  
  getBrands: (division: string): Promise<{ options: { value: string; label: string }[] }> =>
    api
      .get("/api/lookups/brands", {
        params: { division },
      })
      .then((r) => r.data),
  
  getBrandFamilies: (brandNames: string[]): Promise<{ options: { value: string; label: string }[] }> => {
    const params = new URLSearchParams();
    brandNames.forEach((n) => params.append("brand_names", n));
    return api
      .get("/api/lookups/brand-families", { params })
      .then((r) => r.data);
  },
};

export const snapshotApi = {
  create: (data: { period: string; year: string; department: string }) =>
    api.post("/api/snapshots", data).then((r) => r.data),
  getAll: () =>
    api.get<{ snapshots: any[] }>("/api/snapshots").then((r) => r.data),
  getById: (snapshotId: string) =>
    api.get(`/api/snapshots/${snapshotId}`).then((r) => r.data),
  delete: (snapshotId: string) =>
    api.delete(`/api/snapshots/${snapshotId}`).then((r) => r.data),
};
