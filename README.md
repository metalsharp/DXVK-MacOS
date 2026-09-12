# DXVK-MacOS

A maintained macOS/Wine fork of [Gcenx/DXVK-macOS](https://github.com/Gcenx/DXVK-macOS), refreshed onto upstream [DXVK v3.1](https://github.com/doitsujin/DXVK/releases/tag/v3.1).

This fork carries the MoltenVK compatibility work from Gcenx's DXVK-macOS project and ports PR #20, **“Fix D3D9 on MoltenVK: optional features + de-aliased sampler bindings,”** to the current DXVK 3.1 architecture and `dxbc-spirv` submodule.

## Release contents

The release asset contains:

- x86_64 and i386 Wine DLLs for D3D8, D3D9, D3D10Core, D3D11, and DXGI
- MoltenVK and its ICD manifest
- `libvulkan.dylib`, the Wine-compatible loader-name alias for the bundled MoltenVK library
- `dxvk.conf` with automatic MoltenVK D3D9 de-aliased sampler support
- The Wine Vulkan portability patch
- Checksums, license, and runtime instructions

The DXVK `dxgi.dll` is a D3D8/9/10/11 lane. It must not be mixed into a VKD3D-Proton D3D12 lane that uses a specialized DXGI bridge.

## Requirements

- macOS 15 or newer
- Meson and Ninja
- MinGW-w64 cross-compilers:
  - `x86_64-w64-mingw32-gcc/g++`
  - `i686-w64-mingw32-gcc/g++`
- `glslangValidator`
- Git with recursive submodule support
- Wine import libraries and headers for the target Wine runtime

The build produces Windows PE DLLs. The native macOS Vulkan/MoltenVK dependencies are loaded by Wine's Unix side and are not ARM64EC binaries.

## Build from source

```bash
git clone --recursive https://github.com/metalsharp/DXVK-MacOS.git
cd DXVK-MacOS
```

The repository pins upstream DXVK v3.1 and its submodules. Apply the maintained `dxbc-spirv` compatibility patch before building:

```bash
git submodule update --init --recursive
git -C subprojects/dxbc-spirv apply ../patches/dxbc-spirv-moltenvk.patch
```

Build the 64-bit Windows lane:

```bash
meson setup build.x86_64 \
  --cross-file build-win64.txt \
  --buildtype release \
  --prefix "$PWD/stage/x86_64"
meson compile -C build.x86_64
meson install -C build.x86_64
```

Build the 32-bit Windows lane:

```bash
meson setup build.i386 \
  --cross-file build-win32.txt \
  --buildtype release \
  --prefix "$PWD/stage/i386"
meson compile -C build.i386
meson install -C build.i386
```

The cross files use the standard MinGW-w64 tool names. If the Wine import libraries are outside the compiler's normal search paths, provide them through the compiler/linker search path or adapt the Meson dependency paths for the selected Wine build.

## Wine Vulkan portability fix

MoltenVK is reported as a Vulkan portability driver. Wine must enable `VK_KHR_portability_enumeration` and `VK_INSTANCE_CREATE_ENUMERATE_PORTABILITY_BIT_KHR` when creating the host Vulkan instance.

Apply the included patch to the matching Wine source tree:

```bash
cd /path/to/wine-source
git apply /path/to/DXVK-MacOS/patches/wine-vulkan-portability.patch
```

Rebuild the Unix `win32u` library and use the rebuilt Wine runtime. Keep the original Wine runtime backed up until application validation is complete.

## Runtime setup

Use a wow64 prefix for Steam-style mixed 64-bit/32-bit applications:

```bash
export WINEARCH=wow64
export WINEPREFIX=/path/to/prefix
```

Keep the DXVK DLLs and MoltenVK files in the same graphics lane. Set the loader and ICD paths before launching:

```bash
export DXVK_CONFIG_FILE=/path/to/dxvk-macos-v3.1/dxvk.conf
export VK_ICD_FILENAMES=/path/to/dxvk-macos-v3.1/MoltenVK_icd.json
export DYLD_LIBRARY_PATH=/path/to/dxvk-macos-v3.1
export WINEDLLOVERRIDES='d3d8,d3d9,d3d10core,d3d11,dxgi=n,b'
```

`dxvk.conf` contains:

```ini
d3d9.deAliasedSamplers = Auto
```

Use `d3d9.deAliasedSamplers = True` to force the MoltenVK-safe path or `False` for compatibility testing on drivers that support aliased image bindings.

## Provenance

- Upstream DXVK: `70d7508c01201ed3d4bfb33da42ba834eafe3857` (`v3.1`)
- Upstream `dxbc-spirv`: `37a97745bddaf56d717253b0e4565904ce5eb06c`
- Gcenx DXVK-macOS heritage: `1.10.x` branch and release history
- Ported PR #20 commits are recorded in `patches/dxbc-spirv-moltenvk.patch` and the release README

This project is an independent maintained fork and is not an official release of Gcenx, doitsujin, Wine, or MoltenVK. Preserve upstream copyright and license notices when redistributing binaries.
