# _*_ coding: utf-8 _*_
# Author		: bssthu
# Project		: L5MapEditor
# Creation date : 2015-09-24
#

UIC = pyuic5
RCC = pyrcc5
CLEANFILES = ui_*.py *_rc.py *~

.PHONY: all
all : editor/ui_Form.py editor/resource_rc.py

.PHONY: install
install : all
	python setup.py build

editor/ui_Form.py : ui/Form.ui
	$(UIC) --from-imports -o editor/ui_Form.py ui/Form.ui

editor/resource_rc.py : ui/resource.qrc
	$(RCC) -o editor/resource_rc.py ui/resource.qrc

.PHONY: clean
clean:
	cd editor; rm -rf $(CLEANFILES)

.PHONY: test
test:
	coverage run --source=$(PWD) setup_test.py test
	coverage report -m
