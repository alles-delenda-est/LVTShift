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
            la valeur du bâtiment — coût de remplacement déprécié : surface
            habitable (emprise au sol × nombre d&apos;étages, ramenée à la
            surface habitable) × coût de construction au m² habitable ×
            coefficient de dépréciation linéaire calculé à partir de
            l&apos;année de construction (fournie par les diagnostics
            énergétiques DPE de l&apos;ADEME). Là où les prix du quartier
            dépassent nettement le coût de reconstruction, le bâti est
            entretenu et rénové en continu : un immeuble ancien y est
            valorisé comme s&apos;il avait au plus une trentaine
            d&apos;années (« âge effectif »), avec une transition progressive
            selon le niveau de prix des parcelles bâties de l&apos;IRIS. On soustrait ensuite cette
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
            <strong>Le foncier public exonéré</strong> (ministères, hôpitaux
            publics, écoles, mairies, parcs…) ne paie pas la taxe foncière
            aujourd&apos;hui et n&apos;en paierait pas davantage dans la
            simulation. Il est repéré grâce aux fichiers de la DGFiP sur les
            biens des personnes morales, selon une règle prudente : une
            parcelle n&apos;est retenue que si tous ses titulaires de droits
            sont des personnes publiques en pleine propriété, sans bail ni
            copropriété. À Paris, ces parcelles portaient 4,9&nbsp;% du produit
            que le modèle leur attribuait auparavant ; ce montant est désormais
            réparti sur les parcelles réellement imposables.{" "}
            <strong>Les bâtiments agricoles</strong> (serres, granges, silos,
            étables) sont eux aussi exonérés de taxe foncière bâtie, à raison
            de leur usage et non de leur propriétaire&nbsp;: le modèle les
            repère par l&apos;usage « Agricole » de la BD TOPO ou, pour les
            hangars sans usage renseigné, par leur situation en zone agricole
            ou naturelle du PLU, et une parcelle qui ne porte que de tels
            bâtiments est traitée comme une terre agricole non bâtie (Périgny,
            commune des serres, passe ainsi de 41,8&nbsp;% à 47,9&nbsp;% de
            part foncière).
          </p>

          <p>
            <strong>Entrepôts, ateliers et autres locaux d&apos;activité.</strong>{" "}
            Chaque bâtiment est classé d&apos;après la BD TOPO : hangar,
            atelier, grande surface, bureaux, hangar agricole, serre, salle de
            sport, annexe, lieu de culte ou logement. Chaque type a son propre
            coût de construction, exprimé en proportion de celui du logement
            collectif (un entrepôt coûte environ le quart d&apos;un immeuble au
            m², des bureaux environ 80&nbsp;%), hors TVA pour les entreprises
            qui la récupèrent, ainsi que sa propre durée de vie (40 ans pour
            un entrepôt, 60 pour des bureaux, 80 pour le logement). Un
            entrepôt ou une grande surface se vend rarement : on ne peut donc
            pas lui appliquer le prix au m² des appartements. Les parcelles
            dont le plus grand bâtiment est de ce type sont évaluées comme le
            font les experts pour les biens sans marché, par la méthode
            « sol + construction » : le bâtiment à son coût de reconstruction
            déprécié, le terrain au prix local des terrains à bâtir, réduit
            pour le foncier d&apos;activité (× 0,45 autour de Paris et
            ailleurs, × 0,35 autour de Lyon, d&apos;après les ventes de terrains
            d&apos;activité enregistrées dans DVF). Hors zone urbaine, seule
            une cour autour du bâtiment est comptée comme terrain à bâtir, le
            reste comme terre agricole. Les bureaux, qui se vendent, restent
            évalués par le résiduel. Ces coûts reposent sur un seul guide
            professionnel et sont à ±&thinsp;25&nbsp;% près.
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
          {/* Today's-tax baseline: calibrated by tax group, with a range */}
          <div className="border-l-4 border-lisere pl-5">
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Taxe actuelle — calée sur les comptes officiels de chaque commune
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed mb-3">
              Pour savoir qui gagne et qui perd, il faut d&apos;abord savoir
              qui paie quoi aujourd&apos;hui. Le montant total de la taxe
              foncière de chaque commune est connu exactement, mais pas sa
              répartition entre logements, bureaux, commerces et usines : les
              valeurs locatives par local ne sont pas ouvertes. Le modèle
              reconstitue donc, pour chaque commune, la part de la taxe payée
              par trois groupes, à partir du recensement officiel des impôts
              locaux (REI, DGFiP) :
            </p>
            <ul className="font-body text-sm text-encre leading-relaxed list-disc pl-5 space-y-1.5 mb-3">
              <li>
                <strong>les établissements industriels</strong>, à partir de la
                compensation que l&apos;État verse aux communes depuis la
                division par deux de leurs valeurs en 2021 (loi de finances
                pour 2021, art. 29). Appliquée à toute la France, cette méthode
                retrouve exactement la part publiée par la Cour des comptes
                (5,7&nbsp;%) ;
              </li>
              <li>
                <strong>les locaux professionnels</strong> (bureaux, commerces,
                entrepôts), à partir de leur base de cotisation foncière des
                entreprises (CFE). La CFE n&apos;est payée que par les
                occupants : les locaux vides et certains occupants, comme les
                administrations, en sont absents. Brute, elle ne retrouve
                qu&apos;environ 40&nbsp;% de la part nationale des locaux
                professionnels mesurée par la Cour des comptes ; le modèle la
                multiplie donc par 2,5 ;
              </li>
              <li>
                <strong>les logements et le reste</strong>, qui paient le solde.
              </li>
            </ul>
            <p className="font-body text-sm text-encre leading-relaxed mb-3">
              Chaque groupe paie sa part, répartie ensuite entre ses bâtiments
              selon leur surface de plancher. Le résultat contredit ce que
              l&apos;on attendait : au m², les entreprises paient aujourd&apos;hui
              plus que les logements. Les valeurs industrielles comprennent
              les machines et installations fixes, et les locaux
              professionnels ont été réévalués sur les loyers de 2013, alors
              que les logements restent évalués sur ceux de 1970. La réforme
              déplace donc davantage la charge des entreprises vers les
              ménages. Dans le couloir chimique et industriel lyonnais, dans le
              cas central, elle fait baisser l&apos;impôt de l&apos;industrie
              et monter celui des ménages.
            </p>
            <p className="font-body text-sm text-encre leading-relaxed mb-3">
              <strong>
                Le facteur de 2,5 est aujourd&apos;hui la principale source
                d&apos;incertitude sur les résultats par revenu.
              </strong>{" "}
              Sans lui (borne basse), la taxe actuelle des locaux
              professionnels est plus faible, et les ménages paraissent plus
              gagnants de 10 à 15 points : à Paris, le cinquième le plus
              modeste voit son impôt baisser de 17&nbsp;% dans le cas central,
              de 28&nbsp;% en borne basse ; dans la couronne lyonnaise, il
              augmente de 1&nbsp;% dans le cas central et baisse de 16&nbsp;%
              en borne basse. Les nouvelles cotisations sont les mêmes dans les
              deux cas : seul le point de départ change. Le facteur 2,5 est le
              mieux étayé, mais un multiplicateur national unique ne peut
              convenir à chaque commune. Seuls les Fichiers fonciers, qui
              donnent la valeur réelle de chaque local, trancheraient. La page
              de résultats présente donc les deux colonnes côte à côte, cas
              central et borne basse, dans le tableau «&nbsp;Incertitude sur
              la taxe actuelle des locaux professionnels&nbsp;».
            </p>
            <p className="font-body text-sm text-encre leading-relaxed">
              <strong>Les machines.</strong> Par choix, la réforme modélisée
              taxe le sol et les bâtiments, pas les machines et installations
              fixes des usines, pour ne pas pénaliser l&apos;investissement.
              Ce choix pèse peu : les taxer ne déplacerait l&apos;impôt
              industriel que de 1 à 3 points (dans la couronne lyonnaise, la
              baisse passerait de 63&nbsp;% à 60–62&nbsp;%). Elle tient
              surtout à un foncier industriel bon marché.
            </p>
          </div>

          {/* Paris & Lyon, and the inner rings */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Paris, Lyon et leurs couronnes — comment ils sont modélisés
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed mb-3">
              Paris et Lyon publient leurs données cadastrales, de ventes (DVF),
              de diagnostics (DPE) et de revenus (IRIS) par arrondissement, mais
              la taxe foncière est votée et perçue par la commune entière (Paris
              75056, Lyon 69123 — et, à Lyon, une petite part par la Métropole).
              Les arrondissements sont donc assemblés en une seule commune et
              résolus avec un taux unique, comme l&apos;impôt réel : il
              n&apos;existe pas de produit fiscal par arrondissement.
            </p>
            <p className="font-body text-sm text-encre leading-relaxed">
              Les couronnes — « Paris extra-muros » (les 122 communes des
              Hauts-de-Seine, de la Seine-Saint-Denis et du Val-de-Marne) et
              « Lyon extra-muros » (les 57 autres communes de la Métropole de
              Lyon) — ne sont pas modélisées comme un impôt métropolitain unique.
              Chaque commune est résolue séparément, à recettes constantes sur son
              propre produit, puis les résultats sont agrégés ; la bande de
              sensibilité est elle aussi recalculée commune par commune. Les
              quintiles de revenu y sont classés à l&apos;échelle de toute la
              couronne. Montreuil et Villeurbanne figurent à la fois seules et
              dans leur couronne ; les totaux du panel ne les comptent qu&apos;une
              fois.
            </p>
            <p className="font-body text-sm text-encre leading-relaxed mt-3">
              <strong>Paris et la borne de 85&nbsp;%.</strong> Une règle de
              dépréciation purement liée à l&apos;âge ramenait un immeuble
              parisien d&apos;environ 95 ans, pourtant entretenu en continu, à
              25&nbsp;% de son coût de reconstruction — environ
              575&nbsp;€/m², face à un prix de vente médian d&apos;environ
              10&nbsp;860&nbsp;€/m². 95,5&nbsp;% des parcelles bâties
              parisiennes atteignaient alors le plafond de 85&nbsp;% : le
              partage terrain/bâti était fixé par la borne, pas mesuré. Avec
              la règle de l&apos;âge effectif décrite plus haut, une valeur de
              marché et une valeur du bâti calculées toutes deux sur la surface
              habitable, des coûts de construction recalés et une
              valorisation propre aux locaux d&apos;activité, la part
              foncière de Paris ressort à 75,8&nbsp;%, avec 5,6&nbsp;% des
              parcelles bâties au plafond : elle est désormais mesurée.
              Aucune commune n&apos;a plus de la moitié de ses parcelles
              bâties au plafond (Neuilly-sur-Seine en a le plus,
              25,3&nbsp;%). Lyon est à 60,0&nbsp;%. Les prix de vente sont d&apos;abord ramenés en euros 2025 par
              l&apos;indice Notaires-INSEE le plus local (appartements
              parisiens, départements de petite couronne, agglomération
              lyonnaise…), ce qui retire le pic de 2021–2022.
            </p>
          </div>

          {/* Income groups */}
          <div>
            <h4 className="font-body text-sm font-semibold text-encre uppercase tracking-[0.1em] mb-1.5">
              Groupes de revenu — totaux et ménages, pas parcelles
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              Pour chaque quintile de revenu, la barre donne la variation de
              l&apos;impôt payé par l&apos;ensemble des logements du groupe, et
              le losange celle du ménage type : chaque parcelle y compte autant
              de fois qu&apos;elle a de logements. Une simple médiane par
              parcelle compterait un immeuble de 200 logements une seule fois,
              comme une maison. À Villeurbanne, elle montrerait le quintile le
              plus pauvre en hausse (+7,6&nbsp;%), alors que ce groupe paie
              6,3&nbsp;% de moins au total et que son ménage type paie
              6,1&nbsp;% de moins : les grands immeubles, où vit la plupart de
              ses ménages, sont les plus gagnants. Le nombre de logements vient
              de la BD TOPO de l&apos;IGN ; il est estimé pour 5 à 11&nbsp;% des
              parcelles résidentielles qui n&apos;en ont pas.
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
              Coûts de construction et surface habitable
            </h4>
            <p className="font-body text-sm text-encre leading-relaxed">
              Les coûts de construction de Paris (2&thinsp;650&thinsp;€/m²),
              de la petite couronne (2&thinsp;400&thinsp;€/m²), de Lyon et
              Villeurbanne (2&thinsp;000&thinsp;€/m²) et de la couronne
              lyonnaise (1&thinsp;850&thinsp;€/m²) sont calés sur le coût du
              bâtiment des logements sociaux neufs publié par le ministère
              (DHUP/SISAL), ramené en euros 2025 par l&apos;indice BT01 :
              bâtiment seul, par m² de surface brute, honoraires et TVA
              compris. Ce coût étant celui du logement collectif, les maisons
              de ces territoires ont leur propre coût, tiré de l&apos;enquête
              du SDES sur le prix des maisons individuelles neuves (EPTB
              2024) : 2&thinsp;300&thinsp;€/m² à Paris, 2&thinsp;100 en
              petite couronne, 2&thinsp;400 à Lyon et Villeurbanne,
              2&thinsp;250 dans la couronne lyonnaise. Une maison y coûte donc
              moins cher à reconstruire qu&apos;un appartement autour de
              Paris, mais plus cher autour de Lyon, où les maisons neuves de
              l&apos;enquête sont probablement plus souvent construites sur
              mesure : les chiffres lyonnais sont les plus fragiles. Les
              autres communes du panel gardent un coût unique, aux valeurs
              pilotes (de 1&thinsp;600&thinsp;€/m² à Figeac à
              1&thinsp;900&thinsp;€/m² à Grenoble et Annemasse). Les prix
              DVF étant exprimés au m² habitable, la valeur de marché et la
              valeur du bâti sont toutes deux calculées sur la surface
              habitable, estimée à 64&nbsp;% (appartements) et 61&nbsp;%
              (maisons) de la surface emprise × étages, ratios mesurés sur 35
              communes. Quand la BD TOPO ne donne pas le nombre
              d&apos;étages, il est déduit du type de bâtiment : un seul
              niveau, quelle que soit la hauteur, pour les hangars,
              entrepôts et grandes surfaces, les serres, les annexes, les
              constructions légères et les bâtiments agricoles, sportifs ou
              religieux ; la
              hauteur divisée par 3,5&nbsp;m pour les autres bâtiments
              commerciaux de plus de 7&nbsp;m ; la hauteur divisée par
              3&nbsp;m pour le logement. Le maillon le moins sûr est le rapport entre surface
              habitable et surface brute sous-jacent aux coûts : un écart de
              0,05 déplace la valeur bâti d&apos;environ 7&nbsp;%, qui se
              reporte sur le résiduel foncier. Le registre signale en WARN les
              communes dont la part foncière imputée sort de la fourchette
              40–65&nbsp;% (48 au-dessus et 1 en dessous sur 188, dont Paris
              et La Rochelle dans le panel). Cette fourchette est un repère à
              l&apos;échelle d&apos;une métropole, pas un test que chaque
              commune devrait passer : les communes limitrophes de Paris
              (76&nbsp;%) se situent naturellement entre 65 et 75&nbsp;%, comme
              les quartiers d&apos;affaires de premier rang. Les bureaux restent
              valorisés au prix de vente des logements, faute d&apos;une
              surface de prix propre aux locaux professionnels. La bande
              de sensibilité ±&thinsp;10 points encadre cette incertitude dans
              tous les résultats publiés : chiffres clés, catégories de bien
              et quintiles de revenu, où elle apparaît en traits fins autour
              de chaque barre.
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
