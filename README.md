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

## Modules, Classes, Functions
### Module modbusTcpRaw
Implements class ModbusTcpRaw.
#### Class ModbusTcpRaw
Parent class is pyModbusTCP.client.ModbusClient from https://github.com/sourceperl/pyModbusTCP. \
Provides two new funcions:
* read_holding_raw 
* read_input_raw

They work like "read_holding_registers" and "read_input_registers" but return the raw modbus-result-buffer instead of an integer array. 
This avoids unecessary conversion steps. 

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

##### Class members
