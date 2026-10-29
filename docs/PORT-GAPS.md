# What the DXVK 3.1 port still needs

*2026-10-28. Compares Gcenx's DXVK-macOS 1.10.3 (98 commits on upstream v1.10.3) with this fork at `8d348236`
(upstream v3.1.1 plus `40e01640`), against the MoltenVK in MetalSharp Wine 4.0. Capabilities come from
`docs/baselines/baseline-M4-macOS27-metalsharp-wine-4.0.json`; see `docs/gap-policy.md`.*

The fork's goal is one DXVK for MetalSharp's Arm64 FEX build: the D3D8/9/10/11 lane (`GRAPHICS_BACKEND=dxvk`, today
DXVK-macOS 1.10.3) and the DXGI and D3D11On12 half of the VKD3D-Proton lane (today plain upstream DXVK 2.7.1, built for
x86_64 only, so it runs under FEX).

## What the MoltenVK probe changed

MetalSharp's MoltenVK passes every feature and extension DXVK 3.1.1 requires. It also has geometry shaders (as Metal
mesh pipelines), stream 0 transform feedback, `VK_EXT_depth_clip_enable`, cull distances (as clip distances),
`robustBufferAccess2` and `nullDescriptor`. Several items the 2026-09-21 gap policy treated as permanent gaps are
therefore checks, not workarounds, and the five requirements this fork relaxed in `dxvk_device_info.cpp`
(`geometryShader`, `shaderCullDistance`, `depthClipEnable`, `robustBufferAccess2`, `nullDescriptor`) can return to
upstream's strictness. A MoltenVK without them would then be rejected at device creation instead of rendering wrongly.

Still missing in MoltenVK: graphics pipeline libraries, pipeline statistics queries, custom border colors, descriptor
buffers, present timing, multiple transform feedback streams, and correct geometry shader limits (all reported as 0).

## Needed for D3D11 and the VKD3D-Proton lane

| # | Item | Where | Notes |
|---|---|---|---|
| 1 | Pipeline-statistics query crash | `dxvk_gpu_query.cpp:195-235`, `d3d11_query.cpp:44-75` | MoltenVK fails `vkCreateQueryPool` for this type, then `allocQuery` dereferences the null pool. Guard it, and return zeros for D3D11 pipeline-statistics queries when the feature is absent |
| 2 | D3D11On12 device check | `d3d11_main.cpp:280-454`, `dxvk_adapter.cpp:309-340` | `importDevice` wraps VKD3D-Proton's device without checking DXVK's requirements. Check them and log what is missing. VKD3D-Proton-MacOS also has to enable those features on the device it creates |
| 3 | The VKD3D lane's DXGI fixes | VKD3D-Proton-MacOS `patches/dxvk-macos-d3d12-dxgi.patch`, its formats patch, MetalSharp DXVK `8a82645` | Flip-model buffer counts, alpha modes, formats and D3D11On12 error detail. The lane's `validate-dxgi-*.sh` scripts gate on them |
| 4 | ARM64X build | new `build-arm64x.txt` | 1.10.3's cross file, `DXVK_ARCH_ARM64` under ARM64EC, `-marm64x` for the `dxbc-spirv` and `libdisplay-info` subprojects, and `d3d8.dll` in MetalSharp's build and staging scripts. CI currently rejects ARM binaries |
| 5 | Geometry shader limits | MoltenVK `MVKDevice.mm:3476-3480` | The mesh-pipeline geometry shaders need real limits (D3D11 allows 1024 output vertices). Then test geometry shader draws |
| 6 | Stream output | `d3d11_device.cpp:852` | Stream 0 is now supported, so upstream's path runs. Test it. Multi-stream stream output stays unsupported and should fail cleanly |
| 7 | Restore upstream's requirements | `dxvk_device_info.cpp` | See above |
| 8 | Depth clip guard | `dxvk_graphics.cpp:585-592` | Supported here, so not urgent. Chaining the depth clip struct only when the extension is enabled, with 1.10's `depthClampEnable = !depthClipEnable` otherwise, keeps other MoltenVK builds correct |
| 9 | Feature level reporting | `d3d11_features.cpp:204-212` | FL12_1 follows from conservative rasterization plus fragment shader interlock. Check that games taking those paths render |
| 10 | A smoke test that draws | `tools/smoke` | Today's smokes only create a device, clear and present |

## Needed later

| Item | Notes |
|---|---|
| Async pipeline compiling (P4) | No graphics pipeline libraries, no state cache (removed upstream in `57d5a1e4`) and no `VkPipelineCache`, so every new pipeline compiles while the game waits. 1.10.3's `dxvk_pipecompiler` maps onto 3.1.1's `DxvkPipelineWorkers` at `dxvk_graphics.cpp:1086-1115` |
| D3D9 render-target copies | 1.10.3 `7865799f` and `91fdf892` |
| D3D9 shadow samplers | 3.1.1 de-aliases 3 image variants per sampler, 1.10.3 had 5. Check shadow samplers |
| App profiles | LEGO and KSP2 from 1.10.3 |
| Stream-output `S_OK` fallback | 1.10.3 `ce15afaa`. Only for a MoltenVK without transform feedback |
| Docs | README's `../patches` path (CI uses `../../patches`), its `dxvk.conf` claim, and the state cache mentioned in `PHASE2-REPORT.md` |
