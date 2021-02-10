EESchema Schematic File Version 4
LIBS:alto-cache
EELAYER 26 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Connector:Raspberry_Pi_2_3 PI1
U 1 1 5DAE1CB6
P 5950 3950
F 0 "PI1" H 5950 5650 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 5950 5550 50  0000 C CNN
F 2 "Socket_Strips:Socket_Strip_Straight_2x20_Pitch2.54mm" H 5950 3950 50  0001 C CNN
F 3 "https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf" H 5950 3950 50  0001 C CNN
	1    5950 3950
	1    0    0    -1  
$EndComp
NoConn ~ 5150 3450
NoConn ~ 5150 4150
NoConn ~ 5150 4650
NoConn ~ 6750 3650
$Comp
L pspice:R R2
U 1 1 5DAE3D9E
P 4300 4850
F 0 "R2" V 4095 4850 50  0000 C CNN
F 1 "330" V 4186 4850 50  0000 C CNN
F 2 "Resistors_Universal:Resistor_SMD+THTuniversal_0805to1206_RM10_HandSoldering" H 4300 4850 50  0001 C CNN
F 3 "~" H 4300 4850 50  0001 C CNN
	1    4300 4850
	0    -1   1    0   
$EndComp
$Comp
L pspice:R R1
U 1 1 5DAE3E17
P 4300 4350
F 0 "R1" V 4095 4350 50  0000 C CNN
F 1 "330" V 4186 4350 50  0000 C CNN
F 2 "Resistors_Universal:Resistor_SMD+THTuniversal_0805to1206_RM10_HandSoldering" H 4300 4350 50  0001 C CNN
F 3 "~" H 4300 4350 50  0001 C CNN
	1    4300 4350
	0    -1   1    0   
$EndComp
$Comp
L pspice:R R4
U 1 1 5DAE4DE5
P 7600 4150
F 0 "R4" V 7395 4150 50  0000 C CNN
F 1 "330" V 7486 4150 50  0000 C CNN
F 2 "Resistors_Universal:Resistor_SMD+THTuniversal_0805to1206_RM10_HandSoldering" H 7600 4150 50  0001 C CNN
F 3 "~" H 7600 4150 50  0001 C CNN
	1    7600 4150
	0    1    1    0   
$EndComp
$Comp
L pspice:R R3
U 1 1 5DAE4F89
P 7600 3750
F 0 "R3" V 7395 3750 50  0000 C CNN
F 1 "330" V 7486 3750 50  0000 C CNN
F 2 "Resistors_Universal:Resistor_SMD+THTuniversal_0805to1206_RM10_HandSoldering" H 7600 3750 50  0001 C CNN
F 3 "~" H 7600 3750 50  0001 C CNN
	1    7600 3750
	0    1    1    0   
$EndComp
Wire Wire Line
	5550 5250 5650 5250
Connection ~ 5650 5250
Wire Wire Line
	5650 5250 5750 5250
Connection ~ 5750 5250
Wire Wire Line
	5750 5250 5850 5250
Connection ~ 5850 5250
Wire Wire Line
	5850 5250 5950 5250
Connection ~ 5950 5250
Wire Wire Line
	5950 5250 6050 5250
Connection ~ 6050 5250
Wire Wire Line
	6050 5250 6150 5250
Connection ~ 6150 5250
Wire Wire Line
	6150 5250 6250 5250
$Comp
L power:GND #PWR03
U 1 1 5DAE5D19
P 5950 5450
F 0 "#PWR03" H 5950 5200 50  0001 C CNN
F 1 "GND" H 5955 5277 50  0000 C CNN
F 2 "" H 5950 5450 50  0001 C CNN
F 3 "" H 5950 5450 50  0001 C CNN
	1    5950 5450
	1    0    0    -1  
$EndComp
Wire Wire Line
	5950 5450 5950 5250
$Comp
L pspice:R R5
U 1 1 5DAE96BE
P 4300 3350
F 0 "R5" V 4095 3350 50  0000 C CNN
F 1 "330" V 4186 3350 50  0000 C CNN
F 2 "Resistors_Universal:Resistor_SMD+THTuniversal_0805to1206_RM10_HandSoldering" H 4300 3350 50  0001 C CNN
F 3 "~" H 4300 3350 50  0001 C CNN
	1    4300 3350
	0    -1   1    0   
