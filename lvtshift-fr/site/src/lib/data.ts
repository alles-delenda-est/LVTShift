import fs from "node:fs";
import path from "node:path";
import type { Commune, IndexCommune, ValidationCheck, RegisterCommune } from "@/lib/types";

const DATA = path.join(process.cwd(), "public", "data");
function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(path.join(DATA, file), "utf-8")) as T;
}
export function loadIndex(): { communes: IndexCommune[]; currency: string } {
  return readJson("index.json");
}
export function communeKeys(): string[] {
  return loadIndex().communes.map((c) => c.commune_key);
}
export function loadCommune(key: string): Commune {
  return readJson<Commune>(`${key}.json`);
}
export function loadValidation(key: string): { checks: ValidationCheck[] } | null {
  try { return readJson(`${key}.validation.json`); } catch { return null; }
}
export function loadRegister(): { communes: RegisterCommune[] } {
  return readJson("ingestion_register.json");
}
