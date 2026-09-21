# Gap Policy (auto-seeded from capability probe)

*Machine: Apple M4 · MoltenVK 1.4.3 · Vulkan 1.4.357 · generated 2026-09-21 from `docs/baselines/baseline-M4-macOS27.json`*

| Capability | Status | Evidence (probe) | Action / Phase |
|---|---|---|---|
| Vulkan API ≥ 1.3 (DXVK 3.x hard gate) | **supported** | `apiVersion=1.4.357` | none |
| core.geometryShader | **hard-gap** | `geometryShader=False` | graceful per-call errors + single log line (P3.4/P3.5); GS content unsupported |
| core.tessellationShader | **supported** | `tessellationShader=True` | FL11 pipeline test (P3.7) |
| VK_EXT_transform_feedback (stream-out) | **hard-gap** | `transformFeedback=False` | upstream SO creation returns DXGI_ERROR_INVALID_CALL — acceptable graceful-fail (P3.6) |
| VK_KHR/EXT_robustness2 (robustBufferAccess2) | **supported** | `robustBufferAccess2=True` | if supported: REMOVE the force-off in dxvk_device_info.cpp (P3.3); else keep force-off |
| Depth clip semantics | **supported** | `depthClipEnable=False, depthClipControl=True` | prefer VK_EXT_depth_clip_control over force-off (P3.3) |
| VK_EXT_graphics_pipeline_library (compile stutter) | **hard-gap** | `graphicsPipelineLibrary=False` | port DXVK-async pipe compiler (P4.1–P4.5) |
| Present timing / present wait (upstream 44-commit tail) | **partial** | `presentTiming=False, VK_KHR_present_wait=True` | verify opt-in degrade path (P1.6) |
| Sparse/tiled resources (D3D11) | **supported** | `sparseBinding=True, sparseResidencyImage2D=True` | if supported: test a tiled-resource app; else documented-unsupported (P3.10) |
| Pipeline statistics queries (D3D11) | **hard-gap** | `pipelineStatisticsQuery=False` | graceful-zero + single log line (P3.10) |
| Custom border colors (D3D11 sampler) | **graceful-fail** | `customBorderColors=False` | DXVK gates on feature; keep default off (P2.1 option audit) |
| Sampler binding aliasing (d3d9) | **shim** | `MVK advertises no aliasing primitive; deAliasedSamplers shim in fork` | auto-enable when unsupported (P2.2) |
| 3.x descriptor-heap path | **fallback** | `descriptorBuffer=False` | verify non-heap fallback engages; bench it (P3.8) |
| Conservative rasterization (D3D11) | **best-effort** | `overestimationSize=0.5` | approximate per MVK; verify visually (P3.10) |
| Dual-source blending / logicOp / independentBlend | **supported** | `dualSrcBlend=True, logicOp=True` | none |

*(statuses: supported · shim · partial · fallback · best-effort · hard-gap · graceful-fail · BLOCKER)*

---

## Runtime validation addendum (Phase 2, P2.3–P2.8) — device-level verdicts

*Under MetalSharp wine-11.17 + bundled MoltenVK, DXVK `v3.1.1-macos.0` PE DLLs:*

| Lane | Device create | Clear/Present ×600 | 30-min soak | Verdict (device-level) |
|---|---|---|---|---|
| d3d9 (x64+i386) | ✅ | ✅ | ✅ 28 runs / 0 fail | **supported** |
| d3d8 (x64+i386) | ✅ | ✅ | rides d3d9 | **supported** (rides d3d9 lane) |
| d3d11+dxgi (x64+i386) | ✅ | ✅ | not soaked this phase | **supported** (device-level; soak in Phase 3) |

Full-content rendering (fixed-function variety, samplers edge cases) remains
Tier-2 pending real apps — see docs/TEST-APPS.md slots. Evidence:
`/Volumes/AverySSD/scratch-p012/smoke-runs/` (20260921-*).
