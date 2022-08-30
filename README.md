# Verification and Monitoring with Multiple Weakly-Hard Constraints
We used a weakly-hard fault model to constrain the occurrences of faults in system inputs. We developed approaches to verify properties for multiple weakly-hard constraints in an exact and efficient manner. By verifying multiple weakly-hard constraints and storing the verification results as a safety table or the corresponding satisfaction boundary, we defined weakly- hard requirements for the system environment and designed a runtime monitor that guarantees desired properties or notifies the system to switch to a safe mode.

This repository contains the implementations of verifications and use cases from the paper:
#### System Verification and Runtime Monitoring with Multiple Weakly-Hard Constraints
[Springer](https://link.springer.com/chapter/10.1007/978-3-030-60508-7_28)

## Requirements
- numpy
- PyYAML

## Installation
1. Check out the repository
```bash
$ git clone https://github.com/verification-and-monitoring-with-multiple-weakly-hard-constraints
```
2. Install the requirements
```bash=
$ cd verification-and-monitoring-with-multiple-weakly-hard-constraints
$ pip install -r requirements.txt
```

## Input Format
To use our system verification, a finite state machine file representing the system is required. The formats are as follow:
- For `one_input`:

    ```
    [totol number of states]
    [state after input 0] [state after input 1] [1 if this state is unsafe else 0]
    ...
    ...
    ```
    The first line is the total number of the states of this FSM. Each following lines represents a state (starts from state 0). The first(second) number shows the state index of the transition result after input 0(1). And the last number tells that the state is unsafe or not.

    For exmple, in a FSM, there are 5 states in total. State 0 will transition to state 1(2) after having 0(1) and it is a safe state. Then the first two lines of the FSM file will be as follows:

    ```
    5
    1 2 0
    ...
    ...
    ```
- For `two_input`:

    ```
    [totol number of states]
    [state after input 00] [01] [10] [11] [1 if this state is unsafe else 0]
    ...
    ...
    ```
    The format is similar to `one_input`, but there are four kinds of inputs (`00`, `01`, `10`, `11`) instead of two.

## Execution
The following steps will reproduce the experimental results for lane changing. Other use cases could be reproduced similarly.

1. Compile the verifier by typing the command
```bash
$ cd verification-and-monitoring-with-multiple-weakly-hard-constraints/system_verification/two_input/; make
$ cd verification-and-monitoring-with-multiple-weakly-hard-constraints/system_verification/one_input/; make
```
2. Set configuration of the experiment by modifying `cases/lane_changing/config.yaml`.
4. In `run.sh`, make sure that the following values are set to the desired ones:
    - `CASE_DIR=cases/lane_changing`
    - `VERIFIER=system_verification/two_input/verifier`
    - `K=8`
6. Run experiment by executing the bash script
```bash
$ cd verification-and-monitoring-with-multiple-weakly-hard-constraints
$ sh run.sh
```

## Note
* Lane changing and vehicle following should use ```two_input```, and the rest should use ```one_input```.