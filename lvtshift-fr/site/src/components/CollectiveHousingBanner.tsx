import type { ReactNode } from "react";
import { signedPct, signedPctAxis } from "@/lib/format";
import type { ImpactSummary, QuintileGap } from "@/lib/impactSummary";
import VariantTerm from "@/components/VariantTerm";

/**
 * Home-page banner « L'immeuble collectif et les ménages modestes »: the prose
 * and two charts, all fed by lib/impactSummary so neither can drift from the
 * model. Plain HTML/CSS (no client JS): every value is also in the text, and
 * each chart carries a text alternative.
 */

const TRACK = "bg-lisere/70";

/** « Paris extra-muros (petite couronne) » → « Paris extra-muros ». */
function shortName(name: string): string {
  return name.replace(/\s*\(.*\)\s*$/, "");
}

function Swatch({ className }: { className: string }) {
  return <span aria-hidden="true" className={`inline-block w-3 h-3 mr-1.5 align-[-1px] ${className}`} />;
}

interface CountRowProps {
  label: string;
  central: number;
  alt: number | undefined;
  of: number;
}

/** One group: how many territories it pays less in, central case and local variant. */
function CountRow({ label, central, alt, of }: CountRowProps) {
  const bars: { key: string; value: number; fill: string; name: string }[] = [
    { key: "c", value: central, fill: "bg-marine", name: "cas central" },
  ];
  if (alt != null) bars.push({ key: "a", value: alt, fill: "bg-marine/45", name: "variante locale" });
  return (
    <li className="py-3 first:pt-0 last:pb-0">
      <p className="text-sm text-encre leading-snug mb-1.5">{label}</p>
      <div className="space-y-1">
        {bars.map((b) => (
          <div key={b.key} className="flex items-center gap-3">
            <div className={`relative h-3 flex-1 ${TRACK}`} aria-hidden="true">
              <div className={`absolute inset-y-0 left-0 ${b.fill}`} style={{ width: `${of > 0 ? (b.value / of) * 100 : 0}%` }} />
            </div>
            <p className="w-24 shrink-0 text-sm text-encre tabular-nums">
              <strong className="font-semibold">{b.value}</strong> sur {of}
              <span className="sr-only"> ({b.name})</span>
            </p>
          </div>
        ))}
      </div>
    </li>
  );
}

/** Axis bounds, rounded out to a multiple of 10 so ticks fall on whole numbers. */
function bounds(gaps: QuintileGap[]): { lo: number; hi: number } {
  const values = gaps.flatMap((g) => [g.poorest, g.richest, 0]);
  const lo = Math.floor(Math.min(...values) / 10) * 10;
  return { lo, hi: Math.max(Math.ceil(Math.max(...values) / 10) * 10, lo + 10) };
}

function GapChart({ gaps }: { gaps: QuintileGap[] }) {
  if (gaps.length === 0) return null;
  const { lo, hi } = bounds(gaps);
  const at = (v: number) => `${((v - lo) / (hi - lo)) * 100}%`;
  const step = Math.max(10, Math.ceil((hi - lo) / 5 / 10) * 10);
  const ticks: number[] = [];
  for (let t = Math.ceil(lo / step) * step; t <= hi; t += step) ticks.push(t);

  // Same left gutter for every row and for the axis, so the dots line up.
  const gutter = "w-[6.5rem] sm:w-40 shrink-0";

  return (
    <figure>
      <figcaption className="text-sm text-encre leading-snug mb-3">
        <strong>Variation de la taxe foncière, ménages les plus modestes et les plus aisés</strong>,
        par territoire (cas central). Plus un point est à gauche, plus le groupe paie moins.
      </figcaption>
      <p className="text-xs text-encre mb-3 flex flex-wrap gap-x-5 gap-y-1">
        <span>
          <span aria-hidden="true" className="inline-block w-4 h-4 mr-1.5 align-[-3px] rounded-full bg-marine" />
          20 % les plus modestes
        </span>
        <span>
          <span aria-hidden="true" className="inline-block w-2 h-2 mx-1 mr-2 align-[0px] rotate-45 bg-rouge" />
          20 % les plus aisés
        </span>
      </p>

      <div>
        <div className="flex items-end">
          <div className={gutter} />
          <div className="relative flex-1 h-5 mr-5">
            {ticks.map((t) => (
              <span
                key={t}
                className="absolute bottom-0 -translate-x-1/2 text-[0.65rem] text-gris tabular-nums whitespace-nowrap"
                style={{ left: at(t) }}
              >
                {signedPctAxis(t)}
              </span>
            ))}
          </div>
        </div>

        <ul aria-hidden="true">
          {gaps.map((g) => (
            <li key={g.commune_key} className="flex items-stretch min-h-7 border-t border-lisere/60">
              <p className={`${gutter} pr-2 py-0.5 self-center text-xs sm:text-sm text-encre leading-tight`}>{shortName(g.name)}</p>
              <div className="relative flex-1 mr-5">
                {ticks.map((t) => (
                  <span
                    key={t}
                    className={`absolute inset-y-0 w-px ${t === 0 ? "bg-encre/60" : "bg-lisere/70"}`}
                    style={{ left: at(t) }}
                  />
                ))}
                <span
                  className="absolute top-1/2 h-px bg-gris/60"
                  style={{
                    left: at(Math.min(g.poorest, g.richest)),
                    width: `${(Math.abs(g.richest - g.poorest) / (hi - lo)) * 100}%`,
                  }}
                />
                <span
                  className="absolute top-1/2 w-4 h-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-marine ring-2 ring-white"
                  style={{ left: at(g.poorest) }}
                />
                <span
                  className="absolute top-1/2 w-2 h-2 -translate-x-1/2 -translate-y-1/2 rotate-45 bg-rouge ring-1 ring-white z-10"
                  style={{ left: at(g.richest) }}
                />
              </div>
            </li>
          ))}
        </ul>

        <ul className="sr-only">
          {gaps.map((g) => (
            <li key={g.commune_key}>
              {g.name} : 20 % les plus modestes {signedPct(g.poorest)}, 20 % les plus aisés {signedPct(g.richest)}.
            </li>
          ))}
        </ul>
      </div>
    </figure>
  );
}

