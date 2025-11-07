
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


## **3.  SD Card Hot Swap**

Flush (force system) all cached data from RAM:
```bash
sync
```
unmount:
```bash
umount /mnt/sdcard
```
If it works, unmounting is done. 

* If  `"Device is busy"`

	Wait every process then unmount:
```bash
umount -l /mnt/sdcard
```
	*This will Immediately detach the filesystem from the directory tree (so no new process can access `/mnt/sdcard`); keep the filesystem "alive" in the background until the last busy process finishes what it's doing and closes its files then the kernel will _actually_ and _safely_ unmount the device*


	* If the lazy unmount doesn't work (have a stuck process):
	```bash title="print busy PIDs"
	fuser -m /mnt/sdcard
	```
	```bash title="polite kill"
	kill 1234 5678
	```
	```bash title="print busy PIDs again"
	fuser -m /mnt/sdcard
	```
	```bash title="force kill (same as fuser -k)"
	kill -9 1234 5678
	```
	```bash title="now it will unmount"
	umount /mnt/sdcard
	```
	!!! danger "umount -f /dev/mmcblk1p1"
    	llms can suggest this command, which is one of the easiest way to corrupt an sd card. It is a near-guaranteed way to cause data corruption.

* Mount the new sd card:
```bash
mount /dev/mmcblk1p1 /mnt/sdcard
```

* Further debugging:
```bash
fuser -vam /mnt/sdcard
```
*-v verbose, -a all filesystems, -m by mountpoint*

    
    ```bash title="if there is a service which does not let it go"
    systemctl stop sshd.service || true
    ```
        *but mostly `reboot`ing would be way faster then further debugging.*


## **4.  Date Time Fix**

If the device thinks it is in China:
```bash title="check before proceeding"
date; date +%Z%z
```
```bash title="desired timezone"
ln -sf /usr/share/zoneinfo/Etc/GMT-3 /etc/localtime
```
```bash title="set this as default timezone"
echo "Etc/GMT-3" > /etc/timezone 
```
```bash title="confirm it's set"
date; date +%Z%z
```


## **5.  Force kill apps**

If there were a local network problem which killed ssh terminal therefore the process inside the ssh terminal still runs but can't be observed/closed:

```bash title="print programs which uses port *900*"
netstat -tulnp | grep 900
```
**`-t`**: Show TCP connections.    
**`-u`**: Show UDP connections.    
**`-l`**: Show only listening sockets (servers waiting for a connection), not all active connections.   
**`-n`**: Show numeric addresses and port numbers. This is much faster and clearer, as it prevents `netstat` from trying to look up names (it shows `8.8.8.8` instead of `google.com`).    
**`-p`**: Show the pid and name of the program owning the socket. 

```bash title="be nice at first"
kill -9 23274
```
```bash title="wait a few seconds and check if they shut down"
netstat -tulnp | grep 900
```
```bash title="kill"
kill -9 23274
```


## **Additional Notes**

  * **Default ssh password:**  `oelinux***`.
  * **Documentation:** For other issues, refer to the official device documentation `Quectel_SC206E_Series_Linux_User_Guide_V1.1.pdf`.

-----
-----