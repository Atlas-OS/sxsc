# sxsc
A fork of [`echnobas`/sxsc](https://github.com/echnobas/sxsc) ('the SxS compiler') for use in automatic package building for [Atlas](https://github.com/Atlas-OS/Atlas/actions/workflows/package-build.yaml).

Credit goes to [@echnobas](https://github.com/echnobas) for this project. GNU General Public License v3.0 [license](https://github.com/echnobas/sxsc/blob/master/LICENSE).

### Changes
- Removed [`gullible_installer.ps1`](https://github.com/echnobas/sxsc/blob/master/gullible_installer.ps1)
  - Not needed for building
  - [`online-sxs.cmd`](https://github.com/he3als/online-sxs) is used instead
- Removed binaries
  - They are included [by default](https://github.com/actions/runner-images/blob/main/images/win/Windows2022-Readme.md#installed-windows-sdks) in the `windows-latest` GitHub Action runner
  - Changed in the Python script to match that
  - Removed binaries:  `makecab, makecat, signtool`
- Add `requirements.txt`

### References from original project
Anomalous Software Deterioration Corporation, awuctl, whatever127, asdcorp, may5062, stolenbytes, other anonymous people