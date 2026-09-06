---
name: hermes-apm-flight-control-center
trigger_words: ['apm-flight-controller', 'apm', 'flight-controller', 'flight-control', 'drone', 'ahrs', 'mavlink', 'ahrs-tuning', 'flight-dynamics']
category: hardware
description: "Complete flight control systems management with APM ArduPilot: hardware integration, sensor monitoring, servo control, calibration, diagnostics, and production deployment workflows"
---

# Hermes APM/Flight Control Center

A comprehensive umbrella skill for configuring, deploying, and maintaining flight control systems using APM ArduPilot firmware. Consolidates all flight dynamics, sensor monitoring, servo control, and mission systems under one conceptual umbrella.

## Overview

This skill serves as a unified interface for:
- Flight controller configuration and tuning
- Sensor data acquisition and processing
- MAVLink protocol operations
- Servo/PWM channel control and calibration
- Flight mode management
- Emergency procedures and fail-safes

## Core Capabilities

### APM Configuration & Monitoring
- **Port Configuration**: Auto-detect common flight controller serial ports (/dev/ttyACM*, /dev/ttyUSB*)
- **Bitrate & Protocol**: MAVLink v2, automatic baud rate detection (57600/115200/921600)
- **Firmware Validation**: Verify APM / ArduPilot firmware signature and version compatibility
- **Parameter Management**: Read, write, and backup flight controller parameters


### Sensor Telemetry
- **IMU Data**: 3-axis accelerometer (m/s²), 3-axis gyroscope (rad/s), temperature (°C)
- **Barometer**: Atmospheric pressure (hPa), altitude (m)
- **GPS/GNSS**: Satellite count, HDOP/VDOP, altitude (m), location (lat/lon), time sync
- **Power System**: Voltage (V), current (A), power (W), capacity (mAh)
- **Attitude**: Euler angles, quaternion representation, heading
- **RSSI**: Remote control signal strength monitoring


### Servo & Actuator Control
- **Individual Channel Control**: PWM outputs 1000-2000µs range (±50%)
- **Flight Mode Management**: 6+ modes (Stabilize, AltHold, PosHold, Auto, Loiter, RTL, Land)
- **Safety Switch**: Direct emergency servo arrest via channel override
- **Channel Mapping**: Throttle, Aileron, Elevator, Rudder, Mode, Aux1-4
- **Failsafe Recovery**: RSSI loss, battery critical recovery protocols


### Calibration & Testing
- **Three-Point Calibration**: Min/Mid/Max servo endpoints
- **IMU/Temperature Calibration**: In-situ thermal compensation matrix
- **Rudder Effectiveness**: Real time control authority envelope testing
- **Channel Response**: Servo speed, deadzone measurement
- **Battery Threshold Tuning**: Critical voltage alarms


### Mission Systems
- **MAVLink Mission Upload**: Waypoint sequences including altitude, speed, gimbal commands
- **Geo-Fence Enforcement**: Boundary definition and violation handling
- **Return-to-Launch (RTL)**: Automated recovery with altitude tracking
- **Mission Critical Sensors**: Pre-flight validation
- **Emergency Waypoints**: Pre-defined recovery coordinates


## Diagnostic Workflows

### Real-time Status Monitoring
- Monitor flight status every 500ms
- Monitor sensors every 250ms
- Pre-flight validation checklist
- Error detection matrix with recovery protocols

## Integration Patterns

### Ground Control Station Mode
- Flight planning via MAVLink commands
- Real-time telemetry streaming
- Automatic failsafe control takeover

### Research & Development
- Calibration automation sequences
- Aerodynamic testing (IMU vibration analysis, PID tuning)
- Protocol validation
- Hardware-in-the-loop testing

### Production Use Cases
- NDVI Agriculture flights
- Inspection Services (power lines, wind turbines, PV arrays)
- Search & Rescue missions
- Mapping & Surveying with LiDAR/photogrammetry

## Safety Protocols

### Pre-flight (Comprehensive)
1. Power System Verification: 20V < V_battery < 35V
2. Servo Endstop Verification: Display confirmed output positions
3. GPS Quality Check: HDOP < 1.5, satellites > 6
4. IMU Calibration: Reject saturation > 95%
5. Radio Link Test: RSSI > 85% for 10s

### Emergency Escalation
1. Switch to Stabilize then Manual
2. Absolute Throttle Cut (900µs kills motors)
3. Geofence Enforcement to Home GPS
4. Power Descent to minimum safe altitude (1.5m)
5. Motor disarm sequence, transtion to land mode

## Maintenance & Calibration

### Routine Calibration
- Servo travel test: min/max/neutral positions ±20µs tolerance
- Shock absorber integrity check
- Temperature range operation: -10°C to 70°C
- Connectivity verification: USB/serial port integrity

### Tear-down Procedures
- Capacitor inspection: leakage/bulging visual check
- Voltage regulator temperature: ≤60°C under load
- Connector cleaning: corrosion prevention
- Motor health: propeller balance, spin-up diagnostics

## Future Extensions

### Multi-vehicle Coordination
- Swarm control protocol
- Shared mission management across fleet
- Coordinated survey missions

### AI Integration
- Computer vision lens (ArUco tag detection, SLAM)
- Autonomous decision making via reinforcement learning
- Predictive maintenance: IMU anomaly detection

### Cloud Connectivity
- Real-time telemetry stream to cloud dashboard
- Post-flight analytics and flight envelope analysis
- OTA firmware updates via cloud server

---
references:
  01-telemetry-reference.md: "Standard MAVLink telemetry message format and units"
  02-servo-calibration-guide.md: "Multi-point calibration procedure with tolerance tables"
  03-preflight-checklist.md: "Comprehensive pre-flight validation checklist"
  04-failsafe-protocols.md: "Emergency procedure reference"
  05-diagnostic-commands.md: "CLI commands for troubleshooting"
templates:
  preflight.sh: "Automated pre-flight validation script"
scripts:
  battery-monitor.py: "Real-time battery voltage monitoring with warning thresholds"
  apm-sanity-check.py: "System integrity verification tool"
  calibration-sequence.sh: "Multi-stage calibration workflow generator"