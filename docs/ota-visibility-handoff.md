# OTA "In Progress" Visibility — Hand-off

Date: 2026-05-14

## What this does

The website firmware-update page (`#/app/firmware_update`) only ever showed two states:
**"Sırada"** (queued) and **"Yüklendi"** (installed). These changes make it also show
**"Görev Yükleniyor"** (in progress) for every device while the firmware is actually
transferring — for both legacy per-chunk and modern streaming devices.

Most of the plumbing already existed: the OTA server has a direct SQL connection to the
`Taksimetre` DB, already has an `updateDeviceInfo()` writer, and `UpdateInfo == 6` is
already in the C# `GorevDurumu` enum and the frontend grid renderer. It simply never
fired for modern devices. Four small edits across three repos close that gap.
**No DB schema change, no EF-model regeneration.**

---

## Part 1 — Changes to apply

### Repo 1 — Taksimatik_OTA_Backend  (Node.js OTA server)

**File: `DevelopmentOTA/ext/AuthenticationManager.js`** — `updateDeviceInfo()` now updates `MainUpdate` too

```diff
@@ -248,7 +248,15 @@ class AuthenticationManager {
                     WHERE DeviceId = @deviceId
                       AND (UpdateType = 2 OR UpdateType = 3)
                       AND ActiveFirmware = 1
-                      AND UpdateInfo <> @updateValue
+                      AND UpdateInfo <> @updateValue;
+
+                    UPDATE MainUpdate
+                    SET UpdateInfo = @updateValue,
+                    Havuz = CASE WHEN @updateValue = 3 THEN 1 ELSE Havuz END
+                    WHERE DeviceId = @deviceId
+                      AND (UpdateType = 2 OR UpdateType = 3)
+                      AND Active = 1
+                      AND UpdateInfo <> @updateValue;
                 `);
```

*Why:* `updateDeviceInfo()` only updated `Device_Confs_Update` (legacy FW < 25 devices).
The added `UPDATE MainUpdate` gives modern FW ≥ 25 devices the same status. Identical
SET/WHERE shape; `MainUpdate` has no `ActiveFirmware` column so it uses `Active` instead.
A device's active firmware task is in exactly one of the two tables, so one UPDATE hits
0 rows and the other 0–1.

**File: `DevelopmentOTA/index.js`** — write the status at authentication time

```diff
@@ -118,6 +118,7 @@ async function TcpServerStart() {
 						console.log("DeviceId:" + d.deviceId + " Firmware Update Existed ... Mode: " + (session.streamingMode ? "STREAMING" : "per-chunk"));
                         console.log("DeviceId:" + d.deviceId + " Firmware Update Existed ... (X) - (X) - (X) - (X) - (X) - (X) - (X) - (X)");
                         session.authState = 1;
+                        auth_manager.updateDeviceInfo(d.deviceId, 6);   // flag task in-progress now; the 30s timer misses fast streaming sessions
                     } else {
```

*Why:* the existing 30-second timer that writes `UpdateInfo = 6` only catches long-lived
per-chunk sessions. Streaming sessions (FW ≥ 36) finish server-side in milliseconds and
are never scanned by it. Calling `updateDeviceInfo(d.deviceId, 6)` in the `0xFA`
Firmware-Ask handler marks the task in-progress the instant the device authenticates —
covering both modes. Fire-and-forget, matching the existing 30s-timer call style.

### Repo 2 — taksimetreBackend  (C# / .NET)

**File: `Api/Controllers/PublicController.cs`** — recover tasks stuck "in progress", inside `FirmwarePoolService()`

Inserted between the existing `foreach` loop's closing brace and the method's `db.SaveChanges();`:

BEFORE:
```csharp
                    }
                    db.SaveChanges();

                    return Request.CreateResponse(HttpStatusCode.OK, true);
