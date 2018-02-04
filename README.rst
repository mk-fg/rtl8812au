rtl8812au
=========
---------------------------------------------------------------------------
Linux kernel driver for USB WiFi dongles based on Realtek rtl8812au chipset
---------------------------------------------------------------------------

.. contents::
  :backlinks: none



Description
-----------

Linux kernel driver for USB WiFi dongles based on Realtek rtl8812au chipset.

This is a fork of gordboy/rtl8812au, which is based on 5.2.20 realtek driver
version:

- https://github.com/gordboy/rtl8812au

gordboy repo already has VHT patches and is updated to work with latest kernels.

This repo is for testing various performance-related patches/tweaks on top of that.

For ArchLinuxARM PKGBUILD of module from this repo for ODROID-C2 (aarch64,
mainline 4.13.x+ kernel), see:

- https://github.com/mk-fg/archlinux-pkgbuilds/blob/master/rtl8812au-5.2.20-odc2-git/PKGBUILD

For more orthodox forks of this driver, which should probably be picked instead
of this one for any kind of general use, see following links:

- https://github.com/gordboy/rtl8812au/ (5.2.20)
- https://github.com/astsam/rtl8812au/ (5.1.5 with 8814A and radiotap patches)
- https://github.com/zebulon2/rtl8812au-driver-5.2.9 (used in Debian packages)
- https://aur.archlinux.org/packages/rtl8812au-dkms-git/ (Arch Linux AUR package)



Note on support / development / patches
---------------------------------------

I'm not supporting or developing this driver here, just collected a bunch of
ad-hoc patches from different sources for my own purposes.

Please do not ask me to add or merge additional featues or fix something here -
I'm not a kernel developer and don't even have hardware to test this locally.

Maybe just fork the repo and apply whatever you need there instead, or complain
about anything that doesn't work right to hardware vendor or realtek (though
note that they haven't released this code publicly - see source links at the top
of this README).



Upstreaming status
------------------

Coming from the future (2018+), you might find this driver to be superseded by
rtl8xxxu module in linux kernel, which aims to incorporate support for all such
dongles, based on code from realtek driver trees like this one.

| As of early 2018, 881xau ac dongles are not supported in mainline rtl8xxxu module.
| If you want to work on this stuff, maybe start there.
|

More info on history, rationale and internals of both rtl8xxxu and realtek
vendor drivers:
`"Jes Sorensen: rtl8xxxu - true love for cheap USB WiFi dongles"
Linux Plumbers 2016 talk slides (PDF, 2016-11-02)
<https://www.linuxplumbersconf.org/2016/ocw/system/presentations/4089/original/2016-11-02-rtl8xxxu-presentation.pdf>`_

Alternatively, support for these dongles in future kernels might come from
staging rtlwifi driver, as there's already one for rtl8822be (Aug 2017),
which includes bunch of common stuff (e.g. phydm) for ac dongles, and rtlwifi is
already used for some usb dongles.



Performance
-----------

Should very heavily depend on card/dongle used, but between two
ALFA Network AWUS036AC USB dongles plugged into RPi3/ODROID-C2 (USB 2.0)
that I've tested using WiFi Infrastructure mode (AP + STA) with VHT (802.11ac)
and 80MHz channels (in 5GHz band), throughput max with iperf3 seem to be about
220mbps or ~26 MiB/s (half-duplex).

Note that such result is for one specific pair of AP/STA dongles, running in a
specific environment and configuration, so does not mean that other devices
supported by this driver will have same limitations, and here just to show that
driver itself can at least support that much
(easily - extra cpu load is negligible, no bugs).

Relevant hostapd.conf options used for AP dongle and test::

  hw_mode=a
  ieee80211n=1
  require_ht=1
  ieee80211ac=1
  require_vht=1

  channel=52
  vht_oper_chwidth=1
  vht_oper_centr_freq_seg0_idx=58
  ht_capab=[HT40+][SHORT-GI-40]
  vht_capab=[SHORT-GI-80][MAX-MPDU-11454][MAX-A-MPDU-LEN-EXP7][BF-ANTENNA-2][SU-BEAMFORMER][SU-BEAMFORMEE]

