## 1. How to Inspect Connected Cameras


### How to find connected cameras

```bash
ls /dev/video*
```
Which will return something like this:
```text
/dev/video0   /dev/video1   /dev/video2   /dev/video3   /dev/video32  /dev/video33  /dev/video4   /dev/video5
```
For SC206E, single-digit suffixes means camera devices. Double-digit suffixes means video encoder/decoder blocks inside the SoC.


### How to inspect camera devices

The `v4l2-ctl` utility is essential for inspecting camera properties. If the command is not found, the `v4l-utils` the kernel needs to be recompiled to include it (which added and compiled 10/10/2025).

  * **Why are there two `/dev/video*` devices for one camera?**
    Modern UVC cameras often expose multiple interfaces. Typically:
    1.  **Video Capture Node:** (`/dev/video0`) The primary interface that provides the actual video stream.
    2.  **Metadata Node:** (`/dev/video1`) A secondary interface for camera controls, sensor data, etc.

  * **List supported formats, resolutions, and frame rates:**
    This command is crucial for building a correct GStreamer pipeline, as it tells you exactly what the camera can output.

    ```bash
    v4l2-ctl --device /dev/video0 --list-formats-ext
    ```

    ```text hl_lines="3 4 5 6 7 8 9 25 28 29" title="output" 
	ioctl: VIDIOC_ENUM_FMT
			Type: Video Capture
			[0]: 'MJPG' (Motion-JPEG, compressed)
					Size: Discrete 1920x1080
							Interval: Discrete 0.033s (30.000 fps)
							Interval: Discrete 0.040s (25.000 fps)
							Interval: Discrete 0.050s (20.000 fps)
							Interval: Discrete 0.067s (15.000 fps)
							Interval: Discrete 0.100s (10.000 fps)
					Size: Discrete 1280x720
							Interval: Discrete 0.033s (30.000 fps)
							Interval: Discrete 0.040s (25.000 fps)
							Interval: Discrete 0.050s (20.000 fps)
							Interval: Discrete 0.067s (15.000 fps)
							Interval: Discrete 0.100s (10.000 fps)
					Size: Discrete 1024x576
							Interval: Discrete 0.033s (30.000 fps)
							Interval: Discrete 0.050s (20.000 fps)
							Interval: Discrete 0.067s (15.000 fps)
							Interval: Discrete 0.100s (10.000 fps)
							Interval: Discrete 0.200s (5.000 fps)
					...
					...
					...
			[1]: 'YUYV' (YUYV 4:2:2)
					Size: Discrete 1280x720
							Interval: Discrete 0.100s (10.000 fps)
					Size: Discrete 1920x1080
							Interval: Discrete 0.200s (5.000 fps)
					Size: Discrete 1024x576
							Interval: Discrete 0.100s (10.000 fps)
							Interval: Discrete 0.200s (5.000 fps)
					...
					...
					...
    ```


  * **Get all information about a device node:**
    The output clearly shows which node is for `Video Capture` and which is for `Metadata Capture`.

    ```bash
    v4l2-ctl --device /dev/video0 --all
    ```

    ```text title="output" 
	Driver Info:
	        Driver name      : uvcvideo
	        Card type        : Arducam USB Camera: Arducam USB
	        Bus info         : usb-xhci-hcd.2.auto-1
	        Driver version   : 5.4.191
	        Capabilities     : 0x84a00001
	                Video Capture
	                Metadata Capture
	                Streaming
	                Extended Pix Format
	                Device Capabilities
	        Device Caps      : 0x04200001
	                Video Capture
	                Streaming
	                Extended Pix Format
	Media Driver Info:
	        Driver name      : uvcvideo
	        Model            : Arducam USB Camera: Arducam USB
	        Serial           : UC684
	        Bus info         : usb-xhci-hcd.2.auto-1
	        Media version    : 5.4.191
	        Hardware revision: 0x00000100 (256)
	        Driver version   : 5.4.191
	Interface Info:
	        ID               : 0x03000002
	        Type             : V4L Video
	Entity Info:
	        ID               : 0x00000001 (1)
	        Name             : Arducam USB Camera: Arducam USB
	        Function         : V4L2 I/O
	        Flags         : default
	        Pad 0x0100000d   : 0: Sink
	          Link 0x0200001a: from remote pad 0x1000010 of entity 'Extension 4': Data, Enabled, Immutable
	Priority: 2
	Video input : 0 (Camera 1: ok)
	Format Video Capture:
	        Width/Height      : 1280/720
	        Pixel Format      : 'YUYV' (YUYV 4:2:2)
	        Field             : None
	        Bytes per Line    : 2560
	        Size Image        : 1843200
	        Colorspace        : sRGB
	        Transfer Function : Default (maps to sRGB)
	        YCbCr/HSV Encoding: Default (maps to ITU-R 601)
	        Quantization      : Default (maps to Limited Range)
	        Flags             :
	Crop Capability Video Capture:
	        Bounds      : Left 0, Top 0, Width 1280, Height 720
	        Default     : Left 0, Top 0, Width 1280, Height 720
	        Pixel Aspect: 1/1
	Selection Video Capture: crop_default, Left 0, Top 0, Width 1280, Height 720, Flags:
	Selection Video Capture: crop_bounds, Left 0, Top 0, Width 1280, Height 720, Flags:
	Streaming Parameters Video Capture:
	        Capabilities     : timeperframe
	        Frames per second: 10.000 (10/1)
	        Read buffers     : 0
	                     brightness 0x00980900 (int)    : min=-64 max=64 step=1 default=0 value=0
	                       contrast 0x00980901 (int)    : min=0 max=64 step=1 default=32 value=32
	                     saturation 0x00980902 (int)    : min=0 max=128 step=1 default=64 value=64
	                            hue 0x00980903 (int)    : min=-40 max=40 step=1 default=0 value=0
	 white_balance_temperature_auto 0x0098090c (bool)   : default=1 value=1
	                          gamma 0x00980910 (int)    : min=72 max=500 step=1 default=100 value=100
	                           gain 0x00980913 (int)    : min=0 max=100 step=1 default=0 value=0
	           power_line_frequency 0x00980918 (menu)   : min=0 max=2 default=1 value=1
	                                0: Disabled
	                                1: 50 Hz
	                                2: 60 Hz
	      white_balance_temperature 0x0098091a (int)    : min=2800 max=6500 step=1 default=4600 value=4600 flags=inactive
	                      sharpness 0x0098091b (int)    : min=0 max=6 step=1 default=2 value=2
	         backlight_compensation 0x0098091c (int)    : min=0 max=2 step=1 default=1 value=1
	                  exposure_auto 0x009a0901 (menu)   : min=0 max=3 default=3 value=3
	                                1: Manual Mode
	                                3: Aperture Priority Mode
	              exposure_absolute 0x009a0902 (int)    : min=1 max=5000 step=1 default=156 value=156 flags=inactive
	         exposure_auto_priority 0x009a0903 (bool)   : default=0 value=1
    ```


