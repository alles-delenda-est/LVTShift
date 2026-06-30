import { loadIndex, loadValidation, loadRegister } from "@/lib/data";
import { pct } from "@/lib/format";
import type { ValidationCheck, RegisterCommune, RegisterCheck } from "@/lib/types";

export const metadata = {
  title: "Méthodologie — Pour une terre productive",
  description:
    "Transparence méthodologique complète : imputation de la valeur du sol, confrontation au réel, registre d'ingestion et limites documentées.",
};

// ── Helpers ────────────────────────────────────────────────────────────────

function indepLabel(ind: string): string {
  if (ind === "independent") return "indépendant";
  if (ind === "data-quality") return "qualité des données";
  return ind;
}

/** Best comparable percentage for the given check, regardless of field name. */
function comparableValue(c: ValidationCheck): string {
  // Check 1 (vacance): standard field
  if (c.model_comparable_pct != null) {
    return pct(c.model_comparable_pct);
  }
  // Check 2 (part foncière): stored in extra field
  const lsp = c["model_land_share_pct"];
  if (typeof lsp === "number") return pct(lsp);
  // Check 3 (carte bâti): stored in extra field
  const bsp = c["model_built_share_pct"];
  if (typeof bsp === "number") return pct(bsp);
  return "—";
}

/** Descriptive label for the comparable value. */
function comparableLabel(c: ValidationCheck): string | null {
  if (c.model_comparable_label) return c.model_comparable_label;
  const lsp = c["model_land_share_pct"];
  if (typeof lsp === "number") return "part foncière modélisée";
  const bsp = c["model_built_share_pct"];
  if (typeof bsp === "number") return "part bâtie BD TOPO";
  return null;
}

// ── Badge sub-components (no state — safe in Server Component) ─────────────

function StatusBadge({ status }: { status: string }) {
  if (status === "ok") {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[0.6rem] font-semibold uppercase tracking-wide bg-marine/10 text-marine">
        ok
      </span>
    );
  }
  if (status === "non disponible") {
    return <span className="text-xs text-gris italic">non disponible</span>;
  }
  if (status === "flag") {
    return (
      <span className="inline-flex items-center px-1.5 py-0.5 text-[0.6rem] font-semibold uppercase tracking-wide bg-amber-100 text-amber-700">
        signal
      </span>
    );
  }
  return <span className="text-xs text-gris">{status}</span>;
}

