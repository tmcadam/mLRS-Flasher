#!/usr/bin/env python
#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************
from gui.main import App

app_version = '30.11.2025-001'

#-------------------------------------------------
#-- Main (entry point) ---------------------------
#-------------------------------------------------

if __name__ == "__main__":
    app = App(app_version)
    app.update()
    app.after(10,app.after_startup())
    app.mainloop()
    app.closed()