```

AFTER:
```csharp
                    }

                    // Recover firmware tasks stuck "in progress" (UpdateInfo == 6): the OTA server marks a
                    // task in-progress when a device connects; if the device dies mid-transfer (or the OTA
                    // server restarts), the row would sit at 6 forever, holding an activeFirmwareLimit slot.
                    // Queried from the real tables (not a projection) so the rows are EF-tracked and persist.
                    var stuckThreshold = DateTime.Now.AddHours(-3);
                    int loadingState = (int)GorevDurumu.GorevYukleniyor;
                    int bouncedState = (int)GorevDurumu.GorevSıradanCıkarıldı;

                    var stuckLegacyUpdates = db.Device_Confs_Update
                        .Where(u => u.UpdateType == 2 && u.Active == true && u.Havuz == false
                                    && u.UpdateInfo == loadingState && u.QueueEntryDate < stuckThreshold)
                        .ToList();
                    var stuckMainUpdates = db.MainUpdate
                        .Where(u => u.UpdateType == 2 && u.Active == true && u.Havuz == false
                                    && u.UpdateInfo == loadingState && u.QueueEntryDate < stuckThreshold)
                        .ToList();

                    foreach (var stuckEntity in stuckLegacyUpdates)
                    {
                        var fw = db.DeviceLastInfo.Find(stuckEntity.DeviceId)?.FirmwareVersion;
                        if (fw > 16 && fw < 50)
                        {
                            stuckEntity.Havuz = true;
                            stuckEntity.UpdateInfo = bouncedState;
                        }
                    }
                    foreach (var stuckEntity in stuckMainUpdates)
                    {
                        var fw = db.DeviceLastInfo.Find(stuckEntity.DeviceId)?.FirmwareVersion;
                        if (fw > 16 && fw < 50)
                        {
                            stuckEntity.Havuz = true;
                            stuckEntity.UpdateInfo = bouncedState;
                        }
                    }

                    db.SaveChanges();

                    return Request.CreateResponse(HttpStatusCode.OK, true);
```

*Why:* once the OTA server writes `6` to modern devices, a device that dies mid-transfer
(or an OTA-server restart, which wipes its in-memory session map) would leave its row at
`6` forever — `FirmwarePoolService` *exempts* `UpdateInfo == 6` from its 30-minute
stale-bounce, but `activeCount` still *counts* it against `activeFirmwareLimit`. Left
unhandled, stuck `6` rows slowly starve the update queue. This block bounces rows stuck
at `6` whose `QueueEntryDate` is older than 3 h back to the pool (`Havuz = true`,
`UpdateInfo = 3`). Bouncing only frees the queue slot — it does not interrupt an active
TCP transfer, and the device-facing completion paths are not gated on `UpdateInfo`, so a
device that does eventually finish still completes normally.

It queries `Device_Confs_Update` / `MainUpdate` directly (EF-tracked entities) rather
than extending the existing `foreach (var entity in allOldUpdates)` loop right above it —
that loop iterates a projection and does not persist (see Part 3).

### Repo 3 — taksimetreFrontend  (AngularJS)

**File: `app/tpls/firmware_update/list.js`** — live grid auto-refresh, inside `FirmwareUpdateCtrl`

BEFORE:
```js
    // setInterval(function () {
    //     $("#grid").data("kendoGrid").dataSource.read();
    // }, 30000);
```

AFTER:
```js
    // Firmware-update tasks change state on the OTA server side (queued -> in progress -> installed);
    // auto-refresh the grid so operators see those transitions without a manual reload.
    var firmwareRefreshTimer = $interval(function () {
        var grid = $("#grid").data("kendoGrid");
        if (grid) { grid.dataSource.read(); }
    }, 15000);

    $scope.$on('$destroy', function () {
        $interval.cancel(firmwareRefreshTimer);
    });
