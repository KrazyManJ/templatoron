import os

# One file:
os.system('pyinstaller --name Templatoron --windowed --onefile --noconsole --distpath . --icon=icon.ico --add-data="icon.ico;." --add-data="app/design/*.ui;app/design" --add-data="app/src/*.json;app/src" --add-data="app/fonts/*.ttf;app/fonts" main.py')
#os.system('pyinstaller --name Templatoron --windowed --noconsole --icon=icon.ico --add-data="icon.ico;." --add-data="app/design/*.ui;app/design" --add-data="app/src/*.json;app/src" --add-data="app/fonts/*.ttf;app/fonts" main.py')