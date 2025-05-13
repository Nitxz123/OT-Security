# OT-Security

This script creates a virtual Modbus TCP PLC that simulates a water tank. It uses holding registers to represent water level, pump, and valve status. A background thread updates the water level based on pump/valve input every 2 seconds. The server runs on port 1502, allowing external Modbus clients to interact. It prints the system status in real-time for monitoring.
