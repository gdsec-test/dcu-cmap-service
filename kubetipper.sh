#!/bin/sh

[ -z "$LIVENESS_TTL" ] && exit 0;
FACTOR=${LIVENESS_FACTOR:=1}

T0=`ls -l --time-style=+%s /proc/1/cmdline | cut -d " " -f6`
T1=`date +%s`
AGE=$(($T1 - $T0))
RAND=`echo "scale=2; $(( 1 + RANDOM % 100)) / 100" | bc`

echo "Age: $AGE, TTL: $LIVENESS_TTL, Factor: $FACTOR, Rand: $RAND"

[ "$AGE" -ge "$LIVENESS_TTL" ] && [ `echo "$RAND <= $FACTOR" | bc -l` -eq "1" ] && exit 1;

exit 0
