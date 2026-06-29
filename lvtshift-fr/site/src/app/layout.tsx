import "./globals.css";
import type { ReactNode } from "react";
import { EB_Garamond, Source_Serif_4 } from "next/font/google";
import Identity from "@/components/Identity";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";

const garamond = EB_Garamond({
  subsets: ["latin", "latin-ext"],
  variable: "--font-display",
  display: "swap",
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
});

const sourceSerif = Source_Serif_4({
  subsets: ["latin", "latin-ext"],
  variable: "--font-body",
  display: "swap",
  weight: ["300", "400", "600"],
  style: ["normal", "italic"],
});

export const metadata = {
  title: "Pour une terre productive",
  description:
    "Modélisation d'une réforme de la taxe foncière sur la valeur des terrains en France — Récompenser le travail, décourager la rente.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="fr"
      className={`${garamond.variable} ${sourceSerif.variable}`}
    >
      <body className="min-h-screen flex flex-col bg-creme text-encre">
        <header>
          <Identity />
          <Nav />
        </header>
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
