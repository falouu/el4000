EXPECTED_DATA_FIELDS = ["date", "voltage", "current", "power_factor", "apparent_power", "effective_power"]

expected_header_line = ",".join(EXPECTED_DATA_FIELDS) + "\n"
i_date = EXPECTED_DATA_FIELDS.index("date")
i_voltage = EXPECTED_DATA_FIELDS.index("voltage")
i_current = EXPECTED_DATA_FIELDS.index("current")
i_power_factor = EXPECTED_DATA_FIELDS.index("power_factor")
i_apparent_power = EXPECTED_DATA_FIELDS.index("apparent_power")
i_effective_power = EXPECTED_DATA_FIELDS.index("effective_power")