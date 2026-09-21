# Upstream Sync SOP (P0.2)

Cadence: **on every upstream release tag** + a weekly `master` sweep. Never let
`git rev-list --count HEAD..upstream/master` exceed one release cycle (~60 commits).

## Procedure
1. `git fetch upstream --tags && git checkout -b sync/<upstream-tag> main`
2. `git merge upstream/master` — resolve conflicts favoring upstream except in:
   - `src/dxvk/dxvk_device_info.cpp` (MoltenVK feature table)
   - `src/d3d9/*` (deAliasedSamplers & fixed-function shims)
   - `patches/*`, `.github/workflows/*`
3. **Re-validate `patches/dxbc-spirv-moltenvk.patch`** whenever the submodule pointer moved:
   ```bash
   git submodule update --init --recursive subprojects/dxbc-spirv
   git -C subprojects/dxbc-spirv apply --check ../patches/dxbc-spirv-moltenvk.patch
   ```
   If it fails: re-derive the patch from upstream's diff of the failing hunk.
4. Re-run the capability probe; diff against `docs/baselines/*.json` — any feature
   change gets a gap-policy row update in the same commit.
5. Cross-build both PE lanes (CI or local), run `tools/smoke.sh d3d9`.
6. Merge to `main`, tag `<upstream-tag>-macos.N`, write release notes.

## Conflict policy
Upstream owns everything except the documented MoltenVK shim set. If upstream
fixes something a shim worked around, **delete the shim** and record it in
`docs/gap-policy.md` (shims are liabilities, not assets).
