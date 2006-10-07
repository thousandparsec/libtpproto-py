#! /bin/sh

VERSION=`cat ./version.py | grep version | sed -e's/version = (//' -e's/, /./g' -e's/)//'`
DATE_LONG=`date +"%a, %d %b %Y %X %z"`
DATE_SHORT=`date +"%Y%m%d%H%M" -d"$DATE_LONG"`

cat > ./debian/changelog <<EOF
libtpproto-py ($VERSION-darcs+$DATE_SHORT) dapper; urgency=low

  * Release $VERSION from darcs on $DATE_LONG.

 -- Tim Ansell <tim@thousandparsec.net>  $DATE_LONG
EOF

./debian/rules binary-arch
