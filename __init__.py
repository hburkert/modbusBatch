"""
    ModbusBatch: ModbusTCP layer for batched modbus requests.
    Reads register definitions from CSV-Input (YAML, JSON to be done),
    Bulks modbus requests to bunches of up to 120 registers for optimized access,
    Modbus raw-results will be converted to python data-types (U16, U32, S16, S32, CHR/STR).

    Some features:
    - configurable retry mechanism
    - supports little endian double words (aka wordswap)
    - read holding and input registers - no coils
    - register addressing with configurable offset
    - inverter model dependent manipulations of payload

    Modules:
    - mbBatch.py : main classes and functions
    - mbInverter.py: model dependent instructions (naming conventions!)
    - mbUtils.py: conversion utilities
    - modbusTCpRaw: derived from pyModbusTCP.client.ModbusClient
                    returns raw buffer without conversion; avoids unnecessary conversion steps

    Parameters for MbBatch object:
    - host: ip or hostname of modbus-server, required
    - port: int, default 508
    - retry: int, default 3, max retries if modbus fails
    - reg_offset: int, default 0, modbus_address = reg_number - reg_offset
    - reg_wordswap: 0 or 1, 1 means wordswap for doubleword registers
    - file_path: file with register definitions
    - file_type: "csv" only, json and xml to be done
    - inv_model: name of an inverter specific function in mbInverter.py.
                 function will be called after each complete retrieval of batched modbus-requests.
                 See SH10RT example.
    - inv_options: list or dict with additional information for above special function
                   Will be passed with each request payload.

    Synopsis:
        import time
        from modbusBatch.mbBatch import MbBatch
        mb = MbBatch(host="localhost", port=508, retry=3, reg_offset=1,
             reg_wordswap=True, file_type="csv", file_path="./regSH10RT.csv",
             inv_model="SH10RT", inv_options=[<additional options for special function SH10RT>])

        # endless application loop

        while mb.process_batches():
            print(mb.results)
            # check end of program ???
            # or
            time.sleep(10)

        exit( 12 )
"""
# Package version
VERSION = '0.1.0'
