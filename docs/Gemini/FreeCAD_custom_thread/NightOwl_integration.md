# Integration of the NightOwl Multi-Material Unit with the QIDI Q1 Pro
# Интеграция NightOwl Multi-Material Unit с QIDI Q1 Pro

This document provides step-by-step instructions for connecting the Night Owl MMU to a QIDI Q1 Pro, utilizing an ERB controller.
Этот документ содержит пошаговые инструкции по подключению Night Owl MMU к QIDI Q1 Pro с использованием контроллера ERB.

---

## Hardware Configuration Note
## Примечание по аппаратной конфигурации

**English:** The Night Owl MMU differs from traditional MMUs by using exactly **two steppers** (e.g., dual feeder/gear system) and **no selector stepper**. It also uses a servo-based filament cutter.
**Русский:** Night Owl MMU отличается от традиционных MMU тем, что использует ровно **два шаговых двигателя** (например, двойная система подачи/шестерней) и **не имеет двигателя селектора**. Также используется серво-резак для филамента.

---

## Pin Configuration & Klipper Setup
## Конфигурация пинов и настройка Klipper

**English:** Below is the explicit configuration mapping for the two steppers on the ERB, the servo cutter, and the retention of the stock QIDI hall sensor.
**Русский:** Ниже приведена точная конфигурация для двух шаговых двигателей на ERB, серво-резака и сохранения штатного датчика Холла QIDI.

```ini
# 1. MCU Definition / Определение MCU
[mcu nightowl]
serial: /dev/serial/by-id/usb-Klipper_rp2040_YOUR_ID_HERE

# 2. Stepper 1 (Main Feeder) / Шаговый двигатель 1 (Основная подача)
[tmc2209 stepper_nightowl_1]
uart_pin: nightowl:gpio9
run_current: 0.6
[stepper_nightowl_1]
step_pin: nightowl:gpio10
dir_pin: nightowl:gpio11
enable_pin: !nightowl:gpio12
microsteps: 16
rotation_distance: 22.67

# 3. Stepper 2 (Secondary Feeder) / Шаговый двигатель 2 (Вторичная подача)
# (Used instead of a selector / Используется вместо селектора)
[tmc2209 stepper_nightowl_2]
uart_pin: nightowl:gpio22
run_current: 0.6
[stepper_nightowl_2]
step_pin: nightowl:gpio16
dir_pin: nightowl:gpio15
enable_pin: !nightowl:gpio14
microsteps: 16
rotation_distance: 22.67

# 4. Servo Cutter Control / Управление серво-резаком
# Connect to the 5V Servo pin on the ERB / Подключите к пину 5V Servo на ERB
[servo ercf_cutter]
pin: nightowl:gpio29
maximum_servo_angle: 180
minimum_pulse_width: 0.0005
maximum_pulse_width: 0.0025

# 5. Stock QIDI Toolhead Sensor / Штатный датчик печатающей головки QIDI
# Re-route the stock sensor to act as the toolhead sensor / Перенаправление штатного датчика
[filament_switch_sensor toolhead_sensor]
pin: ^!PC3  # Check your QIDI printer.cfg for the exact pin / Проверьте printer.cfg вашего QIDI для точного пина
pause_on_runout: False
```

---

## Testing / Тестирование

**English:**
1. Test Servo: `SET_SERVO SERVO=ercf_cutter ANGLE=90`
2. Test Stepper 1: `FORCE_MOVE STEPPER=stepper_nightowl_1 DISTANCE=10 VELOCITY=5`
3. Test Stepper 2: `FORCE_MOVE STEPPER=stepper_nightowl_2 DISTANCE=10 VELOCITY=5`

**Русский:**
1. Тест серво: `SET_SERVO SERVO=ercf_cutter ANGLE=90`
2. Тест мотора 1: `FORCE_MOVE STEPPER=stepper_nightowl_1 DISTANCE=10 VELOCITY=5`
3. Тест мотора 2: `FORCE_MOVE STEPPER=stepper_nightowl_2 DISTANCE=10 VELOCITY=5`

