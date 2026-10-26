/**
 * Symmetric axis around zero on a round step, for the diverging charts.
 *
 * The previous axes used `max × headroom` as the limit, which put ticks on
 * values such as ±85,3 % or ±17,5 %. This picks the smallest "nice" step
 * (1, 2, 2,5, 5 × 10ⁿ) that covers `absMax × headroom` in at most
 * `maxTicksPerSide` steps, so every tick is a round number.
 */
export interface SymmetricAxis {
  lim: number;
  step: number;
  ticks: number[];
}

const NICE = [1, 2, 2.5, 5];

export function symmetricAxis(
  absMax: number,
  { headroom = 1.1, maxTicksPerSide = 4, minLim = 5 } = {},
): SymmetricAxis {
  const target = Math.max(Math.abs(absMax) * headroom, minLim);
  let step = 1;
  outer: for (let exp = -1; exp <= 6; exp++) {
    for (const n of NICE) {
      const s = n * 10 ** exp;
      if (Math.ceil(target / s) <= maxTicksPerSide) {
        step = s;
        break outer;
      }
    }
  }
  const k = Math.ceil(target / step);
  const lim = k * step;
  const ticks: number[] = [];
  for (let i = -k; i <= k; i++) ticks.push(Number((i * step).toFixed(6)));
  return { lim, step, ticks };
}
