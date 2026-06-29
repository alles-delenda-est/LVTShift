import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Terre Productive",
  description: "Modélisation de la taxe foncière sur la valeur des terrains en France",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