$EndComp
NoConn ~ 6750 3050
NoConn ~ 6750 3150
NoConn ~ 5150 3550
NoConn ~ 5150 4250
NoConn ~ 6750 4050
$Comp
L Connector_Generic:Conn_02x01 J3
U 1 1 5DB0E69C
P 8150 3750
F 0 "J3" H 8200 3950 50  0000 C CNN
F 1 "switch L" H 8200 3876 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 8150 3750 50  0001 C CNN
F 3 "~" H 8150 3750 50  0001 C CNN
	1    8150 3750
	-1   0    0    -1  
$EndComp
$Comp
L power:GND #PWR01
U 1 1 5DB0EA7A
P 8550 4950
F 0 "#PWR01" H 8550 4700 50  0001 C CNN
F 1 "GND" H 8555 4777 50  0000 C CNN
F 2 "" H 8550 4950 50  0001 C CNN
F 3 "" H 8550 4950 50  0001 C CNN
	1    8550 4950
	-1   0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_02x01 J4
U 1 1 5DB0EA80
P 8150 4150
F 0 "J4" H 8200 4367 50  0000 C CNN
F 1 "switch R" H 8200 4276 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 8150 4150 50  0001 C CNN
F 3 "~" H 8150 4150 50  0001 C CNN
	1    8150 4150
	-1   0    0    -1  
$EndComp
Wire Wire Line
	8350 3750 8550 3750
$Comp
L Connector_Generic:Conn_02x01 J5
U 1 1 5DBE2060
P 3750 3350
F 0 "J5" H 3800 3550 50  0000 C CNN
F 1 "led 0" H 3800 3476 50  0000 C CNN
F 2 "LEDs:LED_D5.0mm" H 3750 3350 50  0001 C CNN
F 3 "~" H 3750 3350 50  0001 C CNN
	1    3750 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	5850 2650 5850 2550
Wire Wire Line
	5850 2550 5750 2550
Wire Wire Line
	5750 2650 5750 2550
Connection ~ 5750 2550
Wire Wire Line
	5750 2550 5450 2550
Text Label 5450 2550 2    50   ~ 0
5V
$Comp
L Connector_Generic:Conn_01x03 J1
U 1 1 5DBE742E
P 3750 4550
F 0 "J1" V 3623 4730 50  0000 L CNN
F 1 "servo L" V 3714 4730 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 3750 4550 50  0001 C CNN
F 3 "~" H 3750 4550 50  0001 C CNN
	1    3750 4550
	0    -1   1    0   
$EndComp
Wire Wire Line
	4050 4350 3850 4350
Text Label 3750 4250 0    50   ~ 0
VBUS
Wire Wire Line
	3750 4250 3750 4350
$Comp
L Connector_Generic:Conn_01x03 J2
U 1 1 5DBF65DC
P 3750 5050
F 0 "J2" V 3623 5230 50  0000 L CNN
F 1 "servo R" V 3714 5230 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 3750 5050 50  0001 C CNN
F 3 "~" H 3750 5050 50  0001 C CNN
	1    3750 5050
	0    -1   1    0   
$EndComp
Wire Wire Line
	4050 4850 3850 4850
Text Label 3750 4750 0    50   ~ 0
VBUS
Wire Wire Line
	3750 4750 3750 4850
Wire Wire Line
	3650 4850 3150 4850
Wire Wire Line
	3650 4350 3150 4350
Wire Wire Line
	3550 3350 3150 3350
NoConn ~ 6050 2650
NoConn ~ 5150 3950
NoConn ~ 5150 3850
$Comp
L Connector_Generic:Conn_02x01 J6
U 1 1 5E501EFD
P 1450 1250
F 0 "J6" H 1500 1450 50  0000 C CNN
F 1 "power in" H 1500 1376 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 1450 1250 50  0001 C CNN
F 3 "~" H 1450 1250 50  0001 C CNN
	1    1450 1250
	-1   0    0    -1  
