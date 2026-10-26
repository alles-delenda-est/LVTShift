"use client";

import { useEffect, useState } from "react";

/**
 * True below the `sm` breakpoint (640 px). Charts use it to shrink the
 * category-label column: a fixed 200 px label axis left phones with a plot
 * area too narrow for the bars and their value labels.
 */
export function useNarrow(maxWidth = 639): boolean {
  const [narrow, setNarrow] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${maxWidth}px)`);
    const update = () => setNarrow(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, [maxWidth]);
  return narrow;
}
