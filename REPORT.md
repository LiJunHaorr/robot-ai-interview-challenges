# Report

## Completed

- Implemented the required `Event`, `Effect`, `RobotApplication` interfaces.
- Implemented welcome deduplication, interaction suppression, 10-second tick-based farewell, short-return handling, completed-departure reset, validation, and detached snapshots.
- Added automated tests for all required scenarios plus invalid input and timestamp ordering.

## Verification

Command: `python -m pytest -q`

Result: `11 passed in 0.06s` locally.

## ROS 2 diagnosis

1. Facts: the application created a `wave_hand` effect; the bridge submitted task `task-17` and reported `accepted_async`; `/basic_action_play_v2` has one client and zero servers; robot mode is `STAND`; `robot-action.service` is inactive.
2. `accepted_async` proves only that the bridge accepted/submitted the request. It does not prove execution or completion.
3. Most likely fault: the robot action transport/server layer, because discovery reports no action server and the service is inactive. The bridge may also be accepting requests without checking server availability.
4. Check in order: inspect bridge logs and task state; verify the action server process/service and lifecycle; run `ros2 action list/info` and inspect graph/QoS/namespace; call the action directly with a known-safe test; then inspect hardware/controller faults.
5. Do not execute a real motion yet. There is no discovered action server and the service is inactive, so completion and safety cannot be established.

The first statement in each answer is evidence; conclusions beyond the supplied output remain hypotheses to verify.
