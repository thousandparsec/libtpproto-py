
release:
	rm -rf dist
	python setup.py sdist --formats=gztar,zip
	cp dist/* ../web/downloads/py-netlib
	cd ../web/downloads/py-netlib ; cvs add *.* ; cvs commit
