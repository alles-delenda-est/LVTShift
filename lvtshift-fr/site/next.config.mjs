import createMDX from "@next/mdx";

const withMDX = createMDX({});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // The whole site is static (build-time data, no server routes), so export it
  // to a plain `out/` directory. This makes the Vercel deploy independent of the
  // Root Directory picker: a repo-root vercel.json builds this subfolder and
  // serves out/ as static files.
  output: "export",
  pageExtensions: ["ts", "tsx", "js", "jsx", "md", "mdx"],
  images: { unoptimized: true },
};

export default withMDX(nextConfig);
