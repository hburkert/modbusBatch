"""
 Inverter dependent functions
 Function will be called after complete register retrieval.
 Function name should reflect inverter modell and a layout version e.g. 
 SolaxG3_Micha or SHxxRT_MySQL.
 Functions receive results (dict) and options (dict) from MbBatch as arguments

"""
import logging
log = logging.getLogger(__name__)


def SHxxRT_MySQL(results: {}, options: {} = None):
    _options = options
    if options is None:
        _options = dict()
    try:
        results['device_id'] = int(_options["DB_DEVICE_ID"])
        results['time_sec'] = '%04d-%02d-%02d %02d:%02d:%02d' % \
                              (results['system_clock_year'],
                               results['system_clock_month'],
                               results['system_clock_day'],
                               results['system_clock_hour'],
                               results['system_clock_minute'],
                               results['system_clock_second'],
                               )
        results['mppt1_power'] = results['mppt1_current'] * results['mppt1_voltage']
        results['mppt2_power'] = results['mppt2_current'] * results['mppt2_voltage']
        results['global_error_flag'] = \
            results['inverter_alarm'] + \
            results['grid_side_fault'] + \
            results['system_fault_1'] + \
            results['system_fault_2'] + \
            results['dc_side_fault'] + \
            results['permanent_fault'] + \
            results['bdc_side_fault'] + \
            results['bdc_side_permanent_fault']
        results['bms_status'] = \
            results['battery_fault'] + \
            results['battery_alarm'] + \
            results['bms_alarm'] + \
            results['system_fault_2'] + \
            results['bms_protection'] + \
            results['bms_fault_1'] + \
            results['bms_fault_2'] + \
            results['bms_alarm_2']
        if (results['running_state'] >> 2) & 0x01:
            results['battery_power'] *= -1
    except KeyError as e:
        log.error(f"key error in SHxxRT_MySQL : {e}")
        exit(14)

    sun_rise = _options["SUN_RISE"]
    sun_set = _options["SUN_SET"]
    hhmm = results['time_sec'][11:16]

    if results['global_error_flag'] == 0 and \
        results['bms_status'] in (0, 16384) and \
        10 <= results['battery_temperature'] <= 25 and \
        results['inside_temperature'] <= 50 and \
        (results['system_state'] in (0x10, 0x20, 0x40, 0x0800, 0x4000) or
         (results['system_state'] == 0x08 and (sun_rise >= hhmm or hhmm >= sun_set))):
        results['ERROR_CODE'] = 0
        return
    results['ERROR_CODE'] = 1
    results['ERROR_TEXT'] = ""
    results['ERROR_TIME'] = results['time_sec']
    results['ERROR_TEXT'] += "Inverter error\n" if results['global_error_flag'] > 0 else ''
    results['ERROR_TEXT'] += f" - inverter_alarm: {results['inverter_alarm']}\n" if results['inverter_alarm'] else ""
    results['ERROR_TEXT'] += f" - grid_side_fault: {results['grid_side_fault']}\n" if results['grid_side_fault'] else ""
    results['ERROR_TEXT'] += f" - system_fault_1: {results['system_fault_1']}\n" if results['system_fault_1'] else ""
    results['ERROR_TEXT'] += f" - system_fault_2: {results['system_fault_2']}\n" if results['system_fault_2'] else ""
    results['ERROR_TEXT'] += f" - dc_side_fault: {results['dc_side_fault']}\n" if results['dc_side_fault'] else ""
    results['ERROR_TEXT'] += f" - bdc_side_fault: {results['permanent_fault']}\n" if results['permanent_fault'] else ""
    results['ERROR_TEXT'] += f" - bdc_side_fault: {results['bdc_side_fault']}\n" if results['bdc_side_fault'] else ""
    results['ERROR_TEXT'] += f"System temperature too high: {results['inside_temperature']}\n" \
        if results['inside_temperature'] >= 50 else ""
    results['ERROR_TEXT'] += f"Battery temperature out of range: {results['battery_temperature']}\n" \
        if results['battery_temperature'] >= 25 or results['battery_temperature'] <= 10 else ""
    results['ERROR_TEXT'] += f"Unexpected system state: {results['system_state']}\n" \
        if results['system_state'] not in (0x08, 0x10, 0x20, 0x40, 0x0800, 0x4000) else ""
    results['ERROR_TEXT'] += f"Unexpected intraday standby of inverter: {sun_rise} < {hhmm} < {sun_set}\n" \
        if results['system_state'] == 0x08 and sun_rise <= hhmm <= sun_set else ""

    results['ERROR_TEXT'] += "BMS error\n" if results['bms_status'] > 0 else ''
    results['ERROR_TEXT'] += f" - battery_fault: {results['battery_fault']}\n" if results['battery_fault'] else ""
    results['ERROR_TEXT'] += f" - battery_alarm: {results['battery_alarm']}\n" if results['battery_alarm'] else ""
    results['ERROR_TEXT'] += f" - bms_alarm: {results['bms_alarm']}\n" if results['bms_alarm'] else ""
    results['ERROR_TEXT'] += f" - system_fault_2: {results['system_fault_2']}\n" if results['system_fault_2'] else ""
    results['ERROR_TEXT'] += f" - bms_protection: {results['bms_protection']}\n" if results['bms_protection'] else ""
    results['ERROR_TEXT'] += f" - bms_fault_1: {results['bms_fault_1']}\n" if results['bms_fault_1'] else ""
    results['ERROR_TEXT'] += f" - bms_fault_2: {results['bms_fault_2']}\n" if results['bms_fault_2'] else ""
    results['ERROR_TEXT'] += f" - bms_alarm_2: {results['bms_alarm_2']}\n" if results['bms_alarm_2'] else ""


def doNothing(*_args):
    pass


"""
 Function alias for inverter specific function. 
 Will be dynamically reassigned to one of the above functions.
 See mbBatch.py, parameter "inv_model".
"""
afterModbusComplete = doNothing
