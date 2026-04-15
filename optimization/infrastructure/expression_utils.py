from __future__ import annotations


_CHAR_NORMALIZATION = str.maketrans(
    {
        "\u2212": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2012": "-",
        "\u2011": "-",
    }
)


def normalize_expression_text(expr: str) -> str:
    return expr.translate(_CHAR_NORMALIZATION)