Same as for test results, these aren't necessarily supported by all dongles,
and some dongles might allow e.g. 160MHz or 80+80 channel widths
(different vht_oper_chwidth values), 4x4 MIMO/beamforming, and such,
which driver seem to have the code for.

For a bit more info on AP/STA mode configuration, see following links:

- http://blog.fraggod.net/2017/04/27/wifi-hostapd-configuration-for-80211ac-networks.html
- https://github.com/mk-fg/archlinux-pkgbuilds/issues/2#issuecomment-325991813

Very similar performance between 5.1.5 (old-5.1.5 branch) and 5.2.20 (this one)
driver versions, while 5.2.9 (old-5.2.9.3 branch) is way worse.



Debugging
---------

First of all, enable DEBUG= with make or dkms.conf, e.g. ``make DEBUG=2``.

Values for DEBUG= are 0-3 for progressively more info, see Makefile and
include/autoconf.h for details or to tweak which specific bits should be enabled.

With DEBUG>0, kmsg logging verbosity can be controlled by rtw_drv_log_level=
module parameter: 0=none, 2=error, 3=warn, 4=info (default), 5=debug, 6=max.

For more information about what your specific dongle supports and is configured
for, use /proc interface (with DEBUG>0) that this driver provides under
``/proc/net/rtl8812au/``.

Some useful info nodes there (replace "wlan0" below with your interface name):

- ``/proc/net/rtl8812au/ver_info`` - loaded driver version.

- ``/proc/net/rtl8812au/drv_cfg`` - build-time driver configuration info.

- ``/proc/net/rtl8812au/log_level`` - kmsg (dmesg) logging control.

- ``/proc/net/rtl8812au/wlan0/phy_cap`` - phy capabilities (VHT, STBC,
  Beamforming, etc), as supported by hardware/driver and configuration,
  including resulting mask of them.

- ``/proc/net/rtl8812au/wlan0/{ap,sta}_info``

