def center_widget(app, widget):
    frameGm = widget.frameGeometry()
    frameGm.moveCenter(app.desktop().screenGeometry(app.desktop().screenNumber(app.desktop().cursor().pos())).center())
    widget.move(frameGm.topLeft())