$EndComp
Text Label 1150 1250 2    50   ~ 0
VBUS
$Comp
L power:GND #PWR04
U 1 1 5E501FE6
P 1650 1250
F 0 "#PWR04" H 1650 1000 50  0001 C CNN
F 1 "GND" H 1655 1077 50  0000 C CNN
F 2 "" H 1650 1250 50  0001 C CNN
F 3 "" H 1650 1250 50  0001 C CNN
	1    1650 1250
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J7
U 1 1 5E50286B
P 4900 6100
F 0 "J7" V 4773 6280 50  0000 L CNN
F 1 "regulator" V 4864 6280 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 4900 6100 50  0001 C CNN
F 3 "~" H 4900 6100 50  0001 C CNN
	1    4900 6100
	0    1    -1   0   
$EndComp
$Comp
L power:GND #PWR0101
U 1 1 5E5029A7
P 4900 6800
F 0 "#PWR0101" H 4900 6550 50  0001 C CNN
F 1 "GND" H 4905 6627 50  0000 C CNN
F 2 "" H 4900 6800 50  0001 C CNN
F 3 "" H 4900 6800 50  0001 C CNN
	1    4900 6800
	1    0    0    -1  
$EndComp
Wire Wire Line
	4900 6300 4900 6600
Text Label 4800 6300 3    50   ~ 0
VBUS
$Comp
L Connector_Generic:Conn_01x03 J8
U 1 1 5E505E02
P 1400 1750
F 0 "J8" H 1500 1750 50  0000 L CNN
F 1 "serial" H 1500 1650 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1400 1750 50  0001 C CNN
F 3 "~" H 1400 1750 50  0001 C CNN
	1    1400 1750
	1    0    0    -1  
$EndComp
Text Label 5150 3150 2    50   ~ 0
RX
Text Label 5150 3050 2    50   ~ 0
TX
Text Label 1200 1650 2    50   ~ 0
TX
Text Label 1200 1750 2    50   ~ 0
RX
$Comp
L power:PWR_FLAG #FLG0101
U 1 1 5E506B71
P 5000 6600
F 0 "#FLG0101" H 5000 6675 50  0001 C CNN
F 1 "PWR_FLAG" V 5000 6728 50  0000 L CNN
F 2 "" H 5000 6600 50  0001 C CNN
F 3 "~" H 5000 6600 50  0001 C CNN
	1    5000 6600
	0    1    1    0   
$EndComp
$Comp
L power:PWR_FLAG #FLG0102
U 1 1 5E507F5D
P 4900 6600
F 0 "#FLG0102" H 4900 6675 50  0001 C CNN
F 1 "PWR_FLAG" V 4900 6728 50  0000 L CNN
F 2 "" H 4900 6600 50  0001 C CNN
F 3 "~" H 4900 6600 50  0001 C CNN
	1    4900 6600
	0    -1   -1   0   
$EndComp
Wire Wire Line
	5000 6300 5000 6600
Text Label 5000 6800 0    50   ~ 0
5V
Connection ~ 5000 6600
Wire Wire Line
	5000 6600 5000 6800
Connection ~ 4900 6600
Wire Wire Line
	4900 6600 4900 6800
Wire Wire Line
	3150 4350 3150 4850
$Comp
L power:GND #PWR0102
U 1 1 5E511A46
P 3150 4950
F 0 "#PWR0102" H 3150 4700 50  0001 C CNN
F 1 "GND" H 3155 4777 50  0000 C CNN
F 2 "" H 3150 4950 50  0001 C CNN
F 3 "" H 3150 4950 50  0001 C CNN
	1    3150 4950
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 4950 3150 4850
Connection ~ 3150 4850
Wire Wire Line
	5150 4350 4550 4350
Wire Wire Line
	5150 4450 4550 4450
Wire Wire Line
	4550 4450 4550 4850
Wire Wire Line
	8550 3750 8550 4150
Wire Wire Line
	8350 4150 8550 4150
Connection ~ 8550 4150
Wire Wire Line
	8550 4150 8550 4950
