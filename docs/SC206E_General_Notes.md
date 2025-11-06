
# SoC (SC206E) Setup & Troubleshooting & Development Notes

**For SC206E-EM**  *LTE version*
!!! info ""
	Quectel refer to wifi-only (non-LTE) models as WF, that does not mean devices with wifi. LTE models have both functionality; WF models have only wifi.

---

## **1. Fixing SSH Connectivity Issues**

The SSH daemon (`sshd`) is certainly installed but may not be active. The typical problem is that it's set to listen only for local connections (`127.0.0.1`), or the service does not listen ssh port (`22`).

### Step 1: Check/Remount the Root Filesystem

**Potential Problem:** You cannot save changes to configuration files which we are about to perform because the filesystem is "read-only."

**Solution:** Many embedded systems mount the root filesystem as read-only for stability. You must remount it in read-write mode before you can edit any system files.

Remount the root partition ('/') with read-write permissions
```bash
mount -o remount,rw /
```

### Step 2: Configure the SSH Daemon (`sshd_config`)

**Problem:** SSH is running but refuses connections from the network.

**Solution:** Modify the SSH daemon's main configuration file to listen on all network interfaces.

Open the configuration file with a text editor
```bash
vi /lib/systemd/system/sshd.socket
```

Inside the file, find the `ListenAddress` line:

```bash
ListenStream 127.0.0.1:22
```
**Change the address explicitly:** 

```bash
ListenStream 22
```

then **reboot**. 
*This configuration made default in v0.02, 9 Oct 2025.*
 

## **Additional Notes**

  * **Default ssh password:**  `oelinux***`.
  * **Documentation:** For other issues, refer to the official device documentation `Quectel_SC206E_Series_Linux_User_Guide_V1.1.pdf`.

-----

## **2.  Enabling wifi:**

* in ssh terminal:
```bash
wpa_supplicant -D nl80211 -i wlan0 -c /data/misc/wifi/wpa_supplicant.conf &
```
```bash
wpa_cli -i wlan0 scan
```
```bash
wpa_cli -i wlan0 scan_result
```
```bash
wpa_cli -i wlan0 add_network
```

* which will return a number, ***`<network id>`***, probably "0".
* Guide will refer this ***`<network id>`*** as **0**.
```bash
wpa_cli -i wlan0 set_network 0 ssid '"ssid"'
```
```bash
wpa_cli -i wlan0 set_network 0 psk '"psk"'
```

* Connect to the network:
```bash
wpa_cli -i wlan0 enable_network 0
```
* Save config:
```bash
wpa_cli -i wlan0 save_config
```
* Display Wi-Fi connection list of the current known network IDs and statuses:
```bash
wpa_cli -i wlan0 list_network
```


