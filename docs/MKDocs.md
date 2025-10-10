
## **Admonitions**


!!! note "note-Kernel Version"  
	This documentation is applicable for Linux kernel version 5.4 and later.

!!! abstract "abstract-Summary of this Document"  
	This page outlines the process for inspecting V4L2 devices, identifying their capabilities, and constructing a basic GStreamer pipeline for video streaming.

!!! info "info-Further Reading"  
	For more details on GStreamer, refer to the official documentation.

!!! tip "tip-Performance Tip"  
	Using v4l2-ctl to check formats first can save significant time compared to trial-and-error with GStreamer.

!!! success "success-Compilation Complete"  
	The kernel module was successfully compiled and loaded. You can now proceed to the next step.

!!! question "question-What if v4l2-ctl is not found?"  
	If the command is missing, you need to install the v4l-utils package using your distribution's package manager, e.g., sudo apt-get install v4l-utils.

!!! warning "warning-High CPU Usage"  
	Software-based video encoding is CPU-intensive. Monitor system load when running this pipeline on embedded devices.

!!! failure "failure-Pipeline Failed"  
	The GStreamer pipeline failed to start. This often means there is a mismatch in the video format or resolution specified.

!!! danger "danger-danger-Do Not Interrupt"  
	Flashing the firmware is a critical process. Do not disconnect power or interrupt the device until it is complete, as this could permanently brick the device.

!!! bug "bug-Known Issue with USB 3.0"  
	There is a known bug where some USB 3.0 controllers may cause frame drops. If you experience this, try connecting the camera to a USB 2.0 port.

!!! example "example-Example GStreamer Pipeline"  
	```bash
	gst-launch-1.0 v4l2src device=/dev/video0 ! 'video/x-raw,width=1920,height=1080' ! videoconvert ! autovideosink
	```

!!! quote "quote-From the V4L2 Documentation" 
	The Video4Linux2 (V4L2) API is a kernel interface for analog and digital video capture and output devices. It is the designated standard for a wide range of devices on Linux.

>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor massa, nec semper lorem quam in massa.