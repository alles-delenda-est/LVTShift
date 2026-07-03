// Lets TypeScript resolve `import Content from "@/content/pagers/*.mdx"`.
declare module "*.mdx" {
  import type { ComponentType } from "react";
  const MDXComponent: ComponentType<Record<string, unknown>>;
  export default MDXComponent;
}
