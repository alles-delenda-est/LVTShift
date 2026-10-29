import { loadYields } from "@/lib/data";
import YieldsChart from "@/components/charts/YieldsChart";
import {
  FAMILY_COLORS,
  familyOf,
  SCENARIO_LABELS,
  STATUS_LABELS,
  TIER_LABELS,
  mdEur,
  variant,
  yearsLabel,
  type ScenarioKey,
  type YieldTax,
} from "@/lib/yields";

export const metadata = {
  title: "Scénarios de remplacement — Pour une terre productive",
  description:
    "Ce qu'un impôt sur la valeur du sol devrait rapporter pour remplacer, à recettes égales, la taxe foncière, les droits de mutation et les impôts sur les revenus et plus-values immobiliers.",
};

const SCENARIO_OF: Record<YieldTax["scenario"], string> = {
  S1: "Scénario 1",
  S2: "Scénario 2",
  S2_IFI: "Option IFI (scénarios 2 et 3)",
  S3: "Scénario 3",
};

const STATUS_STYLE: Record<YieldTax["status"], string> = {
  verified: "border-marine text-marine",
  derived: "border-gris text-gris",
  reported: "border-rouge text-rouge",
};

function H3({ id, children }: { id: string; children: React.ReactNode }) {
  return (
    <h3 id={id} className="font-display text-xl md:text-2xl font-medium text-marine leading-tight mb-3">
      {children}
    </h3>
  );
}

