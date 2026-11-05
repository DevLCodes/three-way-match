from three_way_match.clean import clean


def test_removes_box_and_class_tags():
    raw = "<x_0.3574><y_0.0359>**INVOICE**<x_0.4678><y_0.0547><class_Title>"
    assert clean(raw) == "**INVOICE**"


def test_keeps_tables_and_hyphenated_classes():
    raw = (
        "<x_0.1><y_0.1>ACME Ltd<x_0.2><y_0.2><class_Page-header>\n\n"
        "<x_0.1><y_0.3>\\begin{tabular}{cc}\nA & \\$1.00\\\\\n\\end{tabular}<x_0.9><y_0.4><class_Table>"
    )
    assert clean(raw) == "ACME Ltd\n\n\\begin{tabular}{cc}\nA & \\$1.00\\\\\n\\end{tabular}"


def test_drops_picture_blocks():
    raw = "<x_0.1><y_0.1><x_0.2><y_0.2><class_Picture>\n\n<x_0.1><y_0.3>Total: 5<x_0.2><y_0.4><class_Text>"
    assert clean(raw) == "Total: 5"
