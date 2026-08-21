# Implementation Plan

## Goal

Deliver a small, framework-independent robot reception application that implements the specified event rules, exposes the required public API, and is supported by executable tests and concise design/diagnostic documentation.

## Approach

1. Model each person's reception lifecycle independently so that presence, pending absence, completed departure, and per-cycle deduplication have one clear owner.
2. Keep conversation and meeting activity as application-level state. An entry or departure that is suppressed is consumed and is not replayed when the interaction ends.
3. Produce immutable `Effect` values only from `handle_event()`. Return a deep, detached snapshot so callers cannot mutate application state.
4. Keep policy code independent of ROS 2, cameras, and hardware. Document adapters as outward dependencies rather than application dependencies.

## Verification

- Add focused `pytest` tests for every required scenario.
- Add edge cases for multiple people, overlapping suppression modes, invalid/out-of-order events, and configurable timeouts where the public contract needs an explicit behavior.
- Run the complete test suite and record the command and result in `REPORT.md`.

## Deliverables

- `robot_application/`: public models and event-driven application logic.
- `tests/`: behavior and snapshot-isolation tests.
- `ARCHITECTURE.md`: boundaries, state ownership, dependency direction, and extension points.
- `REPORT.md`: completion status, verification evidence, limitations, and ROS 2 diagnosis.
- `AI_USAGE.md`: AI assistance and human-verifiable checks.
- `requirements.txt`: test dependency.

## Risks and Decisions to Make Explicit

- The prompt does not prescribe effect-type names or farewell wording; define stable constants and document them.
- Events are processed in non-decreasing timestamp order. Rejecting stale events prevents negative/ambiguous timeout calculations.
- An event without `person_id` is invalid for person entry/exit, but remains valid for global interaction and tick events.