---

# Night Owl MMU: Advanced Control & Integration
# Night Owl MMU: Дополнительное управление и интеграция

This guide explains how to toggle your MMU usage and how to interact with the system given the QIDI Q1 Pro's proprietary interface limitations.
Это руководство объясняет, как переключать режим использования MMU и как взаимодействовать с системой, учитывая ограничения проприетарного интерфейса QIDI Q1 Pro.

---

## 1. Switching MMU State (Enabled/Disabled)
## 1. Переключение состояния MMU (Вкл/Выкл)

**English:**
Since the MMU is integrated via Happy Hare, there isn't a hard "kill switch." Instead, you should create a "Bypass" macro in your `printer.cfg`. This macro will tell the printer to ignore the MMU logic and treat the printer as a standard single-material machine.

Add this to your `printer.cfg` or `mmu_macros.cfg`:

```ini
[gcode_macro TOGGLE_MMU]
variable_mmu_enabled: True
gcode:
    {% if printer["gcode_macro TOGGLE_MMU"].mmu_enabled %}
        SET_GCODE_VARIABLE MACRO=TOGGLE_MMU VARIABLE=mmu_enabled VALUE=False
        RESPOND MSG="MMU Disabled - Single Material Mode Active"
    {% else %}
        SET_GCODE_VARIABLE MACRO=TOGGLE_MMU VARIABLE=mmu_enabled VALUE=True
        RESPOND MSG="MMU Enabled - Multi-Material Mode Active"
    {% endif %}
```

**Русский:**
Поскольку MMU интегрирован через Happy Hare, нет "жесткого" выключателя. Вместо этого рекомендуется создать макрос «обхода» (Bypass) в вашем `printer.cfg`. Этот макрос скажет принтеру игнорировать логику MMU и работать как обычный одноматериальный принтер.

Добавьте это в ваш `printer.cfg` или `mmu_macros.cfg`:

```ini
[gcode_macro TOGGLE_MMU]
variable_mmu_enabled: True
gcode:
    {% if printer["gcode_macro TOGGLE_MMU"].mmu_enabled %}
        SET_GCODE_VARIABLE MACRO=TOGGLE_MMU VARIABLE=mmu_enabled VALUE=False
        RESPOND MSG="MMU отключен - Одноматериальный режим"
    {% else %}
        SET_GCODE_VARIABLE MACRO=TOGGLE_MMU VARIABLE=mmu_enabled VALUE=True
        RESPOND MSG="MMU включен - Многоматериальный режим"
    {% endif %}
```

---

## 2. Controlling from the Printer Screen
## 2. Управление с экрана принтера

**English:**
**Warning:** The stock QIDI Q1 Pro screen is a "walled garden." It is hardcoded to interact with QIDI's proprietary Klipper implementation and does not recognize the complex menu structures required by Happy Hare (ERCF).

*   **Can you control it from the screen?** No, not effectively. The screen cannot display the Happy Hare status, load/unload buttons, or servo calibration menus.
*   **The Solution:** Access your printer's IP address from a browser on your PC or phone (e.g., http://192.168.x.x). You will see the standard Mainsail or Fluidd interface, which provides full control over the Night Owl MMU, including status indicators, servo testing, and tool changing.

**Русский:**
**Внимание:** Штатный экран QIDI Q1 Pro — это «закрытая система». Он жестко запрограммирован на взаимодействие с проприетарной реализацией Klipper от QIDI и не распознает сложные структуры меню, требуемые Happy Hare (ERCF).

*   **Можно ли управлять с экрана?** Нет, полноценно — нет. Экран не может отображать статус Happy Hare, кнопки загрузки/выгрузки или меню калибровки сервопривода.
*   **Решение:** Зайдите на IP-адрес вашего принтера через браузер на компьютере или телефоне (например, http://192.168.x.x). Вы увидите стандартный интерфейс Mainsail или Fluidd, который предоставляет полный контроль над Night Owl MMU, включая индикаторы состояния, тестирование сервопривода и смену инструмента.
