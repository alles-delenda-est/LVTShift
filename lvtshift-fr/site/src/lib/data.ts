import fs from "node:fs";
import path from "node:path";
import type { Commune, IndexCommune, ValidationCheck, RegisterCommune } from "@/lib/types";

const DATA = path.join(process.cwd(), "public", "data");
function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(path.join(DATA, file), "utf-8")) as T;
}
// Commune keys are open-data slugs; reject anything that could escape DATA/.
function assertKey(key: string): void {
  if (!/^[a-z0-9_-]+$/.test(key)) throw new Error(`invalid commune key: ${key}`);
}
export function loadIndex(): { communes: IndexCommune[]; currency: string } {
  return readJson("index.json");
}
export function communeKeys(): string[] {
  return loadIndex().communes.map((c) => c.commune_key);
}
export function loadCommune(key: string): Commune {
  assertKey(key);
  return readJson<Commune>(`${key}.json`);
}
export function loadValidation(key: string): { checks: ValidationCheck[] } | null {
  assertKey(key);
  try {
    return readJson(`${key}.validation.json`);
  } catch (e) {
    // A missing validation file is expected (null); anything else is a real
    // problem (malformed JSON, permissions) and must surface at build time.
    if ((e as NodeJS.ErrnoException).code === "ENOENT") return null;
    throw e;
  }
}
export function loadRegister(): { communes: RegisterCommune[] } {
  return readJson("ingestion_register.json");
}
