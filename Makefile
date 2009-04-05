
release:
	rm -rf dist
	python setup.py sdist --formats=bztar
	python setup.py bdist --formats=rpm,egg
	cp dist/* ../web/downloads/libtpproto-py

clean:
	rm -rf dist
	rm -rf build
	rm -rf libtpproto_py.egg-info
