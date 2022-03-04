#!/bin/sh

grep TODO -rni  model/* | sed   -e '$!s/$/\\/' > TODOS.md
