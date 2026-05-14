# OTA "In Progress" Visibility — Detailed Change Record

Date: 2026-05-14

## What this document is

A detailed engineering record of the four code changes made to add an "in progress"
state to the website's firmware-update page, plus the two pre-existing bugs found
during the work and deliberately left unfixed. For each item: what the code was, how
it behaved, what changed (or why it wasn't changed), the reasoning, the intended
result, and an honest statement of how far it has actually been validated.

Companion document: `ota-visibility-handoff.md` is the "what to apply" doc for the
server team (per-repo diffs + git playbook). *This* document is the "why, and how
sure are we" record.

## Verification status — read this first

Nothing here has been field-tested or run against production data. Specifically:

| Item | Validated by | NOT validated |
|---|---|---|
| Change 1, 2 (OTA server JS) | `node --check` passes; `git diff` confirms only the intended lines changed; OTA-server logic independently reviewed by Gemini | Not run against a live SQL Server or a real device session |
| Change 3 (frontend JS) | `node --check` passes; reviewed against the identical jQuery/grid patterns already in the same file | Not run in a browser; AngularJS digest/runtime behaviour not exercised |
| Change 4 (C# backend) | Reviewed against the EF6 patterns already used in the same method; independently reviewed by Gemini | **Not compiled** — no .NET build toolchain in this environment; the server team's MSBuild is what confirms it builds |
| Bug A, Bug B | Identified and confirmed by reading the code; both independently flagged by Gemini | — (these are *not* fixed, only documented) |

"Reviewed" means read carefully and checked against neighbouring code that does the
same kind of thing. It does not mean executed. Treat the C# in particular as
"compiles in principle, confirm with a build."

## Background — the system in brief

Three separate codebases cooperate on OTA firmware updates for the fleet
(~15,000 ESP32 devices):

- **OTA server** — `docs-tests/external/old-ota-server/DevelopmentOTA/`, a Node.js
  raw-TCP server. Devices connect to it over 4G and download firmware using a binary
  protocol. It also holds a direct `mssql` connection to the SQL Server database.
- **C# backend** — `docs-tests/external/server/taksimetreBackend-develop/`, the
  ASP.NET / Entity Framework 6 Web API behind the website. Same SQL database.
- **Frontend** — `docs-tests/external/server/taksimetreFrontend-develop/`, an
  AngularJS 1.x single-page app (the operator-facing website).

Key facts the rest of this document depends on:

- A firmware-update **task** is a database row. There are **two tables**:
  `Device_Confs_Update` for legacy devices (firmware version < 25) and `MainUpdate`
  for modern devices (FW >= 25). The website's grid reads from both.
- The task's status is the integer column **`UpdateInfo`**. Enum `GorevDurumu` in
  `Api/Services/UpdateService.cs`: `1` = queued ("Sırada"), `2` = pool ("Havuzda"),
  `3` = removed-from-queue ("Görev Sıradan Çıkarıldı"), `4` = manually closed,
  `5` = completed ("Yüklendi"), `6` = in progress ("Görev Yükleniyor").
- Two transfer modes: **per-chunk** (legacy, slow — the device requests each chunk,
  so the server-side session lives for many minutes) and **streaming** (FW >= 36,
  fast — the server dumps all chunks into the socket buffer in one synchronous loop
  and immediately drops the session, so the server-side session lives milliseconds).
- Before this work, the page only ever showed `1` (queued) and `5` (installed). The
  `6` ("in progress") state already existed in the enum and in the frontend grid
  renderer, and the OTA server already had a writer for it — it just never fired for
  modern devices, and never for streaming sessions. The four changes close that gap.

---

# Change 1 — OTA server: `updateDeviceInfo()` also updates `MainUpdate`

### File
`old-ota-server/DevelopmentOTA/ext/AuthenticationManager.js`, method
`updateDeviceInfo(deviceId, updateValue)` (~lines 237–256).

### Previous code
One SQL `UPDATE`, against `Device_Confs_Update` only:
```js
async updateDeviceInfo(deviceId, updateValue) {
    try {
        await this.connectToDatabase();
        await this.pool.request()
            .input('deviceId', sql.Int, deviceId)
            .input('updateValue', sql.Int, updateValue)
            .query(`
                UPDATE Device_Confs_Update
                SET UpdateInfo = @updateValue,
                Havuz = CASE WHEN @updateValue = 3 THEN 1 ELSE Havuz END
                WHERE DeviceId = @deviceId
                  AND (UpdateType = 2 OR UpdateType = 3)
                  AND ActiveFirmware = 1
                  AND UpdateInfo <> @updateValue
            `);
    } catch (error) {
        console.error(`Device ${deviceId} update failed:`, error.message);
    }
}
```

### Previous behavior
`updateDeviceInfo()` is called from the 30-second `setInterval` at the top of
`index.js` — with value `6` for devices that have an active in-memory session, and
`3` for sessions gone stale. Because the SQL only touched `Device_Confs_Update`, only
**legacy** devices (FW < 25) ever had their status written by the OTA server. Modern
devices keep their firmware-update task in `MainUpdate`, which this method never
touched — so a modern device's task row never moved off `1` (queued) until the device
completed and the C# side set it to `5`.

### The change
A second `UPDATE`, against `MainUpdate`, added to the same batched `.query()`:
```js
                  AND UpdateInfo <> @updateValue;

                UPDATE MainUpdate
                SET UpdateInfo = @updateValue,
                Havuz = CASE WHEN @updateValue = 3 THEN 1 ELSE Havuz END
                WHERE DeviceId = @deviceId
                  AND (UpdateType = 2 OR UpdateType = 3)
                  AND Active = 1
                  AND UpdateInfo <> @updateValue;
```
It mirrors the `Device_Confs_Update` statement exactly, with one difference:
`MainUpdate` has no `ActiveFirmware` column, so the predicate uses `Active = 1`
instead. (Verified against `Data/MainUpdate.cs`: `MainUpdate` has `Active` (bool) and
`Havuz` (nullable bool); it has no `ActiveFirmware` column.)

### Reasoning
- The feature needs the "in progress" status for *all* devices. Everything else was
  already in place (the writer, the enum value, the frontend renderer); the only gap
  on this side was that the writer hit one of the two tables.
- Both statements go in one `.query()` batch — one DB round-trip, smallest possible
  diff, and both statements reuse the same parameterised `@deviceId` / `@updateValue`
  inputs.
- A device's active firmware task exists in exactly one of the two tables, so one
  `UPDATE` matches 0 rows and the other matches 0 or 1. There is no double-write.
- Keeping the `MainUpdate` statement byte-for-byte parallel to the existing one —
  same `Havuz = CASE WHEN @updateValue = 3` clause, same `UpdateInfo <> @updateValue`
  no-op guard — keeps the behaviour predictable and easy to review.

### Behavior intended
While a modern (FW >= 25) device is mid-OTA, its `MainUpdate` row carries
`UpdateInfo = 6`. The C# `updatesFirmware` endpoint surfaces that value unchanged, and
the frontend grid renders it as "Görev Yükleniyor". Legacy devices are unaffected —
their statement is untouched.

### Caveats / confidence
- `UpdateInfo <> @updateValue` with a NULL `UpdateInfo` evaluates to UNKNOWN in SQL,
  so a NULL row would not be matched. This is identical to the existing
  `Device_Confs_Update` statement, which has the same predicate and runs in
  production. In practice `MainUpdate.UpdateInfo` for an active firmware task is never
  NULL — the C# `updatesFirmware` endpoint casts it `(int)u.UpdateInfo` unguarded and
  works, which proves it. The decision was to match the existing pattern, not to
  "improve" it under a visibility feature.
- `node --check` passes; `git diff` confirms exactly these 8 lines were added. Not run
  against a live database.

---

# Change 2 — OTA server: write `UpdateInfo = 6` at authentication time

### File
`old-ota-server/DevelopmentOTA/index.js`, the `0xFA && 0x00` ("Firmware Ask") handler
inside `TcpServerStart()` (~lines 99–128).

### Previous code
The `if (result)` branch — device authenticated, a firmware update exists:
```js
   if (result) {
        d.subOperationId = session.streamingMode ? 0x03 : 0x01;
        console.log("DeviceId:" + d.deviceId + " Firmware Update Existed ... Mode: " + (session.streamingMode ? "STREAMING" : "per-chunk"));
        console.log("DeviceId:" + d.deviceId + " Firmware Update Existed ... (X) - (X) - (X) - (X) - (X) - (X) - (X) - (X)");
        session.authState = 1;
    } else {
```

### Previous behavior
The only thing that wrote `UpdateInfo = 6` was the 30-second `setInterval` (~lines
13–39 of `index.js`), which walks the in-memory `sessionManager.sessions` map and
calls `updateDeviceInfo(deviceId, 6)` for each active session.

That works for **per-chunk** transfers: the session lives for many minutes, so the
30-second timer scans it repeatedly and keeps `6` written. It does **not** work for
**streaming** transfers (FW >= 36): the `0xFD` handler sends every chunk in one tight
synchronous loop, then immediately calls `sessionManager.removeSession()`. The
server-side session exists for milliseconds. The 30-second timer essentially never
sees a streaming session, so a streaming device never received `UpdateInfo = 6` — it
jumped straight from "Sırada" to "Yüklendi".

### The change
One line, immediately after `session.authState = 1;`:
```js
        session.authState = 1;
        auth_manager.updateDeviceInfo(d.deviceId, 6);   // flag task in-progress now; the 30s timer misses fast streaming sessions
```

### Reasoning
- The `0xFA` handler's `if (result)` branch is the one precise moment that means
  "this device has authenticated and a firmware download is about to start" — true
  for *both* transfer modes, and true regardless of how briefly the session then
  lives. Writing `6` here catches every device.
- It is fire-and-forget (not `await`-ed). That matches the existing call style in the
  30-second timer (`auth_manager.updateDeviceInfo(deviceId, 6);`, no `await`), and it
  keeps a DB round-trip off the device-facing response path. `updateDeviceInfo()` has
  its own `try/catch`, so a DB failure cannot break the OTA handshake.
- For per-chunk devices the 30-second timer still runs afterwards — this just makes
  the `6` appear immediately instead of up to 30 seconds later. For streaming devices
  this is the *only* write, and it is correct: the `6` then persists through the
  device's real download + reboot + check-in window, until the C# completion path
  flips it to `5`.

### Behavior intended
The instant any device authenticates for an OTA download, its task row reads "Görev
Yükleniyor" on the website and stays there until the device genuinely completes.
Streaming devices in particular now show the middle state instead of skipping it.

### Caveats / confidence
- Fire-and-forget means a failed DB write is silent: that device just doesn't get its
  `6` that cycle and looks like the old behaviour. The feature degrades gracefully; it
  never harms the firmware transfer itself. (See Bug A — the shared SQL pool is raced
  closed under load, so some of these writes *will* be lost intermittently.)
- `node --check` passes; `git diff` confirms exactly this one line was added.

---

# Change 3 — Frontend: live grid auto-refresh

### File
`server/taksimetreFrontend-develop/app/tpls/firmware_update/list.js`, controller
`FirmwareUpdateCtrl` (~lines 111–113).

### Previous code
```js
    // setInterval(function () {
    //     $("#grid").data("kendoGrid").dataSource.read();
    // }, 30000);
```

### Previous behavior
The firmware-update page's Kendo grid only re-fetched data on explicit user actions —
after the "Kapat" (close) action, after the "Yazılım Gönder" (send firmware) modal
closed, after the "Toplu Görev Kapat" (bulk close) modal closed. The time-based
auto-refresh existed only as a commented-out block. An operator watching the page saw
no status change unless they did something or reloaded the browser.

### The change
The commented-out block is replaced with a working `$interval`:
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

### Reasoning
- Changes 1 and 2 produce status changes on the *server* side. Without a client-side
  auto-refresh, an operator would never see them without manually reloading — the
  feature would be invisible in practice.
- `$interval` (Angular's service) is used instead of the previous code's raw
  `setInterval` for one concrete reason: it is cancellable. A raw `setInterval`, had
  it been uncommented, would keep firing forever after the operator navigated away
  from the page — a timer leak. `$scope.$on('$destroy', ...)` cancels it when the
  controller is torn down. `$interval` was already in the controller's injected
  dependency list (declared but unused), so no signature change was needed.
- The `if (grid)` guard: if the timer fires before the Kendo grid has finished
  initialising (slow load), `$("#grid").data("kendoGrid")` is `undefined` and calling
  `.dataSource.read()` on it throws. The guard makes that tick a harmless no-op. Gemini
  independently flagged the same risk and suggested the same guard.
- 15-second interval: a device's status changes within seconds of connecting, then
  sits at `6` for the ~12–45 minute transfer. 15 s is responsive for someone watching
  without hammering the `/Api/updatesFirmware` endpoint. The previous commented value
  was 30 s; it is a one-number tweak.
- The `$("#grid").data("kendoGrid").dataSource.read()` form is exactly the pattern the
  existing manual-refresh calls in this same file already use (lines ~107, ~123, ~136)
  — this change reuses it rather than introducing a new idiom.
- No change to the status renderer: the grid's `UpdateInfo` column template already
  has `case 6:` returning "Görev Yükleniyor" with a spinning-cog icon.

### Behavior intended
With the firmware-update page open, the grid quietly re-reads every 15 seconds, so an
operator running a fleet update watches rows move Sırada -> Görev Yükleniyor ->
Yüklendi on their own. Leaving the page cancels the timer cleanly.

### Caveats / confidence
- `node --check` passes. Not run in a browser — the AngularJS digest interaction and
  the jQuery `$("#grid")` lookup are reviewed against the identical existing code in
  this file, but not exercised live.

---

# Change 4 — C# backend: recover tasks stuck "in progress"

### File
`server/taksimetreBackend-develop/Api/Controllers/PublicController.cs`, method
`FirmwarePoolService()` (~lines 395–526). The new block is inserted between the
existing `foreach` loop's closing brace and the method's `db.SaveChanges();`.

### Previous code
There was none — this is a new block. For context, the method previously ended:
```csharp
                    foreach (var entity in allOldUpdates)
                    {
                        // existing stale-bounce loop — see Bug B; it is a no-op
                    }
                    db.SaveChanges();

                    return Request.CreateResponse(HttpStatusCode.OK, true);
```

### Previous behavior
`FirmwarePoolService()` is a cron-style endpoint that manages the firmware-update
queue. Two facts about how it treats `UpdateInfo == 6`:
- `activeCount` (~line 434) counts rows with `UpdateInfo == 6` **or** `UpdateInfo == 1`
  against the concurrency cap `activeFirmwareLimit` (50).
- The existing stale-bounce loop (~line 505) **explicitly exempts** `UpdateInfo == 6`
  from being bounced — i.e. a `6` row is treated as "actively in progress, don't
  touch."

Before this feature the C# side never set `6` itself, and the OTA server only set `6`
on `Device_Confs_Update` (legacy). So in practice `MainUpdate` rows never sat at `6`,
and the exemption never mattered.

Changes 1 and 2 break that assumption: the OTA server now sets `6` on `MainUpdate`
(modern) rows too. That introduces a **new failure mode**: a modern device that
authenticates (-> `6`) and then dies mid-transfer — or an OTA-server restart, which
wipes the in-memory session map — leaves the row stuck at `6` forever. It is exempt
from the stale-bounce, so nothing recovers it; but it still counts against
`activeFirmwareLimit`. Enough stuck rows would slowly starve the update queue.

### The change
A new self-contained block, before `db.SaveChanges();`:
```csharp
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
```

### Reasoning
- **The 3-hour threshold.** It only touches rows stuck at `6` with `QueueEntryDate`
  older than `DateTime.Now.AddHours(-3)`. A real transfer is ~12 min (streaming) to
  ~45 min (per-chunk), plus device reboot and first check-in — 3 hours is comfortably
  past any legitimate in-progress window, so a healthy update is never bounced. Gemini
  independently agreed 3 h is safe.
- **What "bounce" does.** It sets `Havuz = true; UpdateInfo = 3`, exactly as the
  existing stale-bounce *intends* to. That frees the `activeFirmwareLimit` slot and
  makes the row eligible for pool->queue promotion again. It deliberately does **not**
  set `Active = false` — the task is still active, so if the device does eventually
  return, the device-facing completion endpoints still complete it normally.
- **Why it queries the real tables instead of extending the existing loop.** The
  original plan for Change 4 was a small `else if` added inside the existing
  `foreach (var entity in allOldUpdates)` loop. That was abandoned because that loop
  is a no-op — it iterates EF *projections*, not tracked entities, so nothing it does
  persists (this is Bug B, below). The new block instead queries
  `db.Device_Confs_Update` / `db.MainUpdate` directly, which returns real tracked
  entities, so the method's existing `db.SaveChanges()` actually writes the change.
  Querying each table separately also avoids a second problem with the projection: it
  conflates `Device_Confs_Update.UpdateId` and `MainUpdate.MainUpdateId` into one
  `UpdateId` field, so a projected row doesn't know which table it came from.
- **The `fw > 16 && fw < 50` guard.** Copied verbatim from the existing stale-bounce
  loop's guard, for consistency. Every OTA-capable device today (legacy ~17–24,
  modern ~36–40) is inside that range, so it is effectively always-true now; it was
  kept rather than diverged from the sibling logic. Gemini noted the hardcoded bounds
  are fragile long-term (they silently stop covering FW >= 50) — noted, not changed.
- **Null-safety.** `db.DeviceLastInfo.Find(...)?.FirmwareVersion` uses the
  null-conditional operator, so a device with no `DeviceLastInfo` row yields `null`,
  and `null > 16` is `false` — the row is left alone. The existing loop does an
  unguarded `.FirmwareVersion` that would throw a `NullReferenceException` and abort
  the whole cron run; the new block was deliberately made safer than its neighbour.

### Behavior intended
A modern device that starts an OTA and then disappears — or the case of an OTA-server
restart mid-transfer — no longer leaves a permanently-stuck `6` row eating a
concurrency slot. After 3 hours, `FirmwarePoolService` bounces the row back to the
pool, the slot is freed, and the row is re-queued so the device can retry when it
returns.

### Caveats / confidence
- **Not compiled.** There is no .NET build toolchain in this environment. The code is
  reviewed against the EF6 patterns already used in this same method — in particular
  the pool->queue promotion logic (~lines 452–465), which fetches tracked entities via
  `db.Device_Confs_Update.FirstOrDefault(...)` and modifies them in exactly this way.
  The server team's MSBuild is what confirms it compiles. The one identifier handled
  with care: `GorevDurumu.GorevSıradanCıkarıldı` uses the Turkish dotless-ı in both
  syllables — it was copied from `Api/Services/UpdateService.cs`, not retyped.
- This is the change that grew most from its plan: from a ~6-line `else if` to a
  ~25-line block, because the planned approach turned out to sit on top of Bug B.

---

# Pre-existing Bug A — OTA server closes the SQL pool after every authentication

**Status: NOT fixed. Documented and flagged for a separate, deliberate fix.**

### File
`old-ota-server/DevelopmentOTA/ext/AuthenticationManager.js`.

### The code
`authenticateAndProcess()` — the core firmware-auth function, called from the `0xFA`
handler — does its database work in a `try` whose `finally` calls
`closeDatabaseConnection()`:
```js
async closeDatabaseConnection() {
    if (this.pool) {
        await sql.close();   // closes the GLOBAL mssql pool
        this.pool = null;
    }
}
```
`connectToDatabase()` lazily re-creates it: `if (!this.pool) { this.pool = await sql.connect(this.sqlConf); }`.

### The behavior (why it is a bug)
The `mssql` library's `sql.connect()` / `sql.close()` act on a single **module-global**
connection pool. There is exactly one `AuthenticationManager` instance
(`const auth_manager = new AuthenticationManager(1024)` at the top of `index.js`),
shared by every device's socket handler. So when device A's `authenticateAndProcess()`
finishes and its `finally` calls `sql.close()`, it tears the pool down **for every
other device currently mid-query**. With `CONNECTION_LIMIT = 75` concurrent devices,
this races continuously: a device whose query is in flight when another device's
`finally` fires gets a "connection is closed" error. The visible result is
intermittent firmware-auth failures under load — a device gets a negative result, is
told "no firmware update," and retries later. The pool is configured `min: 100,
max: 300` — it is *designed* to be a long-lived warm pool; the per-call `sql.close()`
fights its own configuration.

### Relevance to this feature
Change 2's `updateDeviceInfo(d.deviceId, 6)` call is one more consumer of that same
shared, racily-closed pool. It degrades gracefully — the call is `try/catch`'d and
fire-and-forget, so a lost write just means a missed `6` for that device that cycle —
so the feature does **not** worsen the bug, and `authenticateAndProcess` itself is far
more exposed to it than this small write. But it is adjacent and real, which is why
it is recorded here.

### Why it was NOT fixed here
Removing the `sql.close()` is the correct fix, but it is a runtime-behaviour change in
the **core firmware-auth path**: the pool would then hold 100+ persistent connections
(its configured intent, but still a behavioural change). That deserves its own canary
and its own focused attention — not a silent ride-along inside a visibility feature,
where it would muddy that feature's canary signal. Per the user's decision
(2026-05-14), it is a separate, deliberate fix.

### Recommended fix
Remove the `closeDatabaseConnection()` call from `authenticateAndProcess()`'s `finally`
(the method then becomes dead code). The lazy `connectToDatabase()` already reuses
`this.pool` across calls. Before deploying, confirm the SQL Server can handle the
resulting persistent connection count from the OTA-server process.

### Found by
Gemini, during the independent review of the OTA-server changes for this feature.

---

# Pre-existing Bug B — `FirmwarePoolService`'s stale-task loop is a silent no-op

**Status: NOT fixed. Documented and flagged for a separate, deliberate fix.**

### File
`server/taksimetreBackend-develop/Api/Controllers/PublicController.cs`,
`FirmwarePoolService()` (~lines 503–517).

### The code
```csharp
var allOldUpdates = OldActiveUpdates1.Concat(OldActiveUpdates2).OrderByDescending(u => u.Time);

foreach (var entity in allOldUpdates)
{
    var FirmwareVersion = db.DeviceLastInfo.Find(entity.DeviceId).FirmwareVersion;
    if (entity.UpdateInfo != (int)GorevDurumu.GorevYukleniyor && (FirmwareVersion > 16 && FirmwareVersion < 50))
    {
        entity.Havuz = true;
        entity.UpdateInfo = (int)GorevDurumu.GorevSıradanCıkarıldı;
    }
}
db.SaveChanges();
```
`OldActiveUpdates1` / `OldActiveUpdates2` are built as
`db.Device_Confs_Update.Where(...).Select(x => new FirmwareUpdateInfo { ... })` and
`db.MainUpdate.Where(...).Select(x => new FirmwareUpdateInfo { ... })`.

### The behavior (why it is a bug)
`FirmwareUpdateInfo` is a plain DTO class (defined in `UpdateController.cs`), **not an
EF entity**. A `.Select(x => new FirmwareUpdateInfo { ... })` projection materialises
objects that Entity Framework's change tracker knows nothing about. The `foreach` then
assigns `entity.Havuz` and `entity.UpdateInfo` on those detached DTOs — and
`db.SaveChanges()` has no tracked changes to persist. So this loop, whose *intent* is
to bounce stale queued tasks (`UpdateInfo == 1`, `QueueEntryDate` older than 30
minutes) back to the pool, **does nothing at all**. Stale queued firmware tasks are
never actually recovered: they stay `Active`, `Havuz == false`, consuming
`activeFirmwareLimit` slots indefinitely.

For contrast, the pool->queue **promotion** logic earlier in the same method (~lines
452–465) is written correctly — it fetches the real tracked entity
(`db.Device_Confs_Update.FirstOrDefault(u => u.UpdateId == item.UpdateId)`) and
modifies *that*. So promotion works; the stale-bounce silently does not.

### Relevance to this feature
Change 4 (the stuck-`6` recovery) was *originally planned* as a small `else if` added
inside this exact loop. Implemented that way, it would have inherited this same no-op
bug and persisted nothing. That is precisely why Change 4 is instead written as a
separate block that queries the real tables for EF-tracked entities. This feature
therefore works *around* Bug B — it does not fix it, and it does not depend on it
being fixed.

### Why it was NOT fixed here
Fixing it would switch on stale-task recovery behaviour that has been dormant in
production for an unknown period. That is a real fleet-behaviour change and deserves
its own canary — the same rationale as Bug A. Per the user's decision (2026-05-14),
it is a separate, deliberate fix.

### Recommended fix
Rewrite the loop to operate on tracked entities: query `db.Device_Confs_Update` /
`db.MainUpdate` directly (not through the `FirmwareUpdateInfo` projection), modify the
returned entities, and let `SaveChanges()` persist them — following the pattern the
promotion logic in the same method already uses. Mind the `UpdateId` vs
`MainUpdateId` disambiguation: the projection conflates the two tables' primary keys
into one field, so the rewrite must keep the two tables separate (as Change 4 does).

### Found by
Gemini, during the independent review of the C#-backend changes for this feature.

---

## Related documents
- `ota-visibility-handoff.md` — per-repo diffs and the git playbook for handing the
  four changes to the server team.
- Auto-memory entries: `project_ota_visibility_feature` (the feature),
  `project_deferred_ota_sql_pool_close` (Bug A), `project_deferred_firmwarepool_stale_loop`
  (Bug B).
