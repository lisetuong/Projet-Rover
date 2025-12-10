import struct
import time

i2c = None  # Global I2C object
MOTOR_I2C_ADDRESS = 0x26

TICKS_PER_REVOLUTION = 2340
SAMPLE_INTERVAL = 0.01  # 0.01 seconds = 10 ms

REG = {
    'TYPE': 0x01,
    'DEADZONE': 0x02,
    'PULSE_PER_LINE': 0x03,
    'PHASE_COUNT': 0x04,
    'WHEEL_DIAMETER': 0x05,
    'SPEED': 0x06,
    'PWM': 0x07,
    'ENCODER_DELTA': [0x10, 0x11, 0x12, 0x13],
    'ENCODER_HIGH': [0x20, 0x22, 0x24, 0x26],
    'ENCODER_LOW':  [0x21, 0x23, 0x25, 0x27],
}

def init_i2c(i2c_instance):
    global i2c
    i2c = i2c_instance

#def write_register(reg, data_bytes):
#    i2c.writeto_mem(MOTOR_I2C_ADDRESS, reg, bytearray(data_bytes))

#def read_register(reg, length):
#    return i2c.readfrom_mem(MOTOR_I2C_ADDRESS, reg, length)

def write_register(reg, data_bytes):
    if i2c is None:
        raise RuntimeError("I2C non initialisée. Appeler motor.init_i2c(i2c) avant.")
    i2c.writeto_mem(MOTOR_I2C_ADDRESS, reg, bytearray(data_bytes))

def read_register(reg, length):
    if i2c is None:
        raise RuntimeError("I2C non initialisée. Appeler motor.init_i2c(i2c) avant.")
    return i2c.readfrom_mem(MOTOR_I2C_ADDRESS, reg, length)

def float_to_bytes(value):
    return struct.pack('<f', value)

# -------------------------
# Motor Configuration for type 3 TT DC Motor
# -------------------------
def set_motor_parameters():
    write_register(REG['TYPE'], [3])                             # Motor type 3: TT encoder motor
    time.sleep(0.05)
    write_register(REG['PHASE_COUNT'], [0x00, 45])               # 45 phase count
    time.sleep(0.05)
    write_register(REG['PULSE_PER_LINE'], [0x00, 13])            # 13 pulse/line
    time.sleep(0.05)
    write_register(REG['WHEEL_DIAMETER'], list(float_to_bytes(65.0)))  # 65 mm diameter
    time.sleep(0.05)
    write_register(REG['DEADZONE'], [0x04, 0xE2])                # 1250 (0x04E2) deadzone
    time.sleep(0.05)


# -------------------------
# Encoder Readings
# -------------------------
def read_total_encoder_counts():  # Total Nb of ticks (wheel position)
    counts = []
    for high_reg, low_reg in zip(REG['ENCODER_HIGH'], REG['ENCODER_LOW']):
        high = read_register(high_reg, 2)
        low = read_register(low_reg, 2)
        value = ((high[0] << 8) | high[1]) << 16 | ((low[0] << 8) | low[1])
        if value & 0x80000000:
            value -= 0x100000000
        counts.append(value)
    return counts


def read_encoder_deltas():       # Nb ticks for 10 ms
    ticks = []
    for reg in REG['ENCODER_DELTA']:
        buf = read_register(reg, 2)
        value = (buf[0] << 8) | buf[1]
        if value & 0x8000:
            value -= 0x10000
        ticks.append(value)
    return ticks

# -------------------------
# RPM Calculation
# -------------------------

def calculate_rpm(ticks, ticks_per_rev=TICKS_PER_REVOLUTION, interval=SAMPLE_INTERVAL):
    return (ticks / ticks_per_rev) * 60 / interval

# -------------------------
# Motor Control
# -------------------------
def control_motor_pwm(p1, p2, p3, p4):
    pwms = []
    for v in (p1, p2, p3, p4):
        pwms.extend([(v >> 8) & 0xFF, v & 0xFF])
    write_register(REG['PWM'], pwms)

# -------------------------
# Conversion PWM <-> Voltage
# -------------------------
PWM_MAX = 2000
V_MAX = 7.34
V_PER_PWM = V_MAX / PWM_MAX

def voltage_to_pwm(voltage):
    """ Convertit une tension moteur (V) en commande PWM (0–2000). """
    # Saturation entre 0 et V_MAX
    voltage = max(0.0 ,min(V_MAX,voltage))
    return int(voltage / V_PER_PWM)

def control_motor_voltage(v1, v2, v3, v4):
    """ Contrôle les moteurs en spécifiant directement une tension en volts.
    0 V -> moteur arrêté,   7.34 V -> PWM = 2000 """
    p1 = voltage_to_pwm(v1)
    p2 = voltage_to_pwm(v2)
    p3 = voltage_to_pwm(v3)
    p4 = voltage_to_pwm(v4)
    control_motor_pwm(p1, p2, p3, p4)

