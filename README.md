# modbusBatch
ModbusTCP layer for high-speed batched modbus requests.

* Reads register definitions from CSV-Input. 
* Bulks modbus requests to bunches of up to 120 registers for optimized access 
* Requests are handled in one transaction.
* Modbus raw-results will be converted to python data-types (integer, float, utf8-string).
* Configurable retry mechanism
* Little Endian double words aka "wordswap" is supported.
* Reads holding and input registers, no coils, no writing.
* An offset for register addressing may be given.


## Intended Use
Cyclic polling of (many) inverter modbus registers via TCP.

## Installation
```bash
sudo pip install git+https://github.com/hburkert/modbusBatch.git
```

## Synopsis
```python
import time
from modbusBatch.mbBatch import MbBatch
mb = MbBatch(host="localhost",
             port=502,
             retry=3,
             reg_offset=1,
             reg_wordswap=True,
             file_type="csv",
             file_path="./SungrowSHxxRT.csv",
             debug=False)

# endless application loop
while mb.process_batches(close_socket=True):
    # do_some_thing_with(mb.results)
    print(mb.results)
    #store(mb.results)
    #check_end_of_loop() and exit(0)
    time.sleep(20)
exit( 1 )
```

## CSV register specification
````text
# <- this is a comment line
# First non-comment must be csv.header
# Hdr:
reg_type, reg_number, reg_name, reg_desc, measurement_unit, data_type, data_length, unit_id, scaling_factor, reserved
i,4990,serial_number,"Seriennummer",,CHR,5,1,1,
i,5003,daily_output_energy,"This day PV generation and battery discharge",kWh,U16,,1,0.1,
i,5004,total_output_energy,"Total PV generation and battery discharge",kWh,U32,,1,0.1,
i,5008,inside_temperature,"Inside Temperature","deg C",S16,,1,0.1,
i,5009,total_apparent_power,"Scheinleistung gesamt","VA",U32,,1,1,
i,5011,mppt1_voltage,"MPPT1 Voltage","V",U16,,1,0.1,
...
h,5000,system_clock_year,,,U16,1,1,1,
h,5001,system_clock_month,,,U16,1,1,1,
h,5002,system_clock_day,,,U16,1,1,1,
h,5003,system_clock_hour,,,U16,1,1,1,
h,5004,system_clock_minute,,,U16,1,1,1,
h,5005,system_clock_second,,,U16,1,1,1,
....
# registers from unit_id 200:
i,10743,battery_temperature,"","C",S16,,200,0.1,
i,10744,battery_level_abs,"absolute battery level","%",U16,,200,0.1,
````

Order of rows is arbitrary. Internally they will be sorted by `unit_id`, `data_type` and `reg_number`. \
``reg_type`` must be first column, order of other columns is arbitrary.
Columns `reg_type` `reg_number` `reg_name` are always required. Other columns have defaults.\
`data_len` should be given for `data_type` 'str' or 'chr'. Length is expressed in number of registers. Length = 5 results in a string of 10 bytes.

**Warning - Definitions should not overlap:**
```text
i,1000,foo,'',,,chr,100,,,,
i,1099,bar,'',,,u16,1,,,,   <=== overlaps with prev register
```

## Modules, Classes, Functions
### Module modbusTcpRaw
Implements class ModbusTcpRaw.
#### Class ModbusTcpRaw
Parent class is pyModbusTCP.client.ModbusClient from https://github.com/sourceperl/pyModbusTCP. \
Provides two new functions:
* read_holding_raw 
* read_input_raw

They work like "read_holding_registers" and "read_input_registers" but return the raw modbus-result-buffer instead of an integer array. 
This avoids unnecessary conversion steps. 

### Module mbBatch
Implements class MbBatch

#### Class MbBatch
##### Constructor: 
MbBatch(host="localhost", port=502, retry=3, reg_offset=0, reg_wordswap=True, file_type="csv", file_path="registers.csv") \
where:
- host - name or address of modbus host
- port - port number, usually 502
- retry - maximum retries before returning an error
- reg_offset - offset for register addressing. This offset will be subtracted from external register-number. 
- reg_wordswap - True/False. True means U32/S32 register pairs are little endian encoded (Sungrow, SolaX, ...)
- file_type - only "csv" is supported
- file_path - file with register definitions 
- debug - debug flag for modbusTcpRaw 

Function `__init__` stores register specifications from csv-file in 
internal dataclasses (see below) and generates optimized modbus requests.

##### Class members
- dataclass `MbReg` - one Modbus register from CSV
- - reg_type - i=input, h=holding register
- - reg_number - external register number includes offset
- - reg_name - name of register, python name, preferable snake_case
- - reg_desc - optional descriptive text
- - measurement_unit - optional, e.g. W, A, V, kWh
- - data_type - data type: u16, s16, u32, s32, str, chr
- - data_length - needed for str, chr; otherwise derived from data_type
- - scaling_factor - default 1
- - unit_id - modbus unit-id, default 1, there may be different unit-ids (Sungrow!)
- - precision - precision of register value, derived from scaling_factor


- list `MbRegs` - list of `MbReg`, all modbus registers


- dataclass `MbReq` - represents one modbus request
- - unit_id - modbus unit-id, default 1, there may be different unit-ids (Sungrow!)
- - reg_type - i=input, h=holding register
- - address - modbus address (reg_number - offset)
- - quantity - number of registers to read, max. 120
- - from_x - index of first corresponding register in `MbRegs`
- - to_x - index of first corresponding register in `MbRegs`

  Modbus requests are grouped by `unit_id` and `reg_type` and limited to 120 registers.\
**Warning**: Overlapping register definitions may lead to misbehaviour.


- list `MbReqs` - list of `MbReq`, all modbus requests


- dict `results` - after successful retrieval of _all_ registers you will find them here.


- function ``process_batches(close_socket: bool = True)``\
This polling function returns True on success, False on failure.\
Parameter `close_socket=True` closes socket connection after processing the batch.
`close_socket=False` leads to malfunction for Sungrow Inverters. Try it.
  

