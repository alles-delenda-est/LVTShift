import createMDX from "@next/mdx";

const withMDX = createMDX({});

const rawBasePath = process.env.NEXT_PUBLIC_BASE_PATH?.trim() ?? "";
const basePath =
  rawBasePath && rawBasePath !== "/" ? rawBasePath.replace(/\/+$/, "") : "";

/** @type {import('next').NextConfig} */
const nextConfig = {
  // The whole site is static (build-time data, no server routes), so export it
  // to a plain `out/` directory. This makes the Vercel deploy independent of the
  // Root Directory picker: a repo-root vercel.json builds this subfolder and
  // serves out/ as static files. When NEXT_PUBLIC_BASE_PATH is set (e.g.
  // "/LVTShift" for the GitHub Pages mirror), export with basePath and
  // trailingSlash so every route resolves cleanly to <route>/index.html.
  output: "export",
  ...(basePath ? { basePath, trailingSlash: true } : {}),
  pageExtensions: ["ts", "tsx", "js", "jsx", "md", "mdx"],
  images: { unoptimized: true },
};

export default withMDX(nextConfig);
