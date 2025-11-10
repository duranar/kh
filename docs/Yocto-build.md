# **Yocto Development & Build Notes**

### **Initial development setup notes**
 * **How to get BSP & Source Codes**    
    Do not attempt to get BSP from Quectel gitlab server directly. They do not have CDNs around the globe; their **only** gitlab server is located in the mainland China. So fetching the full repo from their server will last **~2 weeks**; assuming in that time period you won't get power cuts and your network connection will be **perfectly** stable. Otherwise you'll start over. Git continuous fetch will not work (using that method will cause your account get **banned** from their server for 2 hours).     
    **Instead**    
    * Get a remote (cloud) machine from tencent cloud with *at least* 100GB storage option (inside or closest one to mainland china),    
    * Fetch the repo in that machine (be sure to be in correct branch)
    * Run the build command (it will fetch another repo, sized ~23 GB)
    * Stop the build after the second repo's fetched
    * Check `/downloads` folder to ensure second repo's files are actually there (you did not break the code too early or too late)
    * Archive the whole thing (do **not** use zip; it does not keep file permissions)    
    * Fetch that file from that machine to your local machine
    * Unarchive it    
    * Git repair and confirm there is not any problem
    * This method does work in a few attempts if you are lucky.
    
     
    
  * **Use docker:** Using 10+ years old OS might be best to (get less errors on) building yocto but will cause other problems. To use docker, refer to the official development documentation `Quectel_SC206E_Series_Linux_Compiling&Burning_Guide_V1.2.pdf`.    
    *For container-related information, check notes on the development machine.*    
    *Do not forget to share main folder with the host machine or it won't be accessible from the host machine.*

!!! danger "make sure you are not root"
    Yocto builds linux kernel. If something goes wrong (and have root priviliges), your host machine's own kernel might be overwritten; which would break your host computer irreversibly.

## **0. Creating Docker image with shared folder**

First unzip the BSP inside a clean folder:
```bash title="takes ~2 hours"
sudo tar --use-compress-program="pigz" -xvf /archivepath/archiveimage.tar.gz -C /work_dir
```

!!! note "take a backup"
    ```bash
    sudo tar -czvf /archivepath/yocto_project_backup_$(date +%F).tar.gz work_dir/
    ```

Then create a new docker image, using a working docker container and work folder:
```bash
sudo docker run -it --name Container-Name -v /work_dir/qcm2290_linux_r60_r004:/home/test/share/qcm2290_linux_r60_r004 working-yocto-env-v1.0 /bin/bash
```

Create another terminal and run (to fix permissions), otherwise host-os users/groups will not be able to write these files:
```bash title="cd /workdir"
sudo chown -R 1001:1001 qcm2290_linux_r60_r004/
```



## **1. Compiling whole yocto build**

!!! note "debug-perf"
    For release versions, do NOT use debug commands. Change `debug` with `perf` in commands/paths.

* *Ensure you are in the `qcm2290_r60_r004` folder*
    ```bash title="always verify -> user in that terminal must NOT be root"
    source build.sh
    ```
    ```bash title="takes many hours"
    build-qti-robotics-med-image
    ```
 First time and every time you make **changes on layers** it will compile it from the beginning, which will take many hours.    
 *Changing layers changes the signature of the build. When the signatures does not match, yocto does not trust the previous build, so it compiles everything from the scratch.*

After the compilation, the generated images are in `build-qti-distro-rb-debug/tmp-glibc/deploy/images/qrbx210-rbx/qti-robotics-med-image/`


## **2. Burning Firmware package**

!!! note "production"
    Train and use the OS which will be used in production for burning packages.    
    Get necessary drivers and tools from the Quectel's FTP server `202.111.194.162`
* Unzip `SC206E_Linux_Unpacking_Tool_xxx.zip`
* Copy image files created by yocto build    
    ```text title="from"
    build-qti-distro-rb-debug\tmp-glibc\deploy\images\qrbx210-rbx\qti-robotics-med-image\
    ```
    ```text title="to, inside SC206E_Linux_Unpacking_Tool_xxx"
    LA.UM.9.15.2\build-qti-distro-fullstack-noselinux-debug\tmp-glibc\deploy\images\qrbx210-rbx\qti-robotics-med-image\
    ```
* Files to be copied:
```text hl_lines="1 2 3 4 5 6 7 8 9"
abl.elf
boot.img
cache.img
persist.img
recoveryfs.img
system.img
systtemrw.img
userdata.img
vmlinux
```