export default function ScenariosPage() {
  const data = loadYields();
  const s1 = variant(data, "S1", false);
  const s3ifi = variant(data, "S3", true);
  const local = s1.tiers_meur.local;
  const base = data.land_base;
  const companyRows = (
    [
      ["S2", false, "Scénario 2"],
      ["S2", true, "Scénario 2 + IFI"],
      ["S3", false, "Scénario 3"],
      ["S3", true, "Scénario 3 + IFI"],
    ] as const
  ).map(([sc, ifi, label]) => {
    const v = variant(data, sc, ifi);
    return { label, added: v.total_meur - s1.total_meur, companies: v.company_land_meur };
  });
  const groups = (["S1", "S2", "S2_IFI", "S3"] as const).map((sc) => ({
    sc,
    taxes: data.taxes.filter((t) => t.scenario === sc),
  }));

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="mb-8 border-b border-lisere pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-gris mb-2">Scénarios de remplacement</p>
        <h2 className="font-display text-2xl md:text-[1.75rem] font-medium text-marine leading-tight mb-3">
          Quels impôts l&apos;impôt sur la valeur du sol remplacerait-il ?
        </h2>
        <p className="font-body text-base text-gris max-w-3xl leading-relaxed">
          La réforme est à recettes égales : chaque euro levé sur la valeur du
          sol remplace un euro d&apos;un impôt existant. Trois scénarios, emboîtés,
          vont du plus simple au plus large. Le graphique montre ce que chacun
          devrait rapporter chaque année.
        </p>
      </div>

      <section aria-labelledby="graphique" className="mb-12">
        <h3 id="graphique" className="text-xs uppercase tracking-[0.18em] text-gris mb-3">
          Recettes à remplacer, par scénario
        </h3>
        <YieldsChart data={data} />
        <div className="mt-5 grid gap-4 md:grid-cols-3 max-w-5xl">
          <p className="font-body text-sm text-encre leading-relaxed">
            <strong className="font-semibold">La taxe foncière fait l&apos;essentiel.</strong>{" "}
            Avec les frais de gestion de l&apos;État, elle pèse {mdEur(data.taxes.filter((t) => familyOf(t.key) === "tf").reduce((s, t) => s + t.reference_meur, 0))}&nbsp;Md€
            ; les scénarios 2 et 3 n&apos;ajoutent au plus que {mdEur(s3ifi.total_meur - s1.total_meur)}&nbsp;Md€.
          </p>
          <p className="font-body text-sm text-encre leading-relaxed">
            <strong className="font-semibold">La part communale ne change pas.</strong>{" "}
            Dans les cinq variantes, {mdEur(local)}&nbsp;Md€ sont levés au niveau
            de la commune (taxe foncière, taxe d&apos;habitation des résidences
            secondaires et droits de mutation communaux) ; ce
            qui s&apos;ajoute relève des départements et de l&apos;État.
          </p>
          <p className="font-body text-sm text-encre leading-relaxed">
            <strong className="font-semibold">Le taux est une moyenne.</strong>{" "}
            Rapporté à la valeur des terrains bâtis, il irait de{" "}
            {s1.rate_pct.toLocaleString("fr-FR")}&nbsp;% à{" "}
            {s3ifi.rate_pct.toLocaleString("fr-FR")}&nbsp;% par an. Le taux local
            réel serait fixé commune par commune.
          </p>
        </div>
      </section>

      <section aria-labelledby="scenarios-def" className="mb-12 max-w-3xl">
        <H3 id="scenarios-def">Les trois scénarios</H3>
        <ol className="font-body text-base text-encre leading-relaxed space-y-3 list-none">
          {(["S1", "S2", "S3"] as ScenarioKey[]).map((sc) => (
            <li key={sc}>
              <strong className="font-semibold">{SCENARIO_LABELS[sc].short} — {SCENARIO_LABELS[sc].long.replace(/^\+ /, "")}.</strong>{" "}
              {sc === "S1" &&
                "Les impôts qui frappent directement la propriété et son achat. La taxe d'habitation sur les résidences secondaires y figure parce qu'elle est, comme la taxe foncière, un impôt local sur un logement, payé le plus souvent par son propriétaire. Les droits de mutation pénalisent chaque déménagement ; un impôt sur le sol ne dépend pas de la fréquence des ventes."}
              {sc === "S2" &&
                "S'y ajoutent l'impôt sur le revenu et les prélèvements sociaux sur les plus-values immobilières des particuliers : une part de ces gains vient de la hausse du prix du terrain, que l'impôt sur le sol capterait chaque année plutôt qu'à la vente. L'IFI peut y être ajouté : c'est un choix politique plus qu'un calcul, car il frappe aussi les bâtiments."}
              {sc === "S3" &&
                "S'y ajoutent l'impôt sur le revenu et les prélèvements sociaux sur les loyers perçus par les particuliers. Ce scénario va le plus loin : il remplace une partie de l'imposition du revenu du capital immobilier par celle de sa composante foncière."}
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="societes" className="mb-12 max-w-3xl">
        <H3 id="societes">Scénarios 2 et 3 : une part de la charge passe aux sociétés</H3>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Les impôts que les scénarios 2 et 3 suppriment ne sont payés que par
          les particuliers : impôt sur le revenu et prélèvements sociaux sur
          leurs plus-values et leurs loyers, et IFI. Les sociétés continuent de
          payer l&apos;impôt sur les sociétés sur leurs propres loyers et
          plus-values. Or l&apos;impôt sur le sol frappe tous les terrains, et
          ceux des sociétés, entreprises publiques comprises, représentent{" "}
          {Math.round(base.companies_meur / 1000).toLocaleString("fr-FR").replace(/\s/g, "\u00a0")}&nbsp;Md€,
          soit {base.companies_share_pct.toLocaleString("fr-FR")}&nbsp;% de la
          base taxable.
        </p>
        <div className="overflow-x-auto -mx-6 px-6 mb-3">
          <table className="w-full min-w-[30rem] font-body text-sm border-collapse">
            <thead>
              <tr className="border-b-2 border-marine text-left text-xs uppercase tracking-wider text-gris">
                <th scope="col" className="py-2 pr-4 font-normal">Variante</th>
                <th scope="col" className="py-2 pr-4 font-normal text-right">Ajouté au scénario 1</th>
                <th scope="col" className="py-2 font-normal text-right">Porté par le foncier des sociétés</th>
              </tr>
            </thead>
            <tbody>
              {companyRows.map((r) => (
                <tr key={r.label} className="border-b border-lisere">
                  <th scope="row" className="py-2 pr-4 text-left font-normal text-encre">{r.label}</th>
                  <td className="py-2 pr-4 text-right tabular-nums">{mdEur(r.added)}&nbsp;Md€</td>
                  <td className="py-2 text-right tabular-nums font-semibold">{mdEur(r.companies)}&nbsp;Md€</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          C&apos;est un transfert des bailleurs et vendeurs particuliers vers
          les sociétés qui possèdent du foncier. Il disparaîtrait si
          l&apos;impôt sur les sociétés payé sur les loyers et plus-values
          immobiliers était remplacé lui aussi ; aucun chiffre public ne
          l&apos;isole, il n&apos;est donc pas modélisé.
        </p>
        <p className="font-body text-sm text-gris leading-relaxed">
          Calcul : part des sociétés dans la base taxable × montant que la
          variante ajoute au scénario 1, en supposant un taux national
          uniforme. Le scénario 1 ne crée pas ce transfert : les sociétés
          paient déjà la taxe foncière et les droits de mutation qu&apos;il
          remplace. Source : INSEE, patrimoine des secteurs institutionnels,
          fin {base.year}.
        </p>
      </section>

      <section aria-labelledby="tableau" className="mb-12">
        <H3 id="tableau">Le détail, impôt par impôt</H3>
        <p className="font-body text-sm text-gris max-w-3xl leading-relaxed mb-4">
          Montants en millions d&apos;euros de {data.price_basis.year}. Pour les
          impôts qui suivent le marché immobilier (droits de mutation,
          plus-values), le montant retenu est la moyenne des{" "}
          {data.average_years} dernières années connues ; pour les autres, la
          dernière année. Chaque année est convertie en euros de{" "}
          {data.price_basis.year} avec l&apos;indice des prix de l&apos;INSEE,
          pour que tous les montants du site partagent la même base de prix. «&nbsp;Vérifié&nbsp;» : lu dans la source
          primaire ; «&nbsp;Calculé&nbsp;» : déduit de chiffres primaires ;
          «&nbsp;À confirmer&nbsp;» : repris d&apos;une source secondaire.
        </p>
        <div className="overflow-x-auto -mx-6 px-6">
          <table className="w-full min-w-[44rem] font-body text-sm border-collapse">
            <thead>
              <tr className="border-b-2 border-marine text-left text-xs uppercase tracking-wider text-gris">
                <th scope="col" className="py-2 pr-4 font-normal">Impôt</th>
                <th scope="col" className="py-2 pr-4 font-normal">Niveau</th>
                <th scope="col" className="py-2 pr-4 font-normal">Finance</th>
                <th scope="col" className="py-2 pr-4 font-normal text-right">Montant</th>
                <th scope="col" className="py-2 pr-4 font-normal">Années</th>
                <th scope="col" className="py-2 font-normal">Statut</th>
              </tr>
            </thead>
            {groups.map(({ sc, taxes }) => (
              <tbody key={sc}>
                <tr>
                  <th colSpan={6} scope="colgroup" className="pt-5 pb-1 text-left font-display text-base font-medium text-marine">
                    {SCENARIO_OF[sc]}
                  </th>
                </tr>
                {taxes.map((t) => (
                  <tr key={t.key} className="border-b border-lisere align-top">
                    <td className="py-2 pr-4">
                      <span className="flex items-start gap-2">
                        <span
                          aria-hidden="true"
                          className="mt-1.5 inline-block w-2 h-2 rounded-sm shrink-0"
                          style={{ background: FAMILY_COLORS[familyOf(t.key) ?? "tf"] }}
                        />
                        <span>
                          <span className="text-encre">{t.label_fr}</span>
                          <span className="block text-xs text-gris mt-0.5 leading-snug">{t.scope}</span>
                          {t.note && <span className="block text-xs text-gris italic mt-0.5 leading-snug">{t.note}</span>}
                          <a href={t.url} className="block text-xs text-marine underline underline-offset-2 mt-0.5 leading-snug">
                            {t.source}
                          </a>
                        </span>
                      </span>
                    </td>
                    <td className="py-2 pr-4 whitespace-nowrap">{TIER_LABELS[t.tier]}</td>
                    <td className="py-2 pr-4">{t.budget}</td>
                    <td className="py-2 pr-4 text-right tabular-nums whitespace-nowrap">
                      {t.reference_meur.toLocaleString("fr-FR").replace(/\s/g, " ")}
                    </td>
                    <td className="py-2 pr-4 whitespace-nowrap">
                      {t.basis === "average" ? "moy. " : ""}
                      {yearsLabel(t.reference_years)}
                    </td>
                    <td className="py-2">
                      <span className={`inline-block border px-1.5 py-0.5 text-xs whitespace-nowrap ${STATUS_STYLE[t.status]}`}>
                        {STATUS_LABELS[t.status]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            ))}
          </table>
        </div>
      </section>

      <section aria-labelledby="hors-champ" className="mb-12 max-w-3xl">
        <H3 id="hors-champ">Ce qui n&apos;est pas compté</H3>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Certains prélèvements touchent aussi la propriété mais restent hors
          des trois scénarios. Les inclure est possible ; chacun est un choix.
        </p>
        <ul className="font-body text-base text-encre leading-relaxed space-y-2 list-disc pl-5">
          <li>
            <strong className="font-semibold">La taxe d&apos;enlèvement des ordures ménagères</strong>{" "}
            (9,2&nbsp;Md€ en 2025), portée sur le même avis que la taxe
            foncière mais qui finance un service.
          </li>
          <li>
            <strong className="font-semibold">La cotisation foncière des entreprises</strong>{" "}
            (8,2&nbsp;Md€), qui frappe l&apos;occupation de locaux par une activité,
            pas la propriété.
          </li>
          <li>
            <strong className="font-semibold">Les compensations versées par l&apos;État</strong>{" "}
            pour les locaux exonérés, surtout industriels (environ 2,7&nbsp;Md€ en
            2025, réduites depuis 2026) : ce n&apos;est pas un impôt, mais les
            communes les perdraient si l&apos;exonération disparaissait.
          </li>
          <li>
            <strong className="font-semibold">La contribution de sécurité immobilière</strong>{" "}
            (0,7&nbsp;Md€ en 2025), payée à l&apos;État à chaque vente, et{" "}
            <strong className="font-semibold">la taxe sur les bureaux en Île-de-France</strong>{" "}
            (environ 1&nbsp;Md€), qui frappe les surfaces de bureaux, de commerces et de stockage.
          </li>
          <li>
            <strong className="font-semibold">L&apos;impôt sur les sociétés</strong>{" "}
            payé sur les loyers et plus-values des sociétés : aucun chiffre public
            ne l&apos;isole. Les <strong className="font-semibold">locations meublées</strong>{" "}
            ne sont pas non plus distinguées dans les sources.
          </li>
        </ul>
        <p className="font-body text-sm text-gris leading-relaxed mt-3">
          Montants : DGFiP, REI 2025, via OFGL.
        </p>
      </section>

      <section aria-labelledby="taux" className="mb-4 max-w-3xl">
        <H3 id="taux">D&apos;où vient le taux indicatif</H3>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          L&apos;INSEE estime provisoirement la valeur des terrains bâtis à{" "}
          {Math.round(base.total_meur / 1000).toLocaleString("fr-FR").replace(/\s/g, " ")}&nbsp;Md€
          fin {base.year}. Les terrains publics (
          {Math.round(base.public_meur / 1000).toLocaleString("fr-FR")}&nbsp;Md€)
          ne paient pas d&apos;impôt foncier et sont retirés, ce qui laisse{" "}
          {Math.round(base.taxable_meur / 1000).toLocaleString("fr-FR").replace(/\s/g, " ")}&nbsp;Md€.
          Le taux indicatif divise les recettes à remplacer, en euros de{" "}
          {data.price_basis.year}, par ce montant.
        </p>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Deux limites : le chiffre de {base.year} est provisoire, et les terres
          agricoles et naturelles n&apos;y figurent pas. Les inclure ferait
          baisser le taux.
        </p>
        <p className="font-body text-sm text-gris leading-relaxed">
          Source :{" "}
          <a href={base.url} className="text-marine underline underline-offset-2">
            {base.source}
          </a>
          . Le calcul est statique : les effets attendus de la réforme sur les
          prix, les ventes et les loyers ne sont pas intégrés à ces montants.
        </p>
      </section>
    </div>
  );
}