interface Props {
  impact: ImpactSummary;
  gaps: QuintileGap[];
  /** Link to the detailed results, shown under the charts. */
  footer?: ReactNode;
}

export function CollectiveHousingBanner({ impact, gaps, footer }: Props) {
  const { alt } = impact;
  return (
    <section aria-labelledby="immeuble-collectif" className="bg-creme border-b border-lisere">
      <div className="max-w-6xl mx-auto px-6 py-10 md:py-12">
        <h2
          id="immeuble-collectif"
          className="font-display text-[1.625rem] md:text-[2rem] font-medium text-marine leading-tight mb-6"
        >
          L&apos;immeuble collectif et les ménages modestes
        </h2>

        <div className="grid lg:grid-cols-12 gap-x-12 gap-y-8 items-start">
          <div className="lg:col-span-5 font-body text-base text-encre leading-relaxed space-y-4">
            <p>
              Sur les {impact.poorestAnalysable} territoires où le découpage par
              revenu est possible, le cinquième des ménages le plus modeste,
              pris dans son ensemble, s&apos;en sort <strong>mieux</strong> que
              le cinquième le plus aisé dans {impact.poorestBelowRichest}{" "}
              d&apos;entre eux
              {alt ? (
                <>
                  {" "}dans le{" "}
                  <VariantTerm kind="central">cas central</VariantTerm>,{" "}
                  {alt.poorestBelowRichest} dans la{" "}
                  <VariantTerm kind="local">variante locale</VariantTerm>. Il paie moins qu&apos;aujourd&apos;hui dans{" "}
                  {impact.poorestPayLess} d&apos;entre eux dans le cas central,{" "}
                  {alt.poorestPayLess} dans la variante locale.
                </>
              ) : (
                <>
                  , et paie moins qu&apos;aujourd&apos;hui dans{" "}
                  {impact.poorestPayLess} d&apos;entre eux.
                </>
              )}
            </p>
            <p>
              {alt ? (
                <>
                  Dans l&apos;immeuble collectif, où vivent la plupart des
                  ménages, le sol est partagé entre de nombreux logements : il
                  paie moins dans {impact.blocksPayLess} territoires sur{" "}
                  {impact.territories} dans le cas central, {alt.blocksPayLess}{" "}
                  dans la variante locale. Le petit immeuble de 2 à 4 logements,
                  souvent moins dense que ses voisins, paie moins dans{" "}
                  {impact.smallBuildingsPayLess} territoires seulement dans le
                  cas central.
                </>
              ) : (
                <>
                  Dans l&apos;immeuble collectif, où vivent la plupart des
                  ménages, le sol est partagé : il paie moins dans{" "}
                  {impact.blocksPayLess} territoires sur {impact.territories}. Le
                  petit immeuble de 2 à 4 logements, souvent moins dense que ses
                  voisins, paie moins dans {impact.smallBuildingsPayLess}{" "}
                  territoires seulement.
                </>
              )}
            </p>
            <p className="text-sm text-gris">
              Les logements sociaux ne sont pas comptés parmi les ménages : leur
              taxe foncière n&apos;étant pas récupérable sur les locataires, sa
              variation pèse sur les bailleurs.
            </p>
            {footer}
          </div>

          <div className="lg:col-span-7 grid gap-8">
            <div className="bg-white border border-lisere p-5">
              <h3 className="text-xs uppercase tracking-[0.15em] text-gris mb-3">
                Dans combien de territoires paient-ils moins ?
              </h3>
              <p className="text-xs text-encre mb-4 flex flex-wrap gap-x-5 gap-y-1">
                <span><Swatch className="bg-marine" />Cas central</span>
                {alt && <span><Swatch className="bg-marine/45" />Variante locale</span>}
              </p>
              <ul className="divide-y divide-lisere/70">
                <CountRow
                  label="Les 20 % de ménages les plus modestes"
                  central={impact.poorestPayLess}
                  alt={alt?.poorestPayLess}
                  of={impact.poorestAnalysable}
                />
                <CountRow
                  label="Immeuble collectif (5 logements ou plus)"
                  central={impact.blocksPayLess}
                  alt={alt?.blocksPayLess}
                  of={impact.territories}
                />
                <CountRow
                  label="Petit immeuble (2 à 4 logements)"
                  central={impact.smallBuildingsPayLess}
                  alt={alt?.smallBuildingsPayLess}
                  of={impact.territories}
                />
              </ul>
              <p className="text-xs text-gris mt-4">
                Les 20 % de ménages les plus modestes : {impact.poorestAnalysable}{" "}
                territoires où le découpage par revenu est possible. Les deux
                autres lignes : les {impact.territories} territoires.
              </p>
            </div>

            <div className="bg-white border border-lisere p-5">
              <GapChart gaps={gaps} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