-----
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

  * **Motion JPEG Capture from USB Camera (V4L2):**

    ```bash
    gst-launch-1.0 -e v4l2src device=/dev/video0 ! 'image/jpeg,width=1920,height=1080,framerate=30/1' ! filesink location=/mnt/sdcard/raw_mjpeg_stream.mjpg
    ```

  * **Motion JPEG Capture from USB Camera (V4L2) and Re-encode:**

    ```bash
    gst-launch-1.0 -e v4l2src device=/dev/video0 ! 'image/jpeg,width=1280,height=720,framerate=15/1' ! avdec_mjpeg ! videoconvert ! qtic2venc ! 'video/x-h264' ! h264parse ! mp4mux ! queue ! filesink location=/mnt/sdcard/mjpeg_720p_15fps_to_h264.mp4
    ```

  * **H.265 (HEVC) Capture from USB Camera (V4L2):**

    ```bash
    gst-launch-1.0 -e v4l2src device=/dev/video0 ! 'video/x-raw,width=1920,height=1080' ! videoconvert ! qtic2venc ! 'video/x-h265' ! h265parse ! mp4mux ! filesink location=/mnt/sdcard/usb-camera-test-03.mp4
    ```
	!!! note ""
		Note that this command does not specify format or framerate, since they can cause problems for auto negotiator
	!!! info ""
		If it's specified as `'video/x-raw,format=YUYV,width=1920,height=1080,framerate=30/1'`, which tells to `v4l2src` "You **must** provide a stream with **exactly** these properties". But for some reason this can cause `videoconvert`  to reject this very specific contract, leading to the `not-negotiated` error.
	!!! tip ""
		This `'video/x-raw,width=1920,height=1080'` command practically asks "Give me any raw format you have at 1080p"; then `v4l2src` checks with the camera driver, the driver responds "At 1080p, the only raw format I offer is `YUYV` at **5 fps**.", `v4l2src` then configures itself for that mode and offers the resulting stream to `videoconvert`.


  * **H.265 (HEVC) Capture from USB Camera (H.264 passthrough):**

	!!! warning "" 
		This command will only work if the camera device supports H.264 passthrough as video capture format. ([refer to this](#how-to-inspect-camera-devices)).


	
	```bash
	gst-launch-1.0 -e v4l2src device=/dev/video4 ! 'video/x-h264,width=1920,height=1080,framerate=30/1' ! h264parse ! mp4mux ! filesink location=/path/to/video.mp4
	```


### Video Preview (Streaming to Display)

!!! warning ""
	*Note: These commands require a Wayland display server to be running on the device.*

  * **Stream from MIPI Camera to Screen:**

    ```bash
    WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/root gst-launch-1.0 -e qtiqmmfsrc camera=0 name=camsrc ! 'video/x-raw,format=NV12,width=1280,height=720,framerate=30/1' ! videoconvert ! waylandsink
    ```

  * **Stream from USB Camera to Screen:**

    ```bash
    WAYLAND_DISPLAY=wayland-0 XDG_RUNTIME_DIR=/run/user/root gst-launch-1.0 -e v4l2src device=/dev/video2 ! 'video/x-raw,width=1280,height=720' ! videoconvert ! waylandsink
    ```


### MJPEG Video Commands

!!! warning ""
	*Note: ffmpeg commands might not work on the SoC. Needs to be tested.*

```bash title="check video properties"
ffprobe video-name.mjpg
```

```bash title="play mjpg video file"
ffplay -f mjpeg video-name.mjpg
```

```bash title="play mjpg video file with fixed framerate"
ffplay -f mjpeg -framerate 30 video-name.mjpg
```

```bash title="re-encode mjpeg video file (h264)"
gst-launch-1.0 -e filesrc location=/mnt/sdcard/MJPEG_VIDEO_FILE_NAME.mjpg ! jpegdec ! videorate ! "video/x-raw,framerate=30/1" !  videoconvert ! qtic2venc ! h264parse ! mp4mux ! filesink location=/mnt/sdcard/H264_ENCODED_VIDEO_FILE_NAME.mp4
```


### Retrieving Saved Files

1.  **Using ADB (Android Debug Bridge):** If the device is connected via a debug port and ADB is active:

	!!! success ""
		ADB works on this SoC even though it is not running Android.
	
	```bash
	adb pull /mnt/sdcard/usb-camera-test-02.mp4 C:\local\folder
	```

2.  **Using SCP (Secure Copy Protocol):** If SSH is working, SCP will also work. You can use PowerShell or a graphical client to transfer files.

	!!! success "**Recommendation: WinSCP** "
		* **WinSCP** is a reliable choice for Windows with many features. 
		!!! failure ""
			  Avoid FileZilla!


  * **Documentation:** For other issues, refer to `Quectel_SC206E_Series_Linux_Multimedia_Application_Note_V1.0.pdf`.


-----
## 3\. GStreamer 

### Gstreamer Concepts
Using an assembly line analogy helps to understand the core concepts:

-Elements: These are the fundamental processing blocks in a pipeline. Each element performs a single, specialized function. Common types include:

  * Source: Produces data (e.g., `v4l2src` reads from a camera).
  * Sink: Consumes data (e.g., `filesink` writes to a file, `waylandsink` displays on a screen).
  * Filter/Converter: Modifies data as it passes through (e.g., `videoconvert` changes color formats, `qtic2venc` encodes raw video into H.265).
  * Parser: Understands the structure of compressed data (e.g., `h264parse`).
  * Muxer: Combines different streams (like video and audio) into a container format (e.g., `mp4mux`).

-Pads: These are the connection points on an element. A sink pad is an input, and a source pad (often written "src") is an output. You can only connect a source pad to a sink pad.

-Capabilities (Caps): This is the "contract" for the data that flows between pads. It's a detailed description of the media type, like `'video/x-raw,format=YUYV,width=640,height=480'`. A "not-negotiated" error occurs when two connected elements cannot agree on a common set of capabilities.

!!! info "syntax"
	
	 * Linking Element  `!`
	
		The exclamation mark (`!`) is used to link the `source` pad of the element on its left to the `sink` pad of the element on its right. It acts as the "pipe" that connects the "workers" on the assembly line. A chain of elements linked by ! forms a pipeline.
	
	 * Caps Filtering / Forcing a format `' ... '`
		 To ensure a specific format is used, you can add a "caps filter" directly into the pipeline. This acts as a requirement for the data flowing through that point.
		 `element ! 'media/type,property=value' ! next_element`


### gst-inspect-1.0 Instruction Manual

This utility serves as a dictionary for GStreamer, allowing the discovery of available elements and their specific functionalities.

```bash title="List all installed elements"
gst-inspect-1.0
```

```bash title="Find elements related to qti"
gst-inspect-1.0 | grep qti
```

```bash title="Find elements related to video"
gst-inspect-1.0 | grep video
```

```bash title="Get the full details for one element"
gst-inspect-1.0 <element-name>
```


### Pipeline's Elements

Configurable options for an element are known as **Element Properties**.

**`v4l2src` (Camera Source)**

This element reads from any Video4Linux2 device, which includes USB camera.
```bash 
gst-inspect-1.0 v4l2src
```

Key Element Properties include:

 * `device`: The device file to use, like `/dev/video0`.
 * `num-buffers`: How many buffers to keep in memory. Increasing this can sometimes help with performance issues but adds latency.
 * `io-mode`: How memory is handled. The default is often fine, but for advanced use, you can control whether the system copies memory or tries to share it directly (DMA).

**videoconvert and autovideoconvert (Software Converters)**

These elements perform raw video format conversions using the CPU.
```bash
gst-inspect-1.0 videoconvert
```

 * Pad Templates*: The most important section is `SINK template` -> `Capabilities`. This lists all raw video formats that `videoconvert` can accept as input.
 * Element Properties: It has properties like `dither` and `alpha-mode` for controlling the quality of the conversion.

`autovideoconvert` has fewer properties of its own because its job is to automatically insert and configure other elements (like `videoconvert`) for you.

**qtic2venc (Qualcomm Hardware H.265 Encoder)**

This is a critical element for hardware-accelerated video encoding on Qualcomm SoCs.

```bash
gst-inspect-1.0 qtic2venc
```

The "Element Properties" provide control over the video encoding process:

 * `bitrate`: Sets the target bitrate for the video in bits per second (e.g., `bitrate=4000000` for 4 Mbps). Higher bitrate means better quality and larger file size.
 * `control-rate`: Sets the bitrate control method. You can choose `variable` (VBR), `constant` (CBR), etc.
 * `i-frame-period` (or similar name like `gop-size`): Determines the frequency of keyframes (I-frames). A smaller number (e.g., 30 for a 30fps stream creates one keyframe per second) improves seeking and is better for streaming, but may increase data usage slightly.

Properties are set in a pipeline using the syntax: `element-name property=value`.

**Debug Tool: `GST_DEBUG`**
The `GST_DEBUG` environment variable enables detailed logging from GStreamer elements.

The format is `GST_DEBUG="element_name:LEVEL,another_element:LEVEL,*:LEVEL"`. The level is a number from 1 (errors only) to 9 (most verbose).

- **Level 3 (INFO):** Useful for observing the basic data flow.
- **Level 5 (DEBUG):** Provides detailed information on internal logic.
- **`*`** A wildcard that applies to all other elements.

**Example:** 

```bash title="debug the hardware encoder and the camera source"
# Set debug level 5 for the encoder, level 3 for the source, and 2 (warnings) for everything else. 
export GST_DEBUG="qtic2venc:5,v4l2src:3,*:2" 
# Execute the pipeline command to see verbose logging output. 
gst-launch-1.0 -e v4l2src device=/dev/video0 ! ...
```


-----
## 4\. USB Camera (UVC) Troubleshooting

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

When you plug in a USB camera, check kernel logs for messages like these:

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

  * `qtiqmmfsrc camera=X`: A Qualcomm-specific element for accessing the SoC's built-in camera hardware interface (e.g., MIPI CSI-2 ports). This is used for ribbon-cable cameras, not USB cameras.
  * `v4l2src device=/dev/videoX`: The standard Linux element for capturing from Video4Linux2 devices. This is used for USB cameras, which are handled by the `uvcvideo` driver that creates `/dev/videoX` nodes.

