#!/bin/bash
CASE_DIR="cases/lane_changing"
VERIFIER="system_verification/two_input/verifier"
CONTROLLER_GENERATOR="$CASE_DIR/generate_controller_automation.py"
CONFIG_FILE="$CASE_DIR/config.yaml"
K="8"
FSM_FILE="controller.in"
BOUNDARY_FILE="boundary.csv"
CM_FILE="cost_matrix.csv"
python3 $CONTROLLER_GENERATOR $CONFIG_FILE $FSM_FILE
$VERIFIER weaklyhardsingle $FSM_FILE $K $CM_FILE $BOUNDARY_FILE
$VERIFIER weaklyhardreuse $FSM_FILE $K
python experiment_fusion.py $K $BOUNDARY_FILE $CM_FILE
rm $BOUNDARY_FILE $CM_FILE $FSM_FILE
