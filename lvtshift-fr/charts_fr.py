"""French-localised charts: reuse upstream's plotting, render euros not dollars.

Upstream ``lvt.viz`` hardcodes the US dollar sign in its chart labels and
annotations (literal ``$`` in f-strings — there is no currency parameter). In
keeping with this fork's zero-upstream-modification rule, we do **not** edit or
re-implement those charts. Instead we run upstream's public ``create_city_report``
unchanged and intercept matplotlib at the moment each figure is saved, rewriting
the currency in the figure's text (``$1,234`` -> ``1 234 €``) first.

Why intercept at ``savefig`` rather than call upstream's private ``_make_*``
helpers: it depends only on the *public* ``create_city_report`` API plus
matplotlib's stable ``Figure.savefig``, so an upstream refactor of the chart
internals won't break us. If anything in the euro-isation fails, we fall back to
saving the chart exactly as upstream produced it (dollars) rather than lose the
chart.

Scope: this localises the *currency* only. Chart titles/axis words remain in
English (upstream); full French titling is a separate i18n step.
"""

import re

import pandas as pd

# Matches a US money token like "$1,234", "$1,234.56" or "-$987". Commas are
# only consumed as thousands separators (between digit groups), so trailing
# punctuation such as the comma in "$156, +0.3%" is left untouched.
_MONEY = re.compile(r"(-?)\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)")


def _money_to_eur(match: re.Match) -> str:
    """`-$2,691,246` -> `-2 691 246 €` (French: space thousands, trailing €)."""
    sign, number = match.group(1), match.group(2)
    number = number.replace(",", " ")  # non-breaking space as thousands sep
    return f"{sign}{number} €"


def _to_eur_text(text: str) -> str:
    """Euro-ise one label: reformat money tokens, then any stray `$` (e.g. "($)")."""
    text = _MONEY.sub(_money_to_eur, text)
    return text.replace("$", "€")


def _eurize_figure(fig) -> None:
    """Rewrite every text artist in a figure from dollars to euros, in place."""
    import matplotlib.text

    for artist in fig.findobj(matplotlib.text.Text):
        s = artist.get_text()
        if "$" in s:
            artist.set_text(_to_eur_text(s))


def create_city_report_fr(df: pd.DataFrame, **kwargs) -> dict:
    """Like ``lvt.viz.create_city_report`` but with euro-denominated charts.

    Accepts and forwards the same keyword arguments (``city``, ``output_dir``,
    ``show``, ``census_categories`` ...). Temporarily wraps
    ``matplotlib.figure.Figure.savefig`` so every chart upstream saves is
    euro-ised first, then restores it — so the patch never leaks beyond this call.
    """
    import matplotlib.figure

    from lvt.viz import create_city_report

    original_savefig = matplotlib.figure.Figure.savefig

    def savefig_eur(self, *args, **saveargs):
        try:
            _eurize_figure(self)
        except Exception:  # never lose a chart over a formatting hiccup
            pass
        return original_savefig(self, *args, **saveargs)

    matplotlib.figure.Figure.savefig = savefig_eur
    try:
        return create_city_report(df, **kwargs)
    finally:
        matplotlib.figure.Figure.savefig = original_savefig
