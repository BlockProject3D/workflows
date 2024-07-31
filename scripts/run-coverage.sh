#!/usr/bin/env sh

./$1

find . -name "*.profraw" -exec mv {} ./ \;
rust-profdata merge -sparse *.profraw -o default.profdata
rm -f *.profraw
rust-cov export $1 -instr-profile=default.profdata --format=lcov > default.lcov
rm -f default.profdata

./lcov2cobertura/target/debug/lcov2xml -d default.lcov
mv coverage.xml "$1.coverage.xml"
rm -f default.lcov
