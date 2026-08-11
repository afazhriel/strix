# Strix Windows Compatibility

## 1. Purpose

Strix has been optimized for native Windows host-side operation. General Strix
functionality — the CLI, configuration, LLM integration, authentication,
target preparation, report generation, the local viewer, telemetry, skills, and
the interactive TUI — runs directly on Windows without requiring Docker.

Docker is only needed for the autonomous, sandboxed pentest engine itself, and
that dependency is architectural and intentional (see
[Docker-Dependent Features](#6-docker-dependent-features) and
[Security Boundary](#8-security-boundary)).

## 2. Environment Verified

- **Windows** host
- **Python 3.12.10**
- **uv** (package/dependency management)
- **Strix 1.5.2**
- **Docker intentionally unavailable** during verification
- **Virtualization intentionally disabled**

Verification was performed without Docker and without virtualization, so the
native Windows host-side surface could be confirmed independently of the
container runtime.

## 3. Windows-Native Capabilities

The following Strix capabilities run natively on Windows:

- **CLI / configuration** — argument parsing, environment validation
  (`STRIX_LLM`, `LLM_API_KEY`, provider/API-base aliases, Perplexity key),
  and persisted settings under `~/.strix/cli-config.json`.
- **LLM / LiteLLM** — provider-agnostic model routing, model settings,
  reasoning effort, prompt caching, streaming controls, timeouts, conversation
  compaction, and context/token budgeting.
- **Codex OAuth** — `strix auth login chatgpt` performs OAuth 2.0 + PKCE
  against auth.openai.com with a localhost callback; tokens are stored
  separately from the CLI config.
- **Target preparation** — target-list files, local-source collection, repo
  cloning, diff-scope resolution, and OpenAPI/Swagger/Postman API-spec
  detection (Postman collections are fetched on the host so API keys never
  enter the sandbox).
- **Reports** — vulnerability and dependency findings, executive summaries,
  deduplication, CVSS, and per-agent LLM usage/cost ledgers.
- **SARIF / JSON / Markdown / PDF** — SARIF 2.1.0 (GitHub code-scanning
  compatible), `vulnerabilities.json`, Markdown vulnerability files and
  executive reports, and AES-256 encrypted PDF reports (password generated
  locally and never leaves the machine).
- **Viewer / authentication** — `strix view` serves the local SPA from a
  standard-library HTTP server, and the email-verification / encrypted-report
  relay used by the viewer.
- **Telemetry** — opt-in usage telemetry and update checking run on the host.
- **Skills** — bundled knowledge packs (`strix/skills`) load natively.
- **TUI** — the interactive Bubble Tea TUI ships as a Windows binary
  (`strix-tui.exe`) bundled in every `win_amd64` wheel and in the frozen
  `strix.exe`; on Windows it authenticates its IPC connection over loopback
  with a per-launch token.

## 4. Windows Compatibility Improvements

Commit `c1f21d9` ("fix: improve Windows compatibility and sandbox UX")
delivered the following changes:

- **Platform-aware POSIX 0600 tests** — file-permission tests account for the
  fact that POSIX mode bits are not meaningful on Windows; secret-file writing
  still uses write-temp-then-replace on Windows.
- **Windows system-tree mount protection** — the bind-mount guard rejects
  `SystemRoot` and `Program Files` as mount sources, in addition to forbidden
  Windows tree names and the user profile.
- **Windows home/root handling** — drive-root and home-directory targets are
  refused consistently, so the agent can never be mounted over the whole
  Windows filesystem or the user's home.
- **Case-insensitive local target deduplication** — `C:\Repo` and `c:\repo`
  resolve to one bind mount on Windows instead of two mounts of the same tree.
- **Windows path normalization** — local target paths are canonicalized before
  comparison so equivalent spellings of the same directory deduplicate.
- **POSIX workspace mount targets** — workspace subdirectories are converted
  to POSIX paths (`/workspace/<subdir>`) before binding, which is what the
  Linux sandbox expects.
- **Clean Docker-unavailable UX** — when the Docker CLI or daemon is
  unavailable, Strix prints a clear "DOCKER SANDBOX UNAVAILABLE" panel with
  platform-specific next steps (start Docker Desktop on Windows,
  `docker info` to confirm) instead of a stack trace, and exits cleanly.
  The message explicitly states that Strix itself is installed and
  functioning and lists available host-side features.
- **Docker availability tests** — `tests/test_environment_docker.py` covers
  CLI-missing, daemon-down, and platform-specific message cases.

## 5. Verification

- **881 passed**
- **7 skipped**
- **0 failed**

The skipped tests are platform-specific and intentional (for example, tests
that only apply on a POSIX host or that require a running Docker daemon). A
clean run confirms the Windows host-side surface and the Windows-specific
improvements above.

## 6. Docker-Dependent Features

These remain **Docker-required by design** and cannot run without the sandbox:

- **Autonomous agent sandbox** — the pentest agent runs as an SDK
  `SandboxAgent` inside a container; the runtime registers a Docker sandbox
  backend only.
- **Shell execution inside the sandbox** — all terminal/tool commands run
  inside the container, never on the host.
- **Browser agent** — the agent-driven browser runs inside the sandbox
  (Chromium is installed in the sandbox image).
- **Kali security toolchain** — nmap, sqlmap, nuclei, ffuf, subfinder, naabu,
  httpx, katana, gospider, trivy, gitleaks, trufflehog, semgrep, and the rest
  are installed only in the Kali-based sandbox image.
- **Caido proxy** — the interception proxy runs as an in-container sidecar;
  the agent's traffic flows through it inside the sandbox.
- **Sandboxed local-source scanning** — local code and repositories are
  bind-mounted into the container and scanned from inside it.
- **Dependency/security scanning performed inside the sandbox** —
  dependency-CVE and SAST-style scanning execute in the container.

## 7. No-Docker Alternative

When Docker is unavailable, **Strix Managed Cloud** (app.strix.ai) is the
alternative for full sandboxed pentesting. The sandbox-unavailable message in
Strix lists it as an option, along with starting Docker Desktop and continuing
to use host-side Strix functionality. Managed cloud is covered by the
documentation and install scripts in this repository; no additional API
endpoints, pricing, or features beyond those are claimed here.

## 8. Security Boundary

- Strix does **not** replace Docker with Windows host subprocess execution.
- The LLM agent must **never** receive unrestricted Windows host shell access
  as a Docker fallback.
- Mount restrictions remain enforced — system trees, the Windows root, and the
  user's home/profile are refused as mount sources.
- The **Docker sandbox remains the security boundary** for autonomous
  pentesting. Everything the agent can execute, browse, or scan stays inside
  that boundary; the host only runs the orchestration, configuration, and
  reporting layers.

## 9. Current Status

> Strix is sufficiently optimized for Windows host-side operation without
> Docker. The remaining Docker dependency is architectural and intentional.

Relevant commit:
[`c1f21d9`](https://github.com/usestrix/strix/commit/c1f21d9)
`fix: improve Windows compatibility and sandbox UX`
