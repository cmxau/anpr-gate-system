from anpr_engine.normalizer import normalize_plate

def test_uppercase():
    assert normalize_plate("mh12ab1234") == "MH12AB1234"

def test_strip_spaces():
    assert normalize_plate("MH 12 AB 1234") == "MH12AB1234"

def test_strip_special_chars():
    assert normalize_plate("MH-12-AB-1234") == "MH12AB1234"

def test_ocr_artifacts():
    assert normalize_plate("MH|2AB!234") == "MH2AB234"

def test_empty_string():
    assert normalize_plate("") == ""
