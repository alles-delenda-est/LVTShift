// ESLint flat config (Next.js 16 removed `next lint`; the ESLint CLI runs this
// directly). Same rule sets as the old .eslintrc.json:
// next/core-web-vitals + next/typescript.
import { defineConfig, globalIgnores } from "eslint/config";
import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

export default defineConfig([
  ...nextCoreWebVitals,
  ...nextTypescript,
  // Build output and generated files are not source code.
  globalIgnores([".next/**", "out/**", "build/**", "next-env.d.ts"]),
]);
