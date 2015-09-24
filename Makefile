# _*_ coding: utf-8 _*_
# Author		: bssthu
# Project		: mainWindow
# Creation date : 2015-09-24
#

UIC = pyuic5
RCC = pyrcc5
CLEANFILES = ui_*.py *_rc.py *~

all : ui_Form.py resource_rc.py

install : all
	python setup.py build

ui_Form.py : Form.ui
	$(UIC) -o ui_Form.py Form.ui

resource_rc.py : resource.qrc
	$(RCC) -o resource_rc.py resource.qrc


clean:
	rm -rf $(CLEANFILES)
