# 3DS battery patches
## Home Menu

**Battery icon in status bar with 25% bars (statusbaticon)**  
This patch makes the battery icon display each bar as 25% of battery charge.

<hr />

**Battery percent in status bar (statusbatpercent)**  
This patch replaces date in statusbar with battery percent.

![Preview](https://raw.githubusercontent.com/LittleFIve233/3ds-battery-patches/refs/heads/master/preview.png)

> It is not possible to display "%" character, so it shows battery percent as ":35:" instead.
> 
> If you have CHSSytem installed, you can use the % patch

## Building
1.Dumping extheader.bin from the 3DS and put it in the repo's root

2.Installing [Python](https://www.python.org/)

3.``pip install suppress``

4.Downloading [armips.exe](https://github.com/LittleFIve233/3ds-battery-patches/blob/master/armips.exe) to environment

5.Run ``make``