function VerdictBadge({ verdict }: { verdict: "OK" | "WARN" | "FAIL" }) {
  const cls =
    verdict === "OK"
      ? "bg-marine/10 text-marine"
      : verdict === "WARN"
        ? "bg-amber-100 text-amber-700"
        : "bg-rouge/10 text-rouge";
  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 text-[0.6rem] font-semibold uppercase tracking-wide ${cls}`}
    >
      {verdict}
    </span>
  );
}

// ── Pre-processed row shapes ───────────────────────────────────────────────

interface ValidationRow {
  communeName: string;
  communeKey: string;
  isFirst: boolean;
  rowSpan: number;
  check: ValidationCheck;
}

type RegisterDisplayRow =
  | { type: "main"; rc: RegisterCommune }
  | {
      type: "detail";
      rowKey: string;
      ch: RegisterCheck;
      verdict: "OK" | "WARN" | "FAIL";
    };

// ── Page ──────────────────────────────────────────────────────────────────

export default function MethodologiePage() {
  const { communes } = loadIndex();
  const { communes: registerCommunes } = loadRegister();

  // Validation rows: flatten all checks across all modellable communes
  const validationRows: ValidationRow[] = communes.flatMap((c) => {
    const validation = loadValidation(c.commune_key);
    if (!validation) return [];
    return validation.checks.map((check, i) => ({
      communeName: c.name,
      communeKey: c.commune_key,
      isFirst: i === 0,
      rowSpan: validation.checks.length,
      check,
    }));
  });

  // Register display rows: each commune row optionally followed by WARN/FAIL detail rows
  const registerRows: RegisterDisplayRow[] = [];
  for (const rc of registerCommunes) {
    registerRows.push({ type: "main", rc });
    for (const ch of rc.checks.filter((c) => c.severity !== "OK")) {
      registerRows.push({
        type: "detail",
        rowKey: `${rc.commune_key}-${ch.check}`,
        ch,
        verdict: rc.verdict,
      });
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      {/* ── Page header ──────────────────────────────────────────────── */}
      <div className="mb-10 border-b border-lisere pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">
          Transparence méthodologique
        </p>
        <h2 className="font-display text-2xl md:text-[1.75rem] font-medium text-marine leading-tight mb-3">
          Méthodologie
        </h2>
        <p className="font-body text-base text-gris max-w-2xl leading-relaxed">
          Comment la valeur du sol est estimée parcelle par parcelle, comment
          les résultats sont confrontés à des données indépendantes, et quelles
          sont les limites documentées du modèle. Ce document est destiné aux
          journalistes, décideurs et pairs qui souhaitent évaluer la rigueur du
          travail.
        </p>
      </div>

      {/* ── Section (a) : Imputation ──────────────────────────────────── */}
      <section className="mb-12">
        <h3 className="font-display text-xl font-medium text-marine mb-4">
          Comment la valeur du sol est imputée
        </h3>
        <div className="font-body text-base text-encre leading-relaxed space-y-4 max-w-3xl">
          <p>
            La France ne dispose d&apos;aucune évaluation officielle séparée
            du terrain et du bâti parcelle par parcelle. La valeur du sol est
            donc <strong>imputée</strong> à partir de données ouvertes
            exclusivement, selon une méthode en deux temps :{" "}
            <em>classer, puis valoriser</em>.
          </p>

          <p>
            <strong>Pour chaque parcelle bâtie,</strong> on estime d&apos;abord
            la valeur du bâtiment — coût de remplacement déprécié : emprise
            au sol × nombre d&apos;étages × coût de construction au m² ×
            coefficient de dépréciation linéaire calculé à partir de
            l&apos;année de construction (fournie par les diagnostics
            énergétiques DPE de l&apos;ADEME). On soustrait ensuite cette
            valeur bâtie à la valeur de marché estimée par régression
            hédonique sur les ventes DVF des cinq dernières années. Le
            résiduel est la valeur imputée du sol.
          </p>

          <p>
            <strong>Pour les parcelles non bâties,</strong> la méthode est
            différente : le zonage du Plan Local d&apos;Urbanisme (GPU, via
            le Géoportail de l&apos;Urbanisme) détermine la catégorie de
            constructibilité de chaque parcelle. Les parcelles constructibles
            sont valorisées à partir des prix de terrains à bâtir extraits de
            DVF ; les terres agricoles ou naturelles sont valorisées au
            barème SAFER (prix au m² par département). On ne leur applique
            pas le résiduel marché&nbsp;&minus;&nbsp;bâti, dont la fiabilité
            serait nulle en l&apos;absence de bâtiment.
          </p>

          <p>
            Cette approche <em>classer-puis-valoriser</em> remplace une
            méthode antérieure qui appliquait une part foncière uniforme à
            toutes les parcelles — source d&apos;artefacts importants dans
            les communes rurales. Désormais, le foncier agricole et naturel
            ne représente qu&apos;une fraction infime de l&apos;assiette
            imposable (de l&apos;ordre de 0,3&nbsp;% à Cahors) ;
            l&apos;essentiel de la valeur du sol provient du foncier urbain
            constructible.
          </p>

          <div className="border-l-4 border-lisere pl-5 text-sm text-gris">
            <strong className="font-semibold text-encre">
              Bande de sensibilité ±&thinsp;10 points de pourcentage.
            </strong>{" "}
            L&apos;hypothèse de part foncière est la principale source
            d&apos;incertitude du modèle. Tous les résultats de titre sont
            accompagnés d&apos;une fourchette calculée en faisant varier la
            part foncière de ±&thinsp;10 points : si la part imputée est de
            60&nbsp;%, les chiffres sont vérifiés à 50&nbsp;% et 70&nbsp;%.
            Cette bande n&apos;est pas une correction — c&apos;est une
            mesure explicite de l&apos;incertitude.
          </div>
        </div>
      </section>

      {/* ── Section (b) : Validation table ───────────────────────────── */}
      <section className="mb-12 border-t border-lisere pt-10">
        <h3 className="font-display text-xl font-medium text-marine mb-2">
          « Confronter le modèle au réel »
        </h3>
        <p className="font-body text-sm text-gris max-w-2xl leading-relaxed mb-6">
          Ces contrôles sont des <strong>vérifications</strong>, jamais des
          cibles de calage : le modèle n&apos;a pas été ajusté pour les
          satisfaire. Les contrôles <em>indépendants</em> s&apos;appuient sur
          des sources extérieures au modèle ; les contrôles{" "}
          <em>qualité des données</em> comparent deux cartes du bâti produites
          indépendamment par des agences différentes.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <caption className="sr-only">
              Contrôles de validation par commune et par benchmark
            </caption>
            <thead>
              <tr className="border-b-2 border-lisere">
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6 w-28"
                >
                  Commune
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6"
                >
                  Benchmark
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6 w-36"
                >
                  Indépendance
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6"
                >
                  Comparable (modèle)
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2"
                >
                  Statut
                </th>
              </tr>
            </thead>
            <tbody>
              {validationRows.map(
                ({ communeName, communeKey, isFirst, rowSpan, check }, idx) => (
                  <tr
                    key={`${communeKey}-${idx}`}
                    className="border-b border-lisere last:border-0"
                  >
                    {isFirst && (
                      <td
                        rowSpan={rowSpan}
                        className="py-3 pr-6 align-top font-display font-medium text-marine whitespace-nowrap"
                      >
                        {communeName}
                      </td>
                    )}
                    <td className="py-3 pr-6 text-encre align-top leading-snug">
                      {check.benchmark}
                    </td>
                    <td className="py-3 pr-6 text-gris align-top text-xs leading-snug">
                      {indepLabel(check.independence)}
                    </td>
                    <td className="py-3 pr-6 align-top">
                      <span className="font-body text-encre">
                        {comparableValue(check)}
                      </span>
                      {comparableLabel(check) && (
                        <span className="block text-xs text-gris mt-0.5 leading-snug">
                          {comparableLabel(check)}
                        </span>
                      )}
                    </td>
                    <td className="py-3 align-top">
                      <StatusBadge status={check.status} />
                      {check.note && (
                        <p className="text-xs text-gris mt-1.5 leading-relaxed max-w-[16rem]">
                          {check.note}
                        </p>
                      )}
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Section (c) : Ingestion register ─────────────────────────── */}
      <section className="mb-12 border-t border-lisere pt-10">
        <h3 className="font-display text-xl font-medium text-marine mb-2">
          Registre d&apos;ingestion
        </h3>
        <p className="font-body text-sm text-gris max-w-2xl leading-relaxed mb-5">
          Le registre documente la couverture des données source pour chaque
          commune candidate. Un verdict{" "}
          <span className="font-semibold text-rouge">FAIL</span> signifie que
          la commune ne peut pas être modélisée par la présente méthode, avec
          la cause documentée.{" "}
          <span className="font-semibold text-amber-700">WARN</span> signifie
          une limitation qui ne bloque pas la modélisation mais doit être
          signalée.
        </p>

        <div className="mb-6 border-l-4 border-rouge pl-5 max-w-2xl">
          <p className="text-sm text-encre leading-relaxed">
            <strong>Mulhouse — exclusion structurelle.</strong> Les ventes
            immobilières dans les départements 57, 67 et 68 (Alsace-Moselle)
            sont enregistrées au <em>Livre Foncier</em>, issu du droit local
            d&apos;origine germanique, et n&apos;alimentent pas le jeu de
            données DVF ouvert publié par le DGFiP. Sans données de ventes,
            aucun modèle hédonique ne peut être calibré et aucun prix de
            terrain à bâtir ne peut être établi.{" "}
            <strong>
              Mulhouse n&apos;est pas modélisable par cette méthode
            </strong>{" "}
            — ce n&apos;est pas une lacune transitoire corrigeable par un
            nouvel essai, c&apos;est une frontière structurelle. La seule
            piste serait une ingestion directe du Livre Foncier (DGFiP /
            ANCT).
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <caption className="sr-only">
              Registre d&apos;ingestion par commune
            </caption>
            <thead>
              <tr className="border-b-2 border-lisere">
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-6 w-32"
                >
                  Commune
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-4 w-24"
                >
                  Modélisable
                </th>
                <th
                  scope="col"
                  className="text-left text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-4 w-20"
                >
                  Verdict
                </th>
                <th
                  scope="col"
                  className="text-right text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 pr-4 w-16"
                >
                  Échecs
                </th>
                <th
                  scope="col"
                  className="text-right text-xs font-semibold uppercase tracking-[0.12em] text-gris pb-2 w-16"
                >
                  Alertes
                </th>
              </tr>
            </thead>
            <tbody>
              {registerRows.map((row) => {
                if (row.type === "main") {
                  const rc = row.rc;
                  const rowBg =
                    rc.verdict === "FAIL"
                      ? "border-rouge/20 bg-red-50/40"
                      : "border-lisere";
                  return (
                    <tr key={rc.commune_key} className={`border-b ${rowBg}`}>
                      <td className="py-2.5 pr-6 font-display font-medium text-marine">
                        {rc.name}
                      </td>
                      <td className="py-2.5 pr-4 text-encre">
                        {rc.modellable ? (
                          "oui"
                        ) : (
                          <span className="font-semibold text-rouge">non</span>
                        )}
                      </td>
                      <td className="py-2.5 pr-4">
                        <VerdictBadge verdict={rc.verdict} />
                      </td>
                      <td className="py-2.5 pr-4 text-right">
                        {rc.n_fail > 0 ? (
                          <span className="font-semibold text-rouge">
                            {rc.n_fail}
                          </span>
                        ) : (
                          <span className="text-gris">0</span>
                        )}
                      </td>
                      <td className="py-2.5 text-right">
                        {rc.n_warn > 0 ? (
                          <span className="text-amber-600">{rc.n_warn}</span>
                        ) : (
                          <span className="text-gris">0</span>
                        )}
                      </td>
                    </tr>
                  );
                }

                // Detail row for WARN / FAIL checks
                const detailBg =
                  row.verdict === "FAIL"
                    ? "border-rouge/20 bg-red-50/40"
                    : "border-amber-100 bg-amber-50/30";
                const badgeCls =
                  row.ch.severity === "FAIL"
                    ? "bg-rouge/10 text-rouge"
                    : "bg-amber-100 text-amber-700";
                return (
                  <tr key={row.rowKey} className={`border-b ${detailBg}`}>
                    <td className="pt-0 pb-2.5 pl-4 pr-6" colSpan={2}>
                      <span
                        className={`inline-flex items-center px-1 py-0 text-[0.55rem] font-semibold uppercase tracking-wide mr-2 ${badgeCls}`}
                      >
                        {row.ch.severity}
                      </span>
                      <span className="text-xs text-encre">
                        {row.ch.message}
                      </span>
                    </td>
                    <td className="pt-0 pb-2.5 text-xs text-gris italic" colSpan={3}>
                      {row.ch.adaptation ?? ""}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Section (d) : Honest limits ──────────────────────────────── */}
      <section className="mb-10 border-t border-lisere pt-10">
        <h3 className="font-display text-xl font-medium text-marine mb-4">
          Limites et réserves honnêtes
        </h3>
        <div className="space-y-7 max-w-3xl">
          {/* Paris */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Paris — absent du panel
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              Paris forme une commune unique dont les données cadastrales et DVF
              sont disponibles, mais dont la taille rend l&apos;ingestion en
              données ouvertes infaisable à l&apos;échelle de ce projet pilote.
              De plus, les arrondissements parisiens n&apos;ont pas de produit
              de taxe foncière propre — la TFPB est prélevée par la ville et la
              métropole — ce qui interdit d&apos;isoler une cible de neutralité
              par arrondissement. Paris est donc absent du panel, non par
              lacune des données, mais par impossibilité d&apos;ingestion à
              cette échelle avec les ressources du pilote.
            </p>
          </div>

          {/* Mulhouse */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Mulhouse — non-modélisable (Alsace-Moselle)
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              Les départements 57 (Moselle), 67 (Bas-Rhin) et 68 (Haut-Rhin)
              relèvent d&apos;un droit local hérité du code civil allemand :
              les ventes immobilières y sont transcrites au{" "}
              <em>Livre Foncier</em>, registre que le DGFiP ne verse pas au
              jeu de données DVF ouvert. Sans données de ventes, la régression
              hédonique est impossible et aucune valeur de terrain à bâtir ne
              peut être établie. Mulhouse est documentée dans le registre
              comme une frontière structurelle — pas une lacune transitoire
              corrigeable par un nouvel essai ou un meilleur accès réseau.
            </p>
          </div>

          {/* Construction cost caveat */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Coûts de construction — gradient régional pilote
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              Les coûts de construction au m² utilisés pour estimer la valeur
              du bâti (de 1&thinsp;600&thinsp;€/m² à Figeac à
              2&thinsp;150&thinsp;€/m² en Île-de-France) sont des valeurs
              pilotes fondées sur un gradient régional grossier, en attente
              d&apos;un calage sur les indices FFB&nbsp;/&nbsp;BT01. Un écart
              de ±&thinsp;15&nbsp;% sur ce paramètre se propage linéairement
              dans la valeur bâti et, par conséquent, dans le résiduel
              foncier. C&apos;est la raison pour laquelle le registre signale
              en WARN les communes dont la part foncière imputée dépasse la
              bande 40–65&nbsp;% (6 communes sur 9 dans le panel) : cette
              anomalie peut indiquer un bâti sous-évalué et un résiduel
              foncier correspondamment surestimé — autant qu&apos;un marché
              foncier effectivement très tendu. Les deux lectures sont
              plausibles, et il serait trompeur de trancher sans calage. La
              bande de sensibilité ±&thinsp;10 points encadre cette
              incertitude dans tous les résultats publiés.
            </p>
          </div>

          {/* Small commune quintile gap */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Petites communes — analyse par quintile de revenu non publiée
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              L&apos;analyse distributive par quintile de revenu repose sur les
              données Filosofi (INSEE) à l&apos;échelle des IRIS. Dans les
              communes disposant de peu d&apos;IRIS distincts — en particulier
              Cahors et Figeac — le nombre de revenus IRIS distincts est
              insuffisant pour former cinq quintiles stables. Pour ces
              communes, l&apos;exportateur émet{" "}
              <code className="text-xs font-mono bg-lisere px-1">null</code>{" "}
              pour la décomposition par quintile, et aucun graphique de revenu
              n&apos;est publié. Cela est documenté dans le registre
              d&apos;ingestion pour chaque commune concernée.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
