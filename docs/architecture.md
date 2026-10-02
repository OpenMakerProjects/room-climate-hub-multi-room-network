# Architecture

```text
Sensors -> validation and filtering -> telemetry -> output/alert
                                      |
                                      +-> Local only telemetry and logs
```

The implementation separates acquisition, decision logic, output handling, and telemetry. Hardware-specific access is kept at the edge so the core behavior can be tested with simulated readings.
