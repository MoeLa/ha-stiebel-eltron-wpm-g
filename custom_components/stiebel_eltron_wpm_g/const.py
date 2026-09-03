"""Constants for Stiebel Eltron WPM G integration."""

from typing import Final

DOMAIN: Final = "stiebel_eltron_wpm_g"
MANUFACTURER: Final = "Stiebel Eltron"
MODEL: Final = "WPM G"

DEFAULT_PORT: Final = 502
DEFAULT_SCAN_INTERVAL: Final = 30
UNIT_ID: Final = 1

# Register addresses for primary heat pump (WPM G)
# Block 1: Systemwerte (Input Registers 36000+)
REG_ROOM_TEMP: Final = 36000  # Factor: 10, Unit: °C
REG_BUFFER_TEMP: Final = 36001  # Factor: 100, Unit: °C
REG_HEATING_CIRCUIT_1_FLOW: Final = 36002  # Factor: 100, Unit: °C
REG_HEATING_CIRCUIT_1_RETURN: Final = 36007  # Factor: 100, Unit: °C
REG_OUTSIDE_TEMP_AVG: Final = 36100  # Factor: 100, Unit: °C
REG_DHW_TEMP_WEIGHTED: Final = 36101  # Factor: 100, Unit: °C
REG_EVAP_TEMP_HIGH: Final = 36102  # Factor: 100, Unit: °C
REG_COND_TEMP_HIGH: Final = 36103  # Factor: 100, Unit: °C
REG_COND_TEMP_LOW: Final = 36104  # Factor: 100, Unit: °C
REG_SUPERHEAT: Final = 36105  # Factor: 100, Unit: K
REG_SUBCOOLING: Final = 36106  # Factor: 100, Unit: K
REG_PRESSURE_LOW: Final = 36107  # Factor: 100, Unit: bar
REG_PRESSURE_HIGH: Final = 36108  # Factor: 100, Unit: bar
REG_CURRENT_L1: Final = 36109  # Factor: 100, Unit: A
REG_CURRENT_L2: Final = 36110  # Factor: 100, Unit: A
REG_CURRENT_L3: Final = 36111  # Factor: 100, Unit: A
REG_VOLTAGE_L1_N: Final = 36112  # Factor: 100, Unit: V
REG_VOLTAGE_L2_N: Final = 36113  # Factor: 100, Unit: V
REG_VOLTAGE_L3_N: Final = 36114  # Factor: 100, Unit: V
REG_VOLTAGE_L1_L2: Final = 36115  # Factor: 10, Unit: V
REG_VOLTAGE_L2_L3: Final = 36116  # Factor: 10, Unit: V
REG_VOLTAGE_L3_L1: Final = 36117  # Factor: 10, Unit: V
REG_POWER_L1: Final = 36118  # Factor: 1, Unit: W
REG_POWER_L2: Final = 36119  # Factor: 1, Unit: W
REG_POWER_L3: Final = 36120  # Factor: 1, Unit: W
REG_ENERGY_TOTAL: Final = 36121  # Factor: 1, Unit: kWh
REG_COMFORT_MODE: Final = 36122  # Factor: 1, Unit: boolean
REG_DEW_POINT: Final = 36123  # Factor: 100, Unit: °C
REG_BUFFER_SETPOINT: Final = 36124  # Factor: 100, Unit: °C
REG_COMPRESSOR_RUNTIME_LSB: Final = 36050  # Factor: 1, Unit: h
REG_COMPRESSOR_RUNTIME_MSB: Final = 36051  # Factor: 1, Unit: h
REG_AUX_HEATER_RUNTIME_LSB: Final = 36052  # Factor: 1, Unit: h
REG_AUX_HEATER_RUNTIME_MSB: Final = 36053  # Factor: 1, Unit: h
REG_DHW_RUNTIME_LSB: Final = 36054  # Factor: 1, Unit: h
REG_DHW_RUNTIME_MSB: Final = 36055  # Factor: 1, Unit: h
REG_ELECTRICAL_ENERGY_LSB: Final = 36035  # Factor: 10, Unit: kWh
REG_ELECTRICAL_ENERGY_MSB: Final = 36036  # Factor: 10, Unit: kWh

# Block 2: Systemparameter (Holding Registers 47000+)
REG_AUX_HEATER_ENABLE: Final = 47001  # boolean
REG_POOL_AUX_EXT_ENABLE: Final = 47002  # boolean
REG_POOL_AUX_INT_ENABLE: Final = 47003  # boolean
REG_AUX_HEATER_INT_ENABLE: Final = 47004  # boolean
REG_AUX_HEATER_EXT_ENABLE: Final = 47005  # boolean
REG_HOT_GAS_DHW_ENABLE: Final = 47006  # boolean
REG_HOT_GAS_PUMP_ENABLE: Final = 47008  # boolean
REG_CIRC_PUMP_ENABLE: Final = 47012  # boolean
REG_COOLING_ENABLE: Final = 47013  # boolean
REG_ENERGY_METER_ENABLE: Final = 47014  # boolean
REG_DHW_ENABLE: Final = 47016  # boolean
REG_HEATING_ENABLE: Final = 47017  # boolean
REG_POOL_ENABLE: Final = 47021  # boolean
REG_PASSIVE_COOLING_ENABLE: Final = 47023  # boolean
REG_MAX_TEMP: Final = 47024  # Factor: 100, Unit: °C
REG_MIN_TEMP: Final = 47025  # Factor: 100, Unit: °C
REG_DHW_ON_TEMP: Final = 47081  # Factor: 100, Unit: °C
REG_DHW_OFF_TEMP: Final = 47082  # Factor: 100, Unit: °C
REG_POOL_SETPOINT: Final = 47091  # Factor: 100, Unit: °C

# Block 3: Systemstatus (Input Registers 37500+)
REG_EXT_AUX_CONTROL: Final = 37500  # boolean
REG_INT_AUX_STAGE2_CONTROL: Final = 37501  # boolean
REG_HC1_PUMP_CONTROL: Final = 37502  # boolean
REG_CONDENSER_CONTROL: Final = 37503  # boolean
REG_INT_AUX_STAGE1_CONTROL: Final = 37504  # boolean
REG_HOT_GAS_PUMP_CONTROL: Final = 37505  # boolean
REG_BRINE_PUMP_CONTROL: Final = 37506  # boolean
REG_COMPRESSOR_CONTROL: Final = 37663  # boolean
REG_HEAT_PUMP_OFF: Final = 37603  # boolean
REG_HEAT_PUMP_READY: Final = 37604  # boolean

# Alarms/Messages (Input Registers 39000+)
REG_ALARM_LEVEL1: Final = 39000  # boolean
REG_ALARM_LEVEL2: Final = 39001  # boolean
REG_ALARM_LEVEL3: Final = 39002  # boolean
