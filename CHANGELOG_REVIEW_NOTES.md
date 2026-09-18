# IBVAP Tactical Command Center - Engineering Review & Change Notes

This document provides a detailed breakdown of all changes made to the IBVAP frontend codebase to resolve login flow issues, input/dropdown contrast failures, and desktop/laptop command center layout constraints.

---

## 📋 Summary of Issues Resolved

| # | Reported Issue | Root Cause | Resolution | Impacted Files |
|---|---|---|---|---|
| **1** | **App pre-logged in by default; Login/Signup not shown** | In `App.jsx`, `loggedIn` was hardcoded to `true` (`useState(true)`). In addition, `Login.jsx` lacked navigation to `Register.jsx`, and `Register.jsx` had an incomplete submit handler without backend signup connection. | Default `loggedIn` set to `false`. Added bidirectional routing between Login and Register views. Connected real Node.js auth endpoints (`/api/auth/login` and `/api/auth/signup`) while retaining the 1-click Quick Demo bypass. | `App.jsx`, `pages/login.jsx`, `pages/register.jsx` |
| **2** | **Clickables (gender dropdown, inputs) turn white / invisible on click** | `index.css` had `:root { color-scheme: light dark; }`. On Windows Chromium in dark mode, browser form controls inverted text. The `.input-group select` had `background: white` without setting `color: #111827`, and `<option>` elements lacked explicit foreground/background colors. Form autofill also lacked dark text overrides. | Forced `color-scheme: light !important;` on `.login-card` and form controls. Set explicit `#ffffff` backgrounds and `#0f172a` text colors on all `input`, `select`, and `option` elements. Styled `<select>` with custom SVG arrow, padding, and focus rings. Added autofill box-shadow override. | `App.css`, `index.css`, `pages/register.jsx` |
| **3** | **App layout not optimized for laptop/desktop screens** | Default Vite template styles in `index.css` constrained `#root` to `width: 1126px`, centered text alignment, and added vertical side borders. Camera video feeds were hardcoded to a tiny `180px` height. | Removed `1126px` restriction and Vite boilerplate. Established a 100vw full-screen military tactical command center layout: fixed 270px left navigation rail, top telemetry bar with live Zulu clock & DEFCON pill, 4-card KPI strip, 16:9 widescreen primary AI YOLOv8 monitor, interactive camera switcher, and right-rail live PostgreSQL alert registry with microservices health matrix. | `index.css`, `App.jsx`, `App.css` |

---

## 🔍 Detailed File Modifications

### 1. `src/index.css` & `pritams-frontend/src/index.css`
- **Removed**:
  - Vite default `#root { width: 1126px; max-width: 100%; margin: 0 auto; text-align: center; border-inline: 1px solid var(--border); }`
  - Unused Vite demo rules (`.counter`, `#social`, etc.)
- **Added**:
  - Full-viewport base reset: `html, body, #root { width: 100%; min-height: 100vh; margin: 0; padding: 0; text-align: left; }`
  - Dark tactical background `#0c121e` and high-contrast font stack with Apple/Segoe/Roboto system fonts.

### 2. `src/App.jsx` & `pritams-frontend/src/App.jsx`
- **State Changes**:
  - `loggedIn`: Initialized to `false` (previously `true`).
  - `page`: Initialized to `"login"`.
  - Added `activeCameraId` (default `1`) to allow switching any camera into the primary high-definition viewport.
  - Added `viewMode` toggle: `"featured"` (primary 16:9 viewport + secondary strip) or `"quad"` (2x2 quad camera grid).
  - Added `alertFilter` (`"all"`, `"critical"`, `"warning"`).
  - Added `militaryTime` live clock updating every second (Local Time + Zulu / UTC).
- **Authentication Flow**:
  - If `!loggedIn`: Routes to `<Login>` or `<Register>` based on `page`.
  - `Login` receives `onLogin` and `onRegister` callbacks.
  - `Register` receives `onLogin` and `onRegisterSuccess` callbacks.
  - Sidebar and top header both provide clean "Sign Out" actions that reset `loggedIn = false`.
- **Surveillance Experience**:
  - Primary viewport displays Camera 01's live WebSocket AI YOLOv8 feed (`ws://localhost:8080/stream`) in widescreen aspect ratio with radar loader when connecting, HUD reticle corners, FPS counter, resolution, and model info.
  - Interactive secondary feeds strip: clicking any of the 4 cameras instantly promotes it to the primary viewport.
  - 4-way Quad Grid mode for operators monitoring all sectors simultaneously.
  - Right panel displays live PostgreSQL alert registry with confidence meters and snapshot thumbnail support, plus a 4-microservice architecture health monitor.

### 3. `src/pages/login.jsx` & `pritams-frontend/src/pages/login.jsx`
- **Added `onRegister` Navigation**: Added a "Register / Create Account" link button allowing operators to switch views.
- **Backend API Integration**: Connects to `POST http://localhost:5000/api/auth/login`. If the Node.js API is offline, presents an informative alert and highlights the Quick Demo button.
- **Quick Demo Bypass**: "⚡ Quick Demo Access (Bypass Login)" allows instant entry as Major General (Admin) without requiring backend services to be started during testing.
- **Form Controls**: Added `id`, `htmlFor`, and standard `autoComplete` attributes.

### 4. `src/pages/register.jsx` & `pritams-frontend/src/pages/register.jsx`
- **Backend API Integration**: Replaced empty stub with real `POST http://localhost:5000/api/auth/signup`.
- **Client-Side Validation**: Checks passcode length (minimum 6 characters) and verifies password match before network submission.
- **Gender Dropdown Contrast**: Wrapped `<select>` in `.select-wrapper` and enforced `color-scheme: light` with explicit white background and dark text on `<option>` items.
- **Success & Error Feedback**: In-line alert banners for error messages and success redirection.

### 5. `src/App.css` & `pritams-frontend/src/App.css`
- **Fixed CSS Syntax Error**: Fixed `color: rgb(229, 217, 217), 217);` in root `src/App.css`.
- **Fix for Dropdown & Input Contrast (Issue 2)**:
  - Enforced `color-scheme: light !important;` on `.login-card`.
  - Explicitly set `background-color: #ffffff !important;` and `color: #0f172a !important;` on `.input-group input`, `.input-group select`, and `.input-group select option`.
  - Replaced browser-default select chevron with high-contrast custom SVG arrow.
  - Added `-webkit-autofill` box-shadow override to stop Chrome from washing out form text.
  - Applied focus rings (`box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15)`).
- **Tactical Command Center Architecture (Issue 3)**:
  - Responsive two-column grid (`minmax(0, 1.85fr) minmax(360px, 1.15fr)`).
  - Sticky full-height tactical sidebar with telemetry status box and radar pulse animations.
  - 16:9 widescreen primary monitor with HUD reticle corners, crosshair, and telemetry badges.
  - Secondary feeds strip with active glow indicator.
  - Sleek alert cards with confidence gauge bars and scrollable list.
  - Microservices matrix displaying live health of Go Broadcaster (`:8080`), Python AI (`:8000`), Node.js (`:5000`), and PostgreSQL (`:5432`).

---

## 🧪 Verification & Build Status

Both builds were executed and validated with 0 errors:
- **`pritams-frontend`**: Vite build completed successfully in `376ms`.
- **Root `SIH-TensorTribe`**: Vite build completed successfully in `1.13s`.