Wire Wire Line
	6750 3750 7350 3750
Wire Wire Line
	6750 3850 7350 3850
Wire Wire Line
	7350 3850 7350 4150
Wire Wire Line
	4550 3350 5150 3350
Wire Wire Line
	3150 3350 3150 4350
Connection ~ 3150 4350
NoConn ~ 6750 4650
NoConn ~ 6750 4150
Text Label 1200 2200 2    50   ~ 0
SDA
Text Label 1200 2300 2    50   ~ 0
SCL
$Comp
L Connector_Generic:Conn_01x03 J10
U 1 1 5F997216
P 1400 2850
F 0 "J10" H 1479 2892 50  0000 L CNN
F 1 "spi" H 1479 2801 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1400 2850 50  0001 C CNN
F 3 "~" H 1400 2850 50  0001 C CNN
	1    1400 2850
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J9
U 1 1 5F997343
P 1400 2300
F 0 "J9" H 1479 2292 50  0000 L CNN
F 1 "i2c" H 1479 2201 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1400 2300 50  0001 C CNN
F 3 "~" H 1400 2300 50  0001 C CNN
	1    1400 2300
	1    0    0    -1  
$EndComp
Text Label 1200 2750 2    50   ~ 0
MOSI
Text Label 1200 2850 2    50   ~ 0
MISO
Text Label 1200 2950 2    50   ~ 0
CLK
Text Label 6750 4350 0    50   ~ 0
MOSI
Text Label 6750 4250 0    50   ~ 0
MISO
Text Label 6750 4450 0    50   ~ 0
CLK
Text Label 6750 3350 0    50   ~ 0
SDA
Text Label 6750 3450 0    50   ~ 0
SCL
$Comp
L Connector_Generic:Conn_01x03 J11
U 1 1 5F997756
P 1400 3400
F 0 "J11" H 1480 3442 50  0000 L CNN
F 1 "io" H 1480 3351 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1400 3400 50  0001 C CNN
F 3 "~" H 1400 3400 50  0001 C CNN
	1    1400 3400
	1    0    0    -1  
$EndComp
Text Label 1200 3400 2    50   ~ 0
GPIO19
Text Label 5150 3750 2    50   ~ 0
GPIO19
Text Label 5150 4550 2    50   ~ 0
GPIO26
Text Label 1200 3500 2    50   ~ 0
GPIO26
Text Label 6750 4750 0    50   ~ 0
GPIO13
Text Label 1200 3300 2    50   ~ 0
GPIO13
$Comp
L Connector_Generic:Conn_01x03 J12
U 1 1 5F998EF1
P 1400 3950
F 0 "J12" H 1480 3992 50  0000 L CNN
F 1 "power out" H 1480 3901 50  0000 L CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x03_Pitch2.54mm" H 1400 3950 50  0001 C CNN
F 3 "~" H 1400 3950 50  0001 C CNN
	1    1400 3950
	1    0    0    -1  
$EndComp
Text Label 1200 4050 2    50   ~ 0
5V
Text Label 6500 2550 0    50   ~ 0
3.3V
Text Label 1200 3950 2    50   ~ 0
3.3V
$Comp
L power:PWR_FLAG #FLG0103
U 1 1 5F99A5B7
P 6400 2550
F 0 "#FLG0103" H 6400 2625 50  0001 C CNN
F 1 "PWR_FLAG" V 6400 2678 50  0000 L CNN
F 2 "" H 6400 2550 50  0001 C CNN
F 3 "~" H 6400 2550 50  0001 C CNN
	1    6400 2550
	1    0    0    -1  
$EndComp
Text Label 5950 5450 0    50   ~ 0
GND
Text Label 1200 3850 2    50   ~ 0
GND
Wire Wire Line
	6500 2550 6400 2550
Text Label 1200 1850 2    50   ~ 0
GND
Text Label 1200 2400 2    50   ~ 0
GND
Wire Wire Line
	6400 2550 6150 2550
Wire Wire Line
	6150 2550 6150 2650
Connection ~ 6400 2550
$EndSCHEMATC
