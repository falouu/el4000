from datetime import datetime

from pkg.statistics import get_avg, get_percentiles
from pkg import all_data_file

class SessionRecordWrapper:

    FIELDS = [
        "session_type",
        "start",
        "end",
        "duration_minutes",
        "effective_power_p10",
        "effective_power_p50",
        "effective_power_p90",
        "effective_power_p99",
        "effective_power_max",
        "effective_power_avg",
        "voltage_min",
        "voltage_p10",
        "voltage_p50",
        "voltage_p90",
        "voltage_p99",
        "voltage_max",
        "voltage_avg"
    ]

    def __init__(self) -> None:
        self._record_len = len(self.FIELDS)
        self._i_session_type = self.FIELDS.index("session_type")
        self._i_start = self.FIELDS.index("start")
        self._i_end = self.FIELDS.index("end")
        self._i_duration_minutes = self.FIELDS.index("duration_minutes")

        self._i_effective_power_p10 = self.FIELDS.index("effective_power_p10")
        self._i_effective_power_p50 = self.FIELDS.index("effective_power_p50")
        self._i_effective_power_p90 = self.FIELDS.index("effective_power_p90")
        self._i_effective_power_p99 = self.FIELDS.index("effective_power_p99")
        self._i_effective_power_max = self.FIELDS.index("effective_power_max")
        self._i_effective_power_avg = self.FIELDS.index("effective_power_avg")

        self._i_voltage_min = self.FIELDS.index("voltage_min")
        self._i_voltage_p10 = self.FIELDS.index("voltage_p10")
        self._i_voltage_p50 = self.FIELDS.index("voltage_p50")
        self._i_voltage_p90 = self.FIELDS.index("voltage_p90")
        self._i_voltage_p99 = self.FIELDS.index("voltage_p99")
        self._i_voltage_max = self.FIELDS.index("voltage_max")
        self._i_voltage_avg = self.FIELDS.index("voltage_avg")


    def create(self, session_type: str, session_start: datetime, session_end: datetime, records: "list[list]") -> None:
        self.__data = [None] * self._record_len

        self.session_type = session_type
        self.start = session_start
        self.end = session_end
        self.duration_minutes = (session_end - session_start).total_seconds() / 60

        effective_power_percentiles = get_percentiles(records, all_data_file.i_effective_power)

        self.effective_power_p10 = effective_power_percentiles["p10"]
        self.effective_power_p50 = effective_power_percentiles["p50"]
        self.effective_power_p90 = effective_power_percentiles["p90"]
        self.effective_power_p99 = effective_power_percentiles["p99"]
        self.effective_power_max = effective_power_percentiles["max"]
        self.effective_power_avg = get_avg(records, all_data_file.i_effective_power)

        voltage_percentiles = get_percentiles(records, all_data_file.i_voltage)

        self.voltage_min = voltage_percentiles["min"]
        self.voltage_p10 = voltage_percentiles["p10"]
        self.voltage_p50 = voltage_percentiles["p50"]
        self.voltage_p90 = voltage_percentiles["p90"]
        self.voltage_p99 = voltage_percentiles["p99"]
        self.voltage_max = voltage_percentiles["max"]
        self.voltage_avg = get_avg(records, all_data_file.i_voltage)


    def wrap(self, record: list) -> None:
        self.__data = record

    def unwrap(self) -> list:
        return self.__data

    def _to_csv_value(self, input) -> str:
        if isinstance(input, datetime):
            return input.strftime('%Y-%m-%d %H:%M')
        return str(input)


    def get_as_csv_data_line(self) -> str:
        return ",".join(self._to_csv_value(value) for value in self.__data) + "\n"

    def get_csv_header(self) -> str:
        return ",".join(self.FIELDS) + "\n"

    @property
    def session_type(self):
        return self.__data[self._i_session_type]

    @session_type.setter
    def session_type(self, session_type):
        self.__data[self._i_session_type] = session_type

    @property
    def start(self):
        return self.__data[self._i_start]

    @start.setter
    def start(self, start_date):
        self.__data[self._i_start] = start_date

    @property
    def end(self):
        return self.__data[self._i_end]

    @end.setter
    def end(self, end_date):
        self.__data[self._i_end] = end_date

    @property
    def duration_minutes(self):
        return self.__data[self._i_duration_minutes]

    @duration_minutes.setter
    def duration_minutes(self, duration_minutes):
        self.__data[self._i_duration_minutes] = duration_minutes

    @property
    def effective_power_p10(self):
        return self.__data[self._i_effective_power_p10]

    @effective_power_p10.setter
    def effective_power_p10(self, effective_power_p10):
        self.__data[self._i_effective_power_p10] = effective_power_p10

    @property
    def effective_power_p50(self):
        return self.__data[self._i_effective_power_p50]

    @effective_power_p50.setter
    def effective_power_p50(self, effective_power_p50):
        self.__data[self._i_effective_power_p50] = effective_power_p50

    @property
    def effective_power_p90(self):
        return self.__data[self._i_effective_power_p90]

    @effective_power_p90.setter
    def effective_power_p90(self, effective_power_p90):
        self.__data[self._i_effective_power_p90] = effective_power_p90

    @property
    def effective_power_p99(self):
        return self.__data[self._i_effective_power_p99]

    @effective_power_p99.setter
    def effective_power_p99(self, effective_power_p99):
        self.__data[self._i_effective_power_p99] = effective_power_p99

    @property
    def effective_power_max(self):
        return self.__data[self._i_effective_power_max]

    @effective_power_max.setter
    def effective_power_max(self, effective_power_max):
        self.__data[self._i_effective_power_max] = effective_power_max

    @property
    def effective_power_avg(self):
        return self.__data[self._i_effective_power_avg]

    @effective_power_avg.setter
    def effective_power_avg(self, effective_power_avg):
        self.__data[self._i_effective_power_avg] = effective_power_avg

    @property
    def voltage_min(self):
        return self.__data[self._i_voltage_min]

    @voltage_min.setter
    def voltage_min(self, voltage_min):
        self.__data[self._i_voltage_min] = voltage_min

    @property
    def voltage_p10(self):
        return self.__data[self._i_voltage_p10]

    @voltage_p10.setter
    def voltage_p10(self, voltage_p10):
        self.__data[self._i_voltage_p10] = voltage_p10

    @property
    def voltage_p50(self):
        return self.__data[self._i_voltage_p50]

    @voltage_p50.setter
    def voltage_p50(self, voltage_p50):
        self.__data[self._i_voltage_p50] = voltage_p50

    @property
    def voltage_p90(self):
        return self.__data[self._i_voltage_p90]

    @voltage_p90.setter
    def voltage_p90(self, voltage_p90):
        self.__data[self._i_voltage_p90] = voltage_p90

    @property
    def voltage_p99(self):
        return self.__data[self._i_voltage_p99]

    @voltage_p99.setter
    def voltage_p99(self, voltage_p99):
        self.__data[self._i_voltage_p99] = voltage_p99

    @property
    def voltage_max(self):
        return self.__data[self._i_voltage_max]

    @voltage_max.setter
    def voltage_max(self, voltage_max):
        self.__data[self._i_voltage_max] = voltage_max

    @property
    def voltage_avg(self):
        return self.__data[self._i_voltage_avg]

    @voltage_avg.setter
    def voltage_avg(self, voltage_avg):
        self.__data[self._i_voltage_avg] = voltage_avg
