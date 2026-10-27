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

/** French number with a non-breaking thousands space: 6091 → "6 091". */
function num(n: number, decimals = 0): string {
  return n
    .toLocaleString("fr-FR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    .replace(/\s/g, " ");
}

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
  const farm = base.farmland;
  const tfpnb = data.taxes.find((t) => t.key === "tfpnb");
  const farmPays = (farm.value_meur * s1.rate_pct) / 100;
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
            Rapporté à la valeur du foncier imposable, il irait de{" "}
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

      <section aria-labelledby="tableau" className="mb-12">
        <H3 id="tableau">Le détail, impôt par impôt</H3>
        <p className="font-body text-sm text-gris max-w-3xl leading-relaxed mb-4">
          Montants en millions d&apos;euros. Pour les impôts qui suivent le
          marché immobilier (droits de mutation, plus-values), le montant retenu
          est la moyenne des {data.average_years} dernières années connues ; pour
          les autres, la dernière année. «&nbsp;Vérifié&nbsp;» : lu dans la source
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
          {num(base.total_meur / 1000)}&nbsp;Md€ fin {base.year}. Les terrains
          publics ({num(base.public_meur / 1000)}&nbsp;Md€) ne paient pas
          d&apos;impôt foncier et sont retirés. S&apos;y ajoutent{" "}
          {num(farm.value_meur / 1000)}&nbsp;Md€ de terres agricoles, ce qui
          donne {num(base.taxable_meur / 1000)}&nbsp;Md€ de foncier imposable.
          Le taux indicatif divise les recettes à remplacer par ce montant.
        </p>
        <h4 className="font-display text-lg font-medium text-marine leading-tight mt-6 mb-2">
          Comment les terres agricoles sont évaluées
        </h4>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Un impôt sur le sol se calcule sur ce que vaut le terrain. Pour les
          terres agricoles, la mesure la plus directe est le prix auquel elles
          se vendent. Les Safer, qui suivent les ventes de terres, publient
          chaque année le prix moyen d&apos;un hectare. Il suffit de le
          multiplier par la surface cultivée :
        </p>
        <ul className="font-body text-base text-encre leading-relaxed space-y-2 list-disc pl-5 mb-3">
          <li>
            <strong className="font-semibold">Terres et prés</strong> :{" "}
            {num(farm.area_ha / 1e6, 1)}&nbsp;millions d&apos;hectares. Un hectare
            libre de bail se vend en moyenne {num(farm.price_free_eur_ha)}&nbsp;€, un
            hectare loué {num(farm.price_let_eur_ha)}&nbsp;€, parce que le fermier
            en place garde le droit de l&apos;exploiter. Le calcul prend le milieu
            des deux prix.
          </li>
          <li>
            <strong className="font-semibold">Vignes</strong> :{" "}
            {num(Math.round(farm.vine_area_ha / 1000) * 1000)}&nbsp;hectares au prix
            moyen des vignes d&apos;appellation hors Champagne,{" "}
            {num(farm.vine_price_eur_ha)}&nbsp;€ l&apos;hectare. Ce prix sous-estime
            la Champagne et surestime les vignes sans appellation.
          </li>
        </ul>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Le résultat est de {num(farm.value_meur / 1000)}&nbsp;Md€ : entre{" "}
          {num(farm.low_meur / 1000)} et {num(farm.high_meur / 1000)}&nbsp;Md€ selon
          que l&apos;on retient le prix des terres louées ou celui des terres
          libres, soit {num((100 * farm.value_meur) / base.taxable_meur, 1)}&nbsp;% du
          foncier imposable. Au taux moyen du scénario&nbsp;1, ces terres
          paieraient environ {num(farmPays / 1000, 1)}&nbsp;Md€ par an ; la taxe
          foncière non bâtie, qui frappe aujourd&apos;hui les terres, les forêts et
          les autres terrains nus, rapporte{" "}
          {num((tfpnb?.reference_meur ?? 0) / 1000, 1)}&nbsp;Md€. Le taux réel
          serait fixé commune par commune.
        </p>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          <strong className="font-semibold">Pourquoi pas le chiffre de l&apos;INSEE ?</strong>{" "}
          Les comptes nationaux évaluent les terres cultivées à{" "}
          {num(farm.insee_meur / 1000)}&nbsp;Md€, plus de quatre fois le prix de
          vente : environ 31&nbsp;500&nbsp;€ l&apos;hectare, quand les ventes
          réelles se font autour de 6&nbsp;000&nbsp;€. L&apos;INSEE ne publie pas
          la méthode qui mène à ce chiffre. Un impôt assis sur une valeur que
          personne ne paie serait difficile à justifier auprès d&apos;un
          exploitant ; le prix de vente, lui, se vérifie.
        </p>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          <strong className="font-semibold">Les forêts ne sont pas comptées.</strong>{" "}
          Leur prix de vente inclut le bois sur pied, qui n&apos;est pas du sol.
          Même à ce prix, elles ajouteraient au plus{" "}
          {num(farm.forest_upper_meur / 1000)}&nbsp;Md€ et baisseraient le taux
          d&apos;environ{" "}
          {num((100 * farm.forest_upper_meur) / (base.taxable_meur + farm.forest_upper_meur), 1)}&nbsp;%.
        </p>
        <p className="font-body text-base text-encre leading-relaxed mb-3">
          Autres limites : la valeur des terrains bâtis de {base.year} est
          provisoire, et les prix moyens nationaux masquent de grands écarts
          entre régions.
        </p>
        <p className="font-body text-sm text-gris leading-relaxed mb-2">
          Terres agricoles :{" "}
          <a href={farm.url} className="text-marine underline underline-offset-2">
            {farm.source}
          </a>
          .
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

