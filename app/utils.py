import base64


def center_widget(app, widget):
    frameGm = widget.frameGeometry()
    frameGm.moveCenter(app.desktop().screenGeometry(app.desktop().screenNumber(app.desktop().cursor().pos())).center())
    widget.move(frameGm.topLeft())


def image_to_base_bytes(path: str):
    with open(path, "rb") as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode()
