#!/bin/sh
ssh -N -f -L $1:localhost:$1 tencloud@mturk-tracker.com
