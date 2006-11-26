
release: clean
	python setup.py sdist --formats=gztar,zip
	python setup.py bdist --formats=rpm,wininst
	cp dist/* ../web/downloads/py-netlib
	cd ../web/downloads/py-netlib ; darcs add *.* ; darcs record

clean:
	rm -rf dist
	rm -rf build
	rm -rf libtpproto_py.egg-info/
