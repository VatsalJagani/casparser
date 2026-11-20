"""Soft-hyphen handling when joining wrapped CDSL ISIN cells."""

from casparser.parsers import pageobj
from casparser.parsers.pageobj import Atom, _join_column_atoms


def _atoms(*texts):
    return [
        Atom(x_left=0, x_right=10, y_top=100 - i * 10, y_bot=90 - i * 10, text=t, font="F")
        for i, t in enumerate(texts)
    ]


def test_u0002_at_wrap_is_rejoined():
    assert _join_column_atoms(_atoms("INF179K01\x02", "WN9")) == "INF179K01WN9"


def test_u0002_embedded_is_stripped():
    assert _join_column_atoms(_atoms("INF179K01\x02WN9")) == "INF179K01WN9"


def test_u00ad_unchanged():
    assert _join_column_atoms(_atoms("INF179K01­", "WN9")) == "INF179K01WN9"
    assert _join_column_atoms(_atoms("INF179K01­WN9")) == "INF179K01WN9"


def test_plain_text_unchanged():
    assert _join_column_atoms(_atoms("INF179K01WN9", "Fund A")) == "INF179K01WN9\nFund A"


def test_read_text_obj_maps_u0002(monkeypatch):
    raw = "INF179K01\x02".encode("utf-16-le") + b"\x00\x00"

    def fake_get_text(obj, tp, buf, size):
        buf[: len(raw)] = raw
        return len(raw)

    monkeypatch.setattr(pageobj.pdfium_raw, "FPDFTextObj_GetText", fake_get_text)
    monkeypatch.setattr(pageobj.pdfium_raw, "FPDFTextObj_GetFont", lambda o: None)
    monkeypatch.setattr(pageobj.pdfium_raw, "FPDFFont_GetBaseFontName", lambda f, b, n: 0)
    buf = (pageobj.ctypes.c_ubyte * pageobj._TEXT_BUF_SIZE)()
    fbuf = pageobj.ctypes.create_string_buffer(pageobj._FONT_BUF_SIZE)
    text, _ = pageobj._read_text_obj(None, None, buf, fbuf)
    assert text == "INF179K01" + pageobj.SOFT_HYPHEN
