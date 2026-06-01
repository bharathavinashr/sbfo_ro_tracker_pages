import { createRouter, createWebHistory } from "vue-router";
import MainPage from "@/pages/MainPage.vue";
import EntryHistoryPage from "@/pages/EntryHistoryPage.vue";
import CycleSnapshotsPage from "@/pages/CycleSnapshotsPage.vue";
import SnapshotDetailPage from "@/pages/SnapshotDetailPage.vue";
import SnapshotHistoryPage from "@/pages/SnapshotHistoryPage.vue";

const routes = [
  { path: "/", component: MainPage },
  { path: "/entry/:originalEntryId/history", component: EntryHistoryPage },
  { path: "/snapshots", component: CycleSnapshotsPage },
  { path: "/snapshots/:snapshotId", component: SnapshotDetailPage },
  { path: "/snapshot-history", component: SnapshotHistoryPage },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
