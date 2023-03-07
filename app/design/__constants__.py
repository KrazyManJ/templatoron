

class StyleConstants:

    VAR_INPUT = """
    QFrame {
        background: #141414;
        max-height: 40px;
        min-height: 40px;
        border-radius: 10px;
        border: 1px solid #555;
    }
    QLineEdit {
        background: transparent;
        border: none;
        font: 10pt "Fira Code";
        color: #ccc;
    }
    """
    QMENU = """
    QMenu {
        background-color: #292929;
        font: 12pt "Inter";
        color: white;
        border: 1px solid #444;
        border-radius: 15px;
        padding: 10px;
    }
    QMenu::item {
        padding: 2px 25px 2px 20px;
        border: 1px solid transparent;
        border-radius: 5px;
    }
    QMenu::item:selected {
        background: #333;
        border: 1px solid #666;
    }
    QMenu::item:pressed {
        background: #444;
        border: 1px solid #666;
    }
    """

    TITLEBAR_NORMALIZE_BTN = "border-image: url(:/titlebar/titlebar/normalize.svg);"
