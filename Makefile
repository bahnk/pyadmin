
# PYTHON PACKAGES
# black
# click
# pylint
# pytest
# sphinx
# sphinx-rtd-theme

PACKAGE=pyadmin

.PHONY: .FORCE

all: .FORCE zip

install:
	python -m pip install --no-cache-dir .

zip: readme test clean
	cd ../ && zip -r $(PACKAGE).zip $(PACKAGE)

readme:
	pandoc --toc -o README.pdf README.md

clean:
	find $(PACKAGE) -name "__pycache__" -type d -exec rm -rfv {} \; || true
	rm -rfv dist/
	rm -rfv $(PACKAGE).egg-info/
	rm -rfv docs/build/
	rm -f docs/make.bat
	rm -rfv .pytest_cache
	rm -rfv build

build:
	python3 -m build

doc:
	cd docs && make html

test: pylint
	pytest --verbose

pylint: black
	pylint setup.py
	pylint --recursive y $(PACKAGE)

black:
	black setup.py
	find ./ -name ".py" -exec black {} \;

