# Test plan

## Static checks

1. Run `python tools/validate.py`.
2. Confirm the firmware or application starts without missing configuration.
3. Compare the assembled wiring with `docs/wiring.md` and component datasheets.

## Functional checks

1. Start with simulated or disconnected actuators.
2. Feed low, nominal, and high readings into the controller.
3. Confirm the **telemetry** behavior matches the serial or console output.
4. Disconnect one sensor and confirm the system enters a safe state.
5. Restore the sensor and verify recovery requires an intentional acknowledgement for latched safety modes.

## Acceptance criteria

- Telemetry includes a timestamp, state, input readings, and output state.
- Invalid readings do not command an actuator on.
- The output changes only after the configured threshold and debounce checks pass.
- The steps in the README reproduce the demonstration.
