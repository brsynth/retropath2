#!/bin/bash

docker run \
  -v $PWD/..:/home:ro \
  -v $PWD/../workflows/9:/home/worflow:ro \
  -v $PWD:/test \
  -w /test \
  --rm brsynth/retropath2 \
/bin/sh run.sh

#cp results/test_out_scope.csv .


# docker run \
#   -v ${PWD}/run.sh:/home/run.sh \
#   -v ${PWD}/tool_RetroPath2.py:/home/tool_RetroPath2.py \
#   -v ${PWD}/test_input_sink.dat:/home/test_input_sink.dat \
#   -v ${PWD}/test_input_source.dat:/home/test_input_source.dat \
#   -v ${PWD}/results/:/home/results/ \
#   --rm brsynth/retropath2 \
# /bin/sh /home/run.sh