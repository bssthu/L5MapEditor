# _*_ coding: utf-8 _*_
# Author		: bssthu
# Project		: L5MapEditor
# Creation date : 2015-09-24
#

UIC = pyuic5
RCC = pyrcc5
CLEANFILES = ui_*.py *_rc.py *~

.PHONY: all
all : ui_Form.py resource_rc.py

.PHONY: install
install : all
	python setup.py build

ui_Form.py : Form.ui
	$(UIC) -o ui_Form.py Form.ui

resource_rc.py : resource.qrc
	$(RCC) -o resource_rc.py resource.qrc

.PHONY: clean
clean:
	rm -rf $(CLEANFILES)

.PHONY: test
test:
	coverage run --source=$(PWD) setup_test.py test
	coverage report -m
