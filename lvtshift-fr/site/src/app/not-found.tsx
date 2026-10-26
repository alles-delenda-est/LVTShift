import Link from "next/link";

export const metadata = {
  title: "Page introuvable — Pour une terre productive",
};

// French replacement for Next.js's default English 404 page.
export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">Erreur 404</p>
      <h2 className="font-display text-2xl md:text-[1.9rem] font-medium text-marine leading-tight mb-4">
        Cette page n&apos;existe pas
      </h2>
      <p className="font-body text-base text-encre leading-relaxed mb-6">
        L&apos;adresse a peut-être changé, ou contient une faute de frappe.
      </p>
      <p className="font-body text-base">
        <Link href="/" className="text-rouge underline underline-offset-2 hover:text-marine">
          Retour à l&apos;accueil
        </Link>
        {" · "}
        <Link href="/resultats" className="text-rouge underline underline-offset-2 hover:text-marine">
          Résultats par commune
        </Link>
      </p>
    </div>
  );
}
