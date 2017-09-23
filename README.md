# rtl8812au

**WARNING: DO NOT USE THIS FORK, USE gordboy/rtl8812au INSTEAD**

See old-5.1.5 branch for previous version (one that was here earlier) of this driver.

## Realtek 8812AU driver version 5.2.9

Works fine with Ubuntu 17.04 Zesty 4.10 kernel. Also now tested and working fine on 4.11, 4.12 and 4.13-rc1, after recent commits.
Only support 8812AU. Now has every known (to me) device USB ID, sorted by ID number.

Source builds with no warnings or errors, and is very stable in use.
Realtek seem to have done a decent job here.

Added (cosmeticly edited) original Realtek_Changelog.txt, this README.md, dkms.conf and a deb dkms package for convenience.

### Building

To build and install module manually:
```sh
$ make
$ sudo make install
```

To use dkms install:

```sh
  (as root, or sudo) copy source folder contents to /usr/src/rtl8812au-5.2.9
```

```sh
$ sudo dkms add -m rtl8812au -v 5.2.9
$ sudo dkms build -m rtl8812au -v 5.2.9
$ sudo dkms install -m rtl8812au -v 5.2.9
```

To use dkms uninstall and remove:

```sh
$ sudo dkms remove -m rtl8812au -v 5.2.9 --all
```

### Deb package

To install the dkms package on Debian, Ubuntu, Mint &etc:

```sh
$ sudo dpkg -i gord-rtl8812au-dkms_1.0-9_amd64.deb
```

To uninstall the dkms package on Debian, Ubuntu, Mint &etc:

```sh
$ sudo dpkg -P gord-rtl8812au-dkms
```

### NetworkManager

As others have noted, people using NetworkManager need to add this stanza to /etc/NetworkManager/NetworkManager.conf

```sh
  [device]
  wifi.scan-rand-mac-address=no
```
