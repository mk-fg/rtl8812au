rtl8812au
=========

**Note:** this is an old branch based on 5.1.5 realtek driver code, see master
branch for later 5.2.9 version with similar patchset.

Linux kernel driver for rtl8812au/rtl8821au/rtl8811au USB WiFi chipsets, based
on version 5.1.5 of upstream Realtek driver from xxNull-lsk/rtl8812AU and
uminokoe/rtl8812AU (no longer available):

- https://github.com/xxNull-lsk/rtl8812AU

Includes patches for VHT operation, removing hardcoded regulatory domain restrictions,
and some others, mostly cherry-picked from other driver versions (e.g. diederikdehaas/rtl8812AU),
plus some extra patches to build it on ArchLinuxARM.

For ArchLinuxARM PKGBUILDs of module from this repo for Raspberry Pi 2/3
(armv7h) and ODROID-C2 (aarch64), see:

- https://github.com/mk-fg/archlinux-pkgbuilds/tree/master/rtl8812au-5.1.5-rpi-git
- https://github.com/mk-fg/archlinux-pkgbuilds/tree/master/rtl8812au-5.1.5-odc2-git

Note that I'm not supporting or developing this driver here, just collected a
bunch of ad-hoc patches from different sources for my own purposes.

Please do not ask me to add or merge additional featues or fix something here -
I'm not a kernel developer and don't even have hardware to test this locally.


Performance
-----------

Should very heavily depend on card/dongle used, but with ALFA Network AWUS036AC
USB dongles plugged into RPi3/ODROID-C2 that I've tested using WiFi
Infrastructure mode (AP + STA) over VHT (802.11ac) with 80MHz channels (in 5GHz
band) and TX-STBC-2BY1/RX-STBC-1 MIMO parameters, throughput limit seem to be
about 220mbps or ~26 MiB/s (half-duplex).

I.e. something that looks like this::

  root@odc2:~# iperf3 -c 10.4.0.1 -t120
  Connecting to host 10.4.0.1, port 5201
  [  4] local 10.4.0.2 port 53667 connected to 10.4.0.1 port 5201
  [ ID] Interval           Transfer     Bandwidth       Retr  Cwnd
  [  4]   0.00-1.00   sec  20.0 MBytes   168 Mbits/sec    0    406 KBytes
  [  4]   1.00-2.00   sec  24.1 MBytes   202 Mbits/sec    0    471 KBytes
  [  4]   2.00-3.00   sec  21.7 MBytes   182 Mbits/sec    0    502 KBytes
  [  4]   3.00-4.00   sec  22.7 MBytes   191 Mbits/sec    0    550 KBytes
  [  4]   4.00-5.00   sec  22.2 MBytes   186 Mbits/sec    0    570 KBytes
  [  4]   5.00-6.00   sec  23.0 MBytes   193 Mbits/sec    0    595 KBytes
  [  4]   6.00-7.00   sec  21.4 MBytes   179 Mbits/sec    0    617 KBytes
  [  4]   7.00-8.00   sec  21.5 MBytes   180 Mbits/sec    0    636 KBytes
  [  4]   8.00-9.00   sec  25.1 MBytes   211 Mbits/sec    0    663 KBytes
  [  4]   9.00-10.00  sec  25.7 MBytes   216 Mbits/sec    0    689 KBytes
  [  4]  10.00-11.00  sec  27.2 MBytes   228 Mbits/sec    0    708 KBytes
  [  4]  11.00-12.00  sec  27.3 MBytes   229 Mbits/sec    0    747 KBytes
  [  4]  12.00-13.00  sec  25.1 MBytes   210 Mbits/sec    0    769 KBytes
  [  4]  13.00-14.00  sec  25.9 MBytes   217 Mbits/sec    0    775 KBytes
  [  4]  14.00-15.00  sec  26.0 MBytes   218 Mbits/sec    0    826 KBytes
  [  4]  15.00-16.00  sec  25.5 MBytes   214 Mbits/sec    0    871 KBytes
  [  4]  16.00-17.00  sec  26.6 MBytes   223 Mbits/sec    0    888 KBytes
  [  4]  17.00-18.00  sec  24.0 MBytes   201 Mbits/sec    0    892 KBytes
  [  4]  18.00-19.00  sec  26.5 MBytes   222 Mbits/sec    0    921 KBytes
  [  4]  19.00-20.00  sec  26.6 MBytes   223 Mbits/sec    0    933 KBytes
  [  4]  20.00-21.00  sec  26.3 MBytes   221 Mbits/sec    0    952 KBytes
  [  4]  21.00-22.00  sec  26.3 MBytes   221 Mbits/sec    0    981 KBytes
  [  4]  22.00-23.00  sec  26.9 MBytes   225 Mbits/sec    0   1008 KBytes
  [  4]  23.00-24.00  sec  26.5 MBytes   223 Mbits/sec    0   1014 KBytes
  [  4]  24.00-25.00  sec  22.6 MBytes   190 Mbits/sec    0   1.00 MBytes
  ^C[  4]  25.00-25.91  sec  21.6 MBytes   199 Mbits/sec    0   1.00 MBytes
  - - - - - - - - - - - - - - - - - - - - - - - - -
  [ ID] Interval           Transfer     Bandwidth       Retr
  [  4]   0.00-25.91  sec   638 MBytes   207 Mbits/sec    0             sender
  [  4]   0.00-25.91  sec  0.00 Bytes  0.00 bits/sec                  receiver
  iperf3: interrupt - the client has terminated

Again, these results are for one specific dongle, running in a specific
environment, so does not mean that other devices supported by this driver will
have same limitations, and are here just to show that driver itself can at least
support that much throughput (easily - extra cpu load is negligible).

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
  vht_capab=[SHORT-GI-80][TX-STBC-2BY1][MAX-MPDU-11454][MAX-A-MPDU-LEN-EXP7][RX-STBC-1]

Same as for test results, these aren't necessarily supported by all dongles, and
other dongles might allow e.g. 160MHz or 80+80 channel widths (different
vht_oper_chwidth values), 2x2 or 4x4 STBC, beamforming, and such, which driver
seem to reject for AWUS036AC that was used here, but has the code for.


Links
-----

Repositories that seem to be most active (as of April 2017) wrt info on this
driver, i.e. places to watch for new issues, commits, pull requests and forks
(in no particular order):

- https://github.com/abperiasamy/rtl8812AU_8821AU_linux
- https://github.com/uminokoe/rtl8812AU/
- https://github.com/diederikdehaas/rtl8812AU/
- https://github.com/astsam/rtl8812au/ (esp. for 8814A and radiotap stuff)
- https://github.com/gnab/rtl8812au/
- https://github.com/Grawp/rtl8812au_rtl8821au/
- https://github.com/ulli-kroll/rtl8821au/

Not all (or any?) of these forks are linked under "Forks" tab on github.

Be sure to check different branches in these, as there are several different
upstream sources (dumps) for this driver, which these are usually based on.

More general links:

- Datasheet: https://wenku.baidu.com/view/733fb49602020740be1e9bb0.html

- | Other ArchLinux AUR builds for this module (from different repos):
  | https://aur.archlinux.org/packages/?O=0&SeB=nd&K=8812au&outdated=&SB=n&SO=a&PP=50&do_Search=Go
