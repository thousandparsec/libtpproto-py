#! /bin/sh

grep 'no =' * | sed -e"s/\(.*\):.*no = \(.*\)/\2 \1/" | sort -n | uniq

