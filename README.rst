rtl8812au
=========

Linux kernel driver for USB WiFi dongles based on Realtek rtl8812au chipset.

This is a fork of gordboy/rtl8812au, which is based on 5.2.20 realtek driver
version:

- https://github.com/gordboy/rtl8812au

gordboy repo already has VHT patches and is updated to work with latest kernels.

This repo is for testing various performance patches/tweaks on top of that.

Note that performance for 5.2.x driver version seem to be worse than for older
5.1.5, see "old-5.1.5" branch here for that version instead.

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


Performance
-----------

**Important:** these test results are for previous 5.1.5 driver version with
same VHT patches, results on 5.2.x (codebase here) may vary!

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

Relevant hostapd.conf options used for this specific dongle and test::

  hw_mode=a
  ieee80211n=1
  require_ht=1
  ieee80211ac=1
  require_vht=1

  channel=149
  vht_oper_chwidth=1
  vht_oper_centr_freq_seg0_idx=155
  ht_capab=[HT40+][SHORT-GI-40]
  vht_capab=[SHORT-GI-80][MAX-MPDU-11454][MAX-A-MPDU-LEN-EXP7][BF-ANTENNA-2][SU-BEAMFORMER][SU-BEAMFORMEE]

Same as for test results, these aren't necessarily supported by all dongles,
and some dongles might allow e.g. 160MHz or 80+80 channel widths
(different vht_oper_chwidth values), 4x4 MIMO/beamforming, and such,
which driver seem to have the code for.

For a bit more info on AP/STA mode configuration, see following links:

- http://blog.fraggod.net/2017/04/27/wifi-hostapd-configuration-for-80211ac-networks.html
- https://github.com/mk-fg/archlinux-pkgbuilds/issues/2#issuecomment-325991813


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


Links
-----

Repositories that seem to be most active (as of Jan 2018) wrt info on this
driver, i.e. places to watch for new issues, commits, pull requests and forks
(in no particular order):

- https://github.com/gordboy/rtl8812au/
- https://github.com/zebulon2/rtl8812au-driver-5.2.9
- https://github.com/aircrack-ng/rtl8812au/
- https://github.com/astsam/rtl8812au/
- https://github.com/abperiasamy/rtl8812AU_8821AU_linux/
- https://github.com/uminokoe/rtl8812AU/ (gone!)
- https://github.com/diederikdehaas/rtl8812AU/
- https://github.com/gnab/rtl8812au/
- https://github.com/ulli-kroll/rtl8821au/

Not all (or any?) of these forks are linked under "Forks" tab on github.

Be sure to check different branches in these, as there are several different
upstream sources (code dumps) for this driver, which these are usually based on.

More general links:

- Chip datasheet (rev May 2012) and documentation for various driver features
  (dated from around 2015, not up-to-date with the code):
  `see document/ dir in this repo <document>`_

- | Other ArchLinux AUR builds for this module (from different repos):
  | https://aur.archlinux.org/packages/?O=0&SeB=nd&K=8812au&outdated=&SB=n&SO=a&PP=50&do_Search=Go