- Counters / stats / metrics:

  - ``/proc/net/rtl8812au/wlan0/rx_signal``
  - ``/proc/net/rtl8812au/wlan0/trx_info``
  - ``/proc/net/rtl8812au/wlan0/trx_info_debug``

  - ``/proc/net/rtl8812au/wlan0/rx_stat`` - counts of frames transmitted at
    specific mimo modes and rates (e.g. VHTSS2MCS4 = VHT + 2 Spatial Streams +
    MCS4 coding set, see include/hal_com.h and http://mcsindex.com/ ), gets
    reset after each poll.

  - ``/proc/net/rtl8812au/wlan0/{rx,tx,int}_logs`` - lots of counters.

- ``/proc/net/rtl8812au/wlan0/odm/cmd``

  Read/write "console" for phydm_cmd() (phydm_debug.c, PHY DM = PHY-layer
  Dynamic Management) interface in the driver, which can be used to debug its
  low-level operation.

  Expects "command arg1 arg2 ... argX" (commas also work) string to be written
  there, ending in newline, which goes to phydm_cmd() and output can be read via
  subsequent read on that node ("GET, nothing to print" indicates no output/command).

  `phydm-cmd.py script <phydm-cmd.py>`_ (python3/readline) in this repo can be
  used to work with this interface interactively.

  Some phydm_cmd() commands/examples:

  - ``-h`` - list supported commands, except ``-h`` itself and ``demo``.
  - ``demo 10 0x3a z abcde`` - dummy command to print arguments, parsed as different types.

  - ``dbg`` - controls debug logging for different phydm components.

    - ``dbg 100`` - dump different phydm debug logging components, and whether
      logging for each one is enabled ("V") or not (".").

      Should look something like this::

        ================================
        [Debug Message] PhyDM Selection
        ================================
        00. (( . ))DIG
        01. (( . ))RA_MASK
        02. (( V ))DYNAMIC_TXPWR
        03. (( . ))FA_CNT
        04. (( . ))RSSI_MONITOR
        05. (( . ))CCKPD
        06. (( . ))ANT_DIV
        07. (( . ))SMT_ANT
        ...

    - ``dbg 101`` - disable phydm debug logging (all components).

    - ``dbg 4 1`` - enable phydm debug logging for RSSI_MONITOR component - 04
      in the "dbg 100" list (see above, number parsed as decimal), 1=enable, 2=disable.

    These will be logged to kmsg/dmesg, same as other debug stuff from driver.

  - ``h2c 0x00 0x01 ... 0x07`` - send H2C command 0x00 to firmware with
    specified parameters.

    H2C = Host-To-Chip (?) command from CMD/EVENT mechanism to make firmware do
    stuff on its own (offload) or change parameters, reporting back via C2H event.
    See e.g. `RTL8712_D0_1_Programming_Guide_20090601.pdf
    <document/RTL8712_D0_1_Programming_Guide_20090601.pdf>`_ for info on such concepts.

    See h2c_cmd enum in ``include/hal_com_h2c.h`` for list of commands, or
    h2c_cmd struct in ``rtl8xxxu.h`` under linux sources (which is probably more
    descriptive), or similar stuff in rtlwifi module.

  - ... and there's much more of them.



Links
-----

Repositories that seem to be most active (as of Jan 2018) wrt info on this
driver, i.e. places to watch for new issues, commits, pull requests and forks
(in no particular order):

- https://github.com/gordboy/rtl8812au/
- https://github.com/zebulon2/rtl8812au-driver-5.2.9/
- https://github.com/aircrack-ng/rtl8812au/
- https://github.com/astsam/rtl8812au/
- https://github.com/abperiasamy/rtl8812AU_8821AU_linux/
- https://github.com/uminokoe/rtl8812AU/ (gone!)
- https://github.com/diederikdehaas/rtl8812AU/
- https://github.com/gnab/rtl8812au/
- https://github.com/ulli-kroll/rtl8821au/
- https://github.com/lwfinger/ (rtl vendor driver sources/communication)

Not all (or any?) of these forks are linked under "Forks" tab on github.

Be sure to check different branches in these, as there are several different
upstream sources (code dumps) for this driver, which these are usually based on.

More general links:

- Chip datasheet (rev May 2012) and documentation for various driver features
  (dated from around 2009-2015, not up-to-date with the code):
  `see document/ dir in this repo <document>`_

- List of 8812au devices (not necessarily have vid/pid listed in this driver!):
  `wikidevi.com link
  <https://wikidevi.com/wiki/Special:Ask?title=Special%3AAsk&q=%5B%5BChip1+model::RTL8812AU%5D%5D&po=%3FInterface%0D%0A%3FForm+factor=FF%0D%0A%3FInterface+connector+type=USB+conn.%0D%0A%3FFCC+ID%0D%0A%3FManuf%0D%0A%3FManuf+product+model=Manuf.+mdl%0D%0A%3FVendor+ID%0D%0A%3FDevice+ID%0D%0A%3FChip1+model%0D%0A%3FSupported+802dot11+protocols=PHY+modes%0D%0A%3FMIMO+config%0D%0A%3FOUI%0D%0A%3FEstimated+year+of+release=Est.+year&eq=yes&p%5Bformat%5D=broadtable&order%5B0%5D=ASC&sort_num=&order_num=ASC&p%5Blimit%5D=500&p%5Boffset%5D=&p%5Blink%5D=all&p%5Bsort%5D=&p%5Bheaders%5D=show&p%5Bmainlabel%5D=&p%5Bintro%5D=&p%5Boutro%5D=&p%5Bsearchlabel%5D=%E2%80%A6+further+results&p%5Bdefault%5D=&p%5Bclass%5D=sortable+wikitable+smwtable>`_

- | Other ArchLinux AUR builds for this module (from different repos):
  | https://aur.archlinux.org/packages/?O=0&SeB=nd&K=8812au&outdated=&SB=n&SO=a&PP=50&do_Search=Go
