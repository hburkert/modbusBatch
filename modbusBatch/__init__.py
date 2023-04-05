"""
    ModbusBatch: ModbusTCP layer for high-speed batched modbus requests.
    Reads register definitions from CSV-Input (YAML, JSON to be done).
    Bulks modbus requests to bunches of up to 120 registers for optimized access
    which are handled in one transaction.
    Modbus raw-results will be converted to python data-types (integer, float, utf8-string).

    Some features:
    - configurable retry mechanism
    - supports little endian double words (aka wordswap)
    - read holding and input registers - no coils
    - register addressing with configurable offset

    Modules:
    - mbBatch.py : main classes and functions
    - mbUtils.py: conversion utilities
    - modbusTCpRaw: derived from pyModbusTCP._client.ModbusClient
                    returns raw buffer without conversion; avoids unnecessary conversion steps

    Parameters for MbBatch object:
    - host: ip or hostname of modbus-server, required
    - port: int, default 508
    - retry: int, default 3, max retries if modbus fails
    - reg_offset: int, default 0, modbus_address = reg_number - reg_offset
    - reg_wordswap: 0 or 1, 1 means wordswap for doubleword registers
    - file_path: file with register definitions
    - file_type: "csv" only, json and xml to be done

    Synopsis:
        import time
        from modbusBatch.mbBatch import MbBatch
        mb = MbBatch(host="localhost",
             port=502,
             retry=3,
             reg_offset=1,
             reg_wordswap=True,
             file_type="csv",
             file_path="./regSH10RT.csv")

        # endless application loop
        while mb.process_batches(close_socket=True):
            do_some_thing_with(mb._results)
            print(mb._results)
            store(mb.result)
            check_end_of_loop() and exit(0)
            times.sleep(some_time)
        exit( 1 )
"""
# Package version
VERSION = '0.1.3'
