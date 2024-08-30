# Automatyczny konfigurator Gamepada Hama uRage Vendetta dla systemu Linux 
Skrypt pythonowy do automatycznej detekcji, inicjalizacji, mapowania i kalibracji gamepada (Gamepad Hama uRage Vendetta) dla systemu Linux, przy użyciu modułów pyusb, pyudev i narzędzia jscal z pakietu joystick.

## Cechy
- **Automatyczne wykrywanie**: Skrypt wykorzystuje `pyudev` do monitorowania zdarzeń USB, wykrywając kiedy gamepad jest podłączony lub odłączony.
- **Inicjalizacja**: Wysyła `kod inicjujący` w celu aktywowania gamepada.
- **Kalibracja**: Automatycznie kalibruje gamepada za pomocą narzędzia `jscal`.
- **Logging**: Rejestrowanie zdarzeń związanych z podłączaniem, inicjalizacją, kalibracją i odłączaniem gamepada. 

## Wymagania Pythona
- Biblioteka `pathlib`
- Biblioteka `pyudev`
- Biblioteka `pyusb`

## Wymagania systemowe
- Python 3.9 lub nowszy
- `joystick` (dla `jscal`)

## Dodawanie reguł Udev dla dostępu bez uprawnień roota:
Aby umożliwić użytkownikowi inicjalizację i kalibrację gamepada bez uprawnień roota, należy skonfigurować reguły udev, które dostosowują uprawnienia do USB i urządzeń wejściowych gamepada.


### Krok 1: Identyfikacja gamepada
Użyj `lsusb` by zidentyfikować `idVendor` i `idProduct` twojego gamepada:

```bash
lsusb
# Bus 003 Device 002: ID 045e:028e Microsoft Corp. Xbox360 Controller
```

IdVendor to `045e`, a idProduct to `028e`.

### Krok 2: Tworzenie reguł udev
- Utwórz nowy plik reguł udev:

```bash
sudo nano /etc/udev/rules.d/99-gamepad.rules
```
- Dodaj następującą zawartość, aby ustawić uprawnienia dla urządzeń INPUT/USB:
```bash
SUBSYSTEM=="input", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="028e", OWNER="myuser", MODE="0600"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="028e", OWNER="myuser", MODE="0660"
```
Ta konfiguracja zapewnia, że zarówno urządzenie wejściowe (np. `/dev/input/js0`), jak i samo urządzenie USB są dostępne dla wybranego użytkownika `myuser`.

### Krok 3: Przeładowanie reguł Udev
Po zapisaniu reguł, przeładuj reguły udev i uruchom je:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Krok 4: Weryfikacja uprawnień
Uruchom skrypt i spróbuj ponownie podłączyć gamepada i sprawdź uprawnienia w odpowiednich węzłach urządzenia:

```bash
ls -l /dev/input/js0
```
Powinieneś zobaczyć coś takiego:
```bash
crw-rw---- 1 myuser input 13, 0 Aug 23 15:00 /dev/input/js0
```

# Automatic configurator of the Hama uRage Vendetta Gamepad for Linux. 
Python script for automatic detection, initialization, mapping and calibration of gamepad (Gamepad Hama uRage Vendetta) for Linux, using pyusb, pyudev modules and jscal tool from joystick package.

## Features
- **Automatic detection**: The script uses `pyudev` to monitor USB events, detecting when a gamepad is connected or disconnected.
- **Initialization**: Sends an `initialization code` to activate the gamepad.
- **Calibration**: Automatically calibrates the gamepad using the `jscal` tool.
- **Logging**: Logs events related to connecting, initializing, calibrating and disconnecting the gamepad. 

## Python requirements
- `pathlib` library
- `pyudev` library
- `pyusb` library

## Systen requirements
- Python 3.9 or later
- `joystick` (for `jscal`)


## Adding Udev Rules for Non-Root Access:
To allow user to initialize and calibrate the gamepad without root permissions, you need to set up udev rules that adjust the permissions on the gamepad's USB and input devices.


### Step 1: Identify Your Gamepad
Use `lsusb` to identify your gamepad's `idVendor` and `idProduct`:

```bash
lsusb
# Bus 003 Device 002: ID 045e:028e Microsoft Corp. Xbox360 Controller
```

The idVendor is `045e` and idProduct is `028e`.

### Step 2: Create Udev Rules
- Create a new udev rules file:

```bash
sudo nano /etc/udev/rules.d/99-gamepad.rules
```
- Add the following content to set permissions for INPUT/USB devices:
```bash
SUBSYSTEM=="input", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="028e", OWNER="myuser", MODE="0600"
SUBSYSTEM=="usb", ATTRS{idVendor}=="045e", ATTRS{idProduct}=="028e", OWNER="myuser", MODE="0660"
```

This configuration ensures that both the input device (e.g. `/dev/input/js0`) and the USB device itself are available to the selected `myuser` user.

### Step 3: Reload Udev Rules

After saving the rules, reload the udev rules and trigger them:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Step 4: Verify Permissions

Run script and try reconnect your gamepad and check the permissions on the relevant device nodes:

```bash

ls -l /dev/input/js0
```
You should see something like:
```bash
crw-rw---- 1 myuser input 13, 0 Aug 23 15:00 /dev/input/js0
```
This indicates that `myuser` has the necessary permissions to access and calibrate the gamepad.
