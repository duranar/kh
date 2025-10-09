
# SoC (SC206E) Setup & Troubleshooting & Development Notes

For SC206E-EM 
*LTE version (In Quectel's documentation, they refer wifi-only (non-LTE) models as WF, that does not mean devices with wifi. LTE models have both functionality.)*

---

## 1. Fixing SSH Connectivity Issues

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

then reboot.


### Additional Notes

  * **Default ssh password:**  `oelinux***`.
  * **Documentation:** For other issues, refer to the official device documentation `Quectel_SC206E_Series_Linux_User_Guide_V1.1.pdf`.

-----
* Quick one-liner:
```bash
SSID="E"; PSK="E15243!"; (wpa_supplicant -B -D nl80211 -i wlan0 -c /data/misc/wifi/wpa_supplicant.conf) && sleep 2 && ID=$(wpa_cli -i wlan0 add_network | tail -1) && wpa_cli -i wlan0 set_network $ID ssid "\"$SSID\"" && wpa_cli -i wlan0 set_network $ID psk "\"$PSK\"" && wpa_cli -i wlan0 enable_network $ID && wpa_cli -i wlan0 save_config && echo "Successfully configured and saved network ID $ID."
```

-----


* To enable wifi:
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


## 2\. GStreamer Video Commands

These commands use GStreamer for video capture and streaming.

### Video Capture (Saving to File)

  * **H.264 Capture from MIPI Camera:**

    ```bash
    gst-launch-1.0 -e qtiqmmfsrc camera=0 name=camsrc ! 'video/x-raw,format=NV12,width=640,height=480,framerate=30/1' ! qtic2venc ! h264parse ! mp4mux ! queue ! filesink location=/mnt/sdcard/test1.mp4
    ```

  * **H.265 (HEVC) Capture from MIPI Camera:**

    ```bash
    gst-launch-1.0 -e qtiqmmfsrc camera=0 name=camsrc ! 'video/x-raw,format=NV12,width=640,height=480,framerate=30/1' ! videoconvert ! qtic2venc ! 'video/x-h265' ! h265parse ! mp4mux ! queue ! filesink location=/mnt/sdcard/test-h265-00.mp4
    ```

  * **H.265 (HEVC) Capture from USB Camera (V4L2):**

    ```bash
    gst-launch-1.0 -e v4l2src device=/dev/video2 ! 'video/x-raw,width=1280,height=720' ! videoconvert ! qtic2venc ! 'video/x-h265' ! h265parse ! mp4mux ! filesink location=/mnt/sdcard/usb-camera-test-03.mp4
    ```

### Video Preview (Streaming to Display)

*Note: These commands require a Wayland display server to be running.*

  * **Stream from MIPI Camera to Screen:**

    ```bash
    WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/root gst-launch-1.0 -e qtiqmmfsrc camera=0 name=camsrc ! 'video/x-raw,format=NV12,width=1280,height=720,framerate=30/1' ! videoconvert ! waylandsink
    ```

  * **Stream from USB Camera to Screen:**

    ```bash
    WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/root gst-launch-1.0 -e v4l2src device=/dev/video2 ! 'video/x-raw,width=1280,height=720' ! videoconvert ! waylandsink
    ```

### Retrieving Saved Files

1.  **Using ADB (Android Debug Bridge):** If the device is connected via a debug port and ADB is active:

	*Note: ADB works on this SoC even though it is not running Android.*

    ```bash
    adb pull /mnt/sdcard/usb-camera-test-02.mp4 C:\local\folder
    ```

2.  **Using SCP (Secure Copy Protocol):** If SSH is working, SCP will also work. You can use PowerShell or a graphical client to transfer files.

      * **Recommendation:** **WinSCP** is a reliable and popular choice for Windows. Avoid FileZilla!


  * **Documentation:** For other issues, refer to `Quectel_SC206E_Series_Linux_Multimedia_Application_Note_V1.0.pdf`.

-----

## 3\. USB Camera (UVC) Troubleshooting

This section covers how to diagnose and use standard USB Video Class (UVC) cameras.

### Initial Diagnostics

  * **Check if the USB device is recognized:**

	   Run before and after plugging in the camera to see the difference
    ```bash
    lsusb
    ```

  * **Check if the UVC driver module is loaded:**

    ```bash
    lsmod | grep uvcvideo
    ```

      * **Important:** If this command returns nothing, it does **not** mean the driver is absent. Drivers can be built directly into the kernel instead of being loadable modules (`.ko` files). Built-in drivers are always active from boot and will not appear in `lsmod`. The most reliable way to confirm the driver is working is to check the kernel logs (`dmesg`).

### Understanding Kernel Logs (`dmesg`)

When you plug in a USB camera, check `dmesg` for messages like these:

```log
# Confirms the USB port is active in host mode
xhci-hcd xhci-hcd.2.auto: new USB bus registered, assigned bus number 2

# The system has read the device's descriptors
usb 1-1: Product: UNIQUESKY_CAR_CAMERA

# MOST IMPORTANT LINE: The uvcvideo driver has successfully recognized and attached to the camera.
uvcvideo: Found UVC 1.00 device UNIQUESKY_CAR_CAMERA (abcd:ab51)
```

### Understanding Camera Sources

There is no direct relationship between `/dev/videoX` device nodes and `camera=X` indices. They are used by different GStreamer elements.

  * qtiqmmfsrc camera=X`: A Qualcomm-specific element for accessing the SoC's built-in camera hardware interface (e.g., MIPI CSI-2 ports). This is used for ribbon-cable cameras, not USB cameras.
  * `v4l2src device=/dev/videoX`: The standard Linux element for capturing from Video4Linux2 devices. This is used for USB cameras, which are handled by the `uvcvideo` driver that creates `/dev/videoX` nodes.

### Using `v4l2-ctl` to Inspect Cameras

The `v4l2-ctl` utility is essential for inspecting camera properties. If the command is not found, the `v4l-utils` the kernel needs to be recompiled to include it.

  * **Why are there two `/dev/video*` devices for one camera?**
    Modern UVC cameras often expose multiple interfaces. Typically:

    1.  **Video Capture Node:** (`/dev/video2`) The primary interface that provides the actual video stream.
    2.  **Metadata Node:** (`/dev/video3`) A secondary interface for camera controls, sensor data, etc.

  * **Get all information about a device node:**
    The output clearly shows which node is for `Video Capture` and which is for `Metadata Capture`.

    ```bash
    v4l2-ctl --device /dev/video2 --all
    ```

    ```text
    Driver Info:
            Driver name     : uvcvideo
            Card type       : UNIQUESKY_CAR_CAMERA
            Bus info        : usb-xhci-hcd.2.auto-1
            Driver version  : 5.4.191
            Capabilities    : 0x84200001
                    Video Capture
                    Streaming
                    Extended Pix Format
                    Device Capabilities
    ```

  * **List supported formats, resolutions, and frame rates:**
    This command is crucial for building a correct GStreamer pipeline, as it tells you exactly what the camera can output.

    ```bash
    v4l2-ctl --device /dev/video2 --list-formats-ext
    ```

    ```text
    ioctl: VIDIOC_ENUM_FMT
            Index       : 0
            Type        : Video Capture
            Pixel Format: 'YUYV' (YUYV 4:2:2)
            Name        : YUYV 4:2:2
                    Size: Discrete 640x480
                            Interval: Discrete 0.033s (30.000 fps)
                    Size: Discrete 1280x720
                            Interval: Discrete 0.100s (10.000 fps)

            Index       : 1
            Type        : Video Capture
            Pixel Format: 'MJPG' (Motion-JPEG)
            Name        : Motion-JPEG
                    Size: Discrete 1920x1080
                            Interval: Discrete 0.033s (30.000 fps)
                    Size: Discrete 1280x720
                            Interval: Discrete 0.033s (30.000 fps)
    ```