```

*Why:* the firmware-update grid only refreshed on manual button clicks (the auto-refresh
was commented out). This restores it as a proper `$interval` (15 s) with a grid-existence
guard and `$destroy` cleanup, so operators see the queued → in progress → installed
transitions live. `$interval` is already injected into the controller, and the `case 6`
("Görev Yükleniyor") renderer already exists in this file — no other frontend change is
needed. The interval is tunable (one number); the previous commented-out value was 30 s.

---

## Part 2 — Git playbook  (run these yourself — nothing was committed)

The 3 cosmetic comment-date lines that were uncommitted in `index.js` before this work
have been reverted, so the OTA server working tree now contains **only** the two intended
changes (`git diff` confirmed: `index.js` +1 line, `AuthenticationManager.js` +8 lines).

### OTA server — real git repo, clean patch possible

The server team's `Taksimatik_OTA_Backend` is at the same commit as this clone
(`7c770cb`), so a `format-patch` from here will `git am` cleanly onto their repo.

```
cd docs-tests/external/old-ota-server
git checkout -b ota-progress-visibility
git add DevelopmentOTA/index.js DevelopmentOTA/ext/AuthenticationManager.js
git commit -m "OTA: write UpdateInfo=6 (in progress) for all devices"
git format-patch -1 HEAD
```

Leave the untracked `README.md` / `SERVER-patch-*.md` / `ota server kod degisiklikleri.txt`
files alone — they're docs-tests artifacts, not OTA-server source. The `git add` above
stages only the two intended files.

Suggested commit message body:
```
updateDeviceInfo() now also UPDATEs MainUpdate, not just Device_Confs_Update,
so modern (FW>=25) devices get the in-progress status. index.js calls
updateDeviceInfo(deviceId, 6) in the 0xFA handler so streaming sessions --
which finish before the 30s timer scans them -- are also marked.
```

### Frontend & C# backend — zip snapshots, no git

These two folders have no git and no shared history with the server team's live repos, so
a `format-patch` from here would **not** `git am` onto their repos. The deliverable for
these two is **Part 1 above** — the server team applies the change directly to their
`app/tpls/firmware_update/list.js` and `Api/Controllers/PublicController.cs`.

If you want local version tracking on the snapshot folders anyway:
```
cd docs-tests/external/server/taksimetreFrontend-develop      # then repeat for taksimetreBackend-develop
git init
git add -A
git commit -m "snapshot baseline + OTA-visibility change"
```
That is one combined commit — adequate for local tracking. If you specifically want a
clean baseline/change split for those two (so `format-patch` produces an isolated patch),
say so and the two edits can be reverted, baseline committed, then re-applied.

---

## Part 3 — Issues found during this work, NOT fixed here

Both were found by Gemini during review and deliberately left out of this change — each
is a runtime-behaviour change in a sensitive path that deserves its own separate canary,
not a ride-along with a visibility feature.

1. **OTA server closes the SQL pool after every authentication.**
   `DevelopmentOTA/ext/AuthenticationManager.js` — `authenticateAndProcess()`'s `finally`
   calls a global `sql.close()`. The pool is the module-global `mssql` singleton shared by
   all concurrent device handlers, so this races every other in-flight operation and
   causes intermittent firmware-auth failures under load (up to `CONNECTION_LIMIT = 75`
   concurrent). The pool's own config (`min:100, max:300`) already expects a persistent
   pool. Fix: remove `closeDatabaseConnection()` from that `finally`.

2. **`FirmwarePoolService`'s stale-task recovery loop is a silent no-op.**
   `Api/Controllers/PublicController.cs` — the existing `foreach (var entity in allOldUpdates)`
   modifies `FirmwareUpdateInfo` objects that are EF *projections*, not tracked entities,
   so `db.SaveChanges()` never persists them. Net effect: stale queued tasks
   (`UpdateInfo == 1`, older than 30 min) are never actually bounced back to the pool.
   (This is why the new block in Part 1 queries the real tables instead of reusing this
   loop.) Fix: rewrite the loop to fetch tracked entities, following the pattern the
   pool→queue promotion logic in the same method already uses.

---

## Verification done

- All three JavaScript files pass `node --check`.
- The C# change was reviewed against the EF6 patterns already used in the same method
  (the pool→queue promotion logic fetches tracked entities the same way). It has **not**
  been compiled here — the server team's MSBuild will confirm it.
- The OTA-server approach and the C# change were both independently reviewed by Gemini.
- The `UpdateInfo 6 → 5` completion path was verified safe: the device-facing endpoints
  (`FirmwareUpdate`, `criticalinfo`, `periodicdeviceinfo`) flip a row to `5` based on
  `Active == true` + firmware-version match, never on the current `UpdateInfo` value.