* Run build.bat.
!!! warn "checklist"
    If python 3.x is installed, must be removed from the environment variables.    
    **`Python 2.7.18`** must be used ([python.org/downloads](https://www.python.org/downloads/)) and must be in the environment variables.    
    Quectel suggest using `cmd` instead of powershell.
    
* If it runs successfully, two critical lines will appear:    
    ```text hl_lines="1 5"
    [hh:mm:ss] - update_common_info.py:==========UPDATE COMMON INFO COMPLETE==========" 
    ...
    ...
    ...
    [hh:mm:ss] - zavier :==========UNPACKING COMPLETE==========" 
    ```
        * If there is a problem, it will be shown in the cmd.

* After build.bat runs successfully, `qcm2290_qfil_download_emmc` folder will be created automatically inside `SC206E_Linux_Unpacking_Tool_xxx`.

* Turn on `"EMG_DOWNLOAD"` switch on the board, power on the board and then the module enters USB QDLoader 9008 status. To verify it:
```cmd
adb devices
```
```text title="it must print"
USB QDLoader 9008
```    
    *if not, `adb reboot edl` so device enters edl mode.*

* Run `QFIL` tool, which must select correct COM port automatically and shows the Qualcomm device.
* Select **"Flat Build"** from the radio buttons as **Build Type**.
* **"Browse…"** **Programmer Path** field to select **`prog_firehose_ddr.elf`** from `qcm2290_qfil_download_emmc` directory.
* **"Load XML…" Rawprogram and Path** field to select **`rawprogram_unsparse0.xml`** and **`patch0.xml`** to store the target file.
* Click **`Download`** Button. Wait ~2 minutes. **Download Succeed** will appear in the status box.

!!! danger "Settings"
    **Do NOT **meddle with the Configuration window of QFIL!



## **3. Custom modifications**

### **3.1 Creating a new layer**

In order to not break something in the BSP, do not change anything in the source files. Instead create append files. For adding own custom services/apps, create a custom layer and work on that layer (instead of existing layers). In order to do so:

* Ensure you are in the docker image, correct (non-root) user and directory.
    ```bash title="load required variables and set correct paths"
    source build.sh
    ```
* Create a new layer
    ```bash title="new layer name = meta-custom"
    bitbake-layers create-layer ../../meta-custom
    ```
    ```bash title="add that layer to existing build"
    bitbake-layers add-layer ../../meta-custom
    ```
    ```bash title="verify if the layaer added"
    bitbake-layers show-layers
    ```
* Current tree for new layer should be:

    ```text title="in /qcm2290_linux_r60_r004/"
    meta-custom/
    ├── conf/
    │   └── layer.conf
    └── recipes-apps/
    ```
    !!! danger ""
        layer.conf file guide will be added later.



### **3.2 Creating a new app**
For each service or application to include in the build, a new app must be added to that layer. 

* First create a `.bbappend` file so we can add/remove our custom apps into the main build. That file must be in `meta-custom/recipes-products/images/` and it's name must be `qti-robotics-med-image.bbappend`, since `bitbake` will look only this name and path.
* Create a new app inside `recipes-apps` directory (by creating a new folder and a `.bb` file). Now the new layer's tree must be like this:
    ```text title="in /qcm2290_linux_r60_r004/"
    meta-custom/
    ├── conf/
    │   └── layer.conf
    ├── recipes-apps/
    │   └── custom-app-01/
    │       └── custom-app-01_0.1.bb
    │
    └── recipes-products/
        └── images/
            └── qti-robotics-med-image.bbappend
    ```
* Depending on the purpose of the app, there might be more files or folders inside the apps directory `custom-app-01/`. Research more.
* bitbake filename syntax is `app-name`_`version`.bb. Version name is not mandatory. If there are multiple files with different versions, bitbake will select the one with highest version number.
* Before adding the new app into the main build, always test it isolated first, to see if there is any compilation error:
```cmd
bitbake custom-app-01
```
<br>
<br>
* Creating a new layer/app inside the docker environment will not give permissions to write/execute/create new files inside that layer/app. To fix this (on the host machine):
```bash title="assuming in the correct folder"
sudo chmod -R a+rwX meta-custom/
```
    `a`: applies the changes to the owner and all other users and groups.    
    `+r`: adds read permission.    
    `+w`: adds write permission.    
    *or simply sudo chown -R 1001:1001 meta-custom/*

### **3.3 Including custom apps into the build**

Simply add this line to the `qti-robotics-med-image.bbappend`:
```bash
CORE_IMAGE_EXTRA_INSTALL += "custom-app-01"
```

To verify, first:
```bash
bitbake-layers show-recipes
```
Which hopefully shows the new app. Otherwise    

* Check if the new layer is added ([if not added](#31-creating-a-new-layer))
```bash
bitbake-layers show-layers
```
* If the output is too crowded
```bash
bitbake-layers show-layers | grep -n meta-custom
```

Additional verification:
```bash
bitbake -e qti-robotics-med-image | grep CORE_IMAGE_EXTRA_INSTALL
```    

[if still missing](#32-creating-a-new-app)



### **3.4 Other modifications**
!!! danger ""
    **will be added (GPIO/ssh/su pw/wifi/LTE)**

Permanent changes on existing files:
```text title="qcm2290_linux_r60_r004/src/vendor/qcom/proprietary/devicetree/qcom/scuba-pinctrl.dtsi, line 790, added:" hl_lines="4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20"
...
...
...
		/* Custom modification 03/11/2025 */
		/* Button config: GPIO 28 as input with pull-down */
		pmx_user_button {
			user_button_active: user_button_active {
				mux {
					pins = "gpio28";
					function = "gpio";
				};
				config {
					pins = "gpio28";
					drive-strength = <2>; /* mA, for???/*
					bias-pull-down;       /* idle = 0, pressed -> 1 */
					input-enable;
				};
			};
		};
		/* Custom modification 03/11/2025 ended*/
...
...
...
```

```text title="qcm2290_linux_r60_r004/poky/meta/recipes-connectivity/openssh/sshd.socket, line 6, changed:" hl_lines="4 5"
...
...
...
-ListenStream=127.0.0.1:22
+ListenStream=22
...
...
...
```


## **4. Bitbake Syntax** 


* In order to not compile an app during bitbake build, do not use empty `do_compile(){}` function. Instead remove the existing `do_compile` function and use:
```cmd
do_compile[noexec] = "1"
```



---
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>