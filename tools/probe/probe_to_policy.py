#!/usr/bin/env python3
"""
probe_to_policy.py — convert a capability-probe JSON report into seeded
docs/gap-policy.md rows, with automatic status derivation per capability.

Usage: python3 tools/probe/probe_to_policy.py <probe.json> [> docs/gap-policy.md]
"""
import json, sys, datetime

def load(path):
    with open(path) as f:
        return json.load(f)

def dev0(d):
    return d["device0"]

def rows(dev, meta):
    api = tuple(int(x) for x in dev["apiVersion"].split("."))
    exts = set(dev["extensions"])
    R = []

    def add(cap, status, evidence, action):
        R.append((cap, status, evidence, action))

    api_ok = api >= (1, 3, 0)
    add("Vulkan API ≥ 1.3 (DXVK 3.x hard gate)",
        "supported" if api_ok else "BLOCKER",
        f"apiVersion={dev['apiVersion']}", "none" if api_ok else "upgrade MoltenVK ≥1.3.0")

    add("core.geometryShader", "hard-gap" if not dev["core"]["geometryShader"] else "supported",
        f"geometryShader={dev['core']['geometryShader']}",
        "graceful per-call errors + single log line (P3.4/P3.5); GS content unsupported")

    add("core.tessellationShader", "supported" if dev["core"]["tessellationShader"] else "hard-gap",
        f"tessellationShader={dev['core']['tessellationShader']}", "FL11 pipeline test (P3.7)")

    tf = dev["ext"]["transformFeedback"] or "VK_EXT_transform_feedback" in exts
    add("VK_EXT_transform_feedback (stream-out)", "hard-gap" if not tf else "supported",
        f"transformFeedback={dev['ext']['transformFeedback']}",
        "upstream SO creation returns DXGI_ERROR_INVALID_CALL — acceptable graceful-fail (P3.6)")

    r2 = dev["ext"]["robustBufferAccess2"]
    add("VK_KHR/EXT_robustness2 (robustBufferAccess2)",
        "supported" if r2 else "hard-gap",
        f"robustBufferAccess2={r2}",
        "if supported: REMOVE the force-off in dxvk_device_info.cpp (P3.3); else keep force-off")

    dce = dev["ext"]["depthClipEnable"] in (True,) or "VK_EXT_depth_clip_enable" in exts
    dcc = dev["ext"]["depthClipControl"]
    add("Depth clip semantics",
        "supported" if dcc else ("shim" if dce else "audit"),
        f"depthClipEnable={dev['ext']['depthClipEnable']}, depthClipControl={dcc}",
        "prefer VK_EXT_depth_clip_control over force-off (P3.3)")

    gpl = dev["ext"]["graphicsPipelineLibrary"]
    add("VK_EXT_graphics_pipeline_library (compile stutter)",
        "hard-gap" if not gpl else "supported",
        f"graphicsPipelineLibrary={gpl}",
        "port DXVK-async pipe compiler (P4.1–P4.5)")

    pt = dev["ext"]["presentTiming"] or "VK_EXT_present_timing" in exts
    pw = "VK_KHR_present_wait" in exts
    add("Present timing / present wait (upstream 44-commit tail)",
        "supported" if pt else ("partial" if pw else "graceful-fail"),
        f"presentTiming={dev['ext']['presentTiming']}, VK_KHR_present_wait={pw}",
        "verify opt-in degrade path (P1.6)")

    sparse = dev["core"]["sparseBinding"] and dev["core"]["sparseResidencyImage2D"]
    add("Sparse/tiled resources (D3D11)", "supported" if sparse else "hard-gap",
        f"sparseBinding={dev['core']['sparseBinding']}, sparseResidencyImage2D={dev['core']['sparseResidencyImage2D']}",
        "if supported: test a tiled-resource app; else documented-unsupported (P3.10)")

    add("Pipeline statistics queries (D3D11)",
        "hard-gap" if not dev["core"]["pipelineStatisticsQuery"] else "supported",
        f"pipelineStatisticsQuery={dev['core']['pipelineStatisticsQuery']}",
        "graceful-zero + single log line (P3.10)")

    add("Custom border colors (D3D11 sampler)",
        "supported" if dev["ext"]["customBorderColors"] else "graceful-fail",
        f"customBorderColors={dev['ext']['customBorderColors']}",
        "DXVK gates on feature; keep default off (P2.1 option audit)")

    add("Sampler binding aliasing (d3d9)",
        "shim",
        "MVK advertises no aliasing primitive; deAliasedSamplers shim in fork",
        "auto-enable when unsupported (P2.2)")

    db = dev["ext"]["descriptorBuffer"]
    add("3.x descriptor-heap path",
        "supported" if db else "fallback",
        f"descriptorBuffer={db}",
        "verify non-heap fallback engages; bench it (P3.8)")

    add("Conservative rasterization (D3D11)",
        "best-effort" if "VK_EXT_conservative_rasterization" in exts else "hard-gap",
        f"overestimationSize={dev['conservativeRaster']['primitiveOverestimationSize']}",
        "approximate per MVK; verify visually (P3.10)")

    add("Dual-source blending / logicOp / independentBlend", "supported",
        f"dualSrcBlend={dev['core']['dualSrcBlend']}, logicOp={dev['core']['logicOp']}",
        "none")

    return R

def main():
    d = load(sys.argv[1])
    dev = dev0(d)
    meta = sys.argv[1]
    print("# Gap Policy (auto-seeded from capability probe)")
    print()
    print(f"*Machine: {dev['deviceName']} · MoltenVK {dev['driverInfo']} · Vulkan {dev['apiVersion']} · generated {datetime.date.today().isoformat()} from `{meta}`*")
    print()
    print("| Capability | Status | Evidence (probe) | Action / Phase |")
    print("|---|---|---|---|")
    for cap, status, ev, act in rows(dev, meta):
        print(f"| {cap} | **{status}** | `{ev}` | {act} |")
    print()
    print("*(statuses: supported · shim · partial · fallback · best-effort · hard-gap · graceful-fail · BLOCKER)*")

if __name__ == "__main__":
    main()
