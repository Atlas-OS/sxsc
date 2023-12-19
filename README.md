# sxsc
A fork of [`echnobas`/sxsc](https://github.com/echnobas/sxsc) (the SxS compiler - pronounced sxs-see) for use in automatic package building for [Atlas](https://github.com/Atlas-OS/Atlas/actions/workflows/package-build.yaml).

GNU General Public License v3.0 [license](https://github.com/echnobas/sxsc/blob/a45c5f321153a0dd33266cb35fce3effac7212ad/LICENSE).

### Changes
- Removed [`gullible_installer.ps1`](https://github.com/echnobas/sxsc/blob/master/gullible_installer.ps1)
  - Not needed for building
  - [`online-sxs.cmd`](https://github.com/he3als/online-sxs) is used instead
- Removed binaries
  - They are included [by default](https://github.com/actions/runner-images/blob/main/images/win/Windows2022-Readme.md#installed-windows-sdks) in the `windows-latest` GitHub Action runner
  - Changed in the Python script to match that
  - Removed binaries:  `makecab, makecat, signtool`
- Add `requirements.txt`
- Files support