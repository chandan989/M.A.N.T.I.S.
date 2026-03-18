# M.A.N.T.I.S. Design System: The Operator Terminal

## 1. Core Philosophy: The Operator Terminal

- **Monospace-Only**: Every single character, space, and UI element is tied to a strict grid.
- **Text as UI**: No SVGs, no drop shadows, no border-radius. Borders, buttons, and progress bars are constructed entirely from ASCII/ANSI text characters.
- **High Contrast / Zero Glare**: Pure black backgrounds with bright, phosphor-like text.
- **Raw Execution**: The interface should feel like a direct pipe into the Hedera network. Transitions are non-existent; data snaps into place.

## 2. Color Palette (Phosphor Matrix)

We retain the M.A.N.T.I.S. insectoid brand identity (Purples/Magentas) but adapt it for high-contrast terminal legibility.

### Base Canvas
- **Terminal Black**: `#000000` — Absolute true black. No gradients.
- **Scanline Dim**: `#120E1A` — Used sparingly for alternating table rows.

### Text & Data
- **Phosphor Purple**: `#B072FF` — The primary text color for logs, data, and active states.
- **Dimmed Violet**: `#4A3B5C` — Used for borders, grid lines, and inactive parameters.
- **System White**: `#E0DCE6` — High-contrast text for critical numbers (e.g., APY, Wallet Balance).

### System Alerts
- **Critical Magenta**: `#FF2A85` — Used for `[ ERR ]`, bearish sentiment, or emergency withdrawals.
- **Success Cyan**: `#00F0FF` — Used for transaction hashes and `[ OK ]` statuses.

## 3. Typography

The entire system relies on a single font family to maintain the grid.

- **Primary Font**: JetBrains Mono, Fira Code, or VT323.

### Styling
- Never use bold or italic. Use color to create visual hierarchy.
- **Line height**: 1.2 to 1.4 (keep it tight).
- **Letter spacing**: 0 (monospaced handles this naturally).

## 4. UI Component Library (Text-Based)

### Headers & Titles
Instead of graphic headers, use ASCII art banners or bracketed text.

```plaintext
╔════════════════════════════════════════════════════════════╗
║ M.A.N.T.I.S. // MARKET ANALYSIS & TACTICAL INTEGRATION SYS ║
╚════════════════════════════════════════════════════════════╝
```

### Borders & Containers
Use extended ASCII box-drawing characters for clean, single-line or double-line panels.

```plaintext
┌─ [ SENTRY SKILL ] ────────────────┐
│ STATUS    : [ ACTIVE ]            │
│ SENTIMENT : -0.72 (BEARISH)       │
│ TARGET    : HBAR/USDC             │
└───────────────────────────────────┘
```

### Buttons & Interactions
Buttons are indicated by square brackets or angle brackets. Hover states are represented by an inverted background (black text on solid purple block) or a prefixed cursor `>`.

- **Inactive**: `[ HARVEST REWARDS ]`
- **Hover/Focus**: `>[ HARVEST REWARDS ]<`
- **Active**: `[██HARVESTING...██]`

### Progress Bars & Meters
Data visualization uses block characters (`█`, `▓`, `▒`, `░`) or standard ASCII (`#`, `-`).

```plaintext
VOLATILITY : [████████░░░░░░░░] 50%
RISK LVL   : [####------] MODERATE
```

### Status Tags
Always bracketed, always fixed width for perfect column alignment.
- `[  OK  ]` (Cyan)
- `[ WARN ]` (Yellow/Magenta)
- `[ FAIL ]` (Magenta)
- `[ IDLE ]` (Dimmed Violet)

## 5. Layout & Spacing Principles

- **Strict Columns**: Emulate an 80-column or 120-column terminal width. Limit the max-width of the central content to maintain the illusion of a retro CRT monitor.
- **White Space is Black Space**: Use empty lines to separate logic blocks instead of borders.
- **Data Tables**: Align everything to the character grid.

```plaintext
TX HASH       ACTION         STATUS     VALUE
---------------------------------------------------------
0x8f9c...4a2b WIDEN_RANGE    [  OK  ]   $1,204.50
0x3b1a...9c2d HARVEST_SWAP   [  OK  ]   $42.10
0x7e4f...1a5b DEPOSIT        [ WARN ]   ---
```

## 6. Animation & Effects

Minimalist terminal UIs shouldn't be static, but they shouldn't be smooth either.

- **Blinking Cursor**: A constant `_` or `█` blinking at 1Hz at the end of the active log line.
- **Typewriter Reveal**: Instead of fading in, new components or log entries print to the screen character-by-character (fast, e.g., 10ms per character).
- **Scanline Overlay**: A very faint, purely CSS-based horizontal scanline effect that crawls down the screen slowly to simulate CRT refresh rates, without blurring the sharp text.
- **Hard Toggles**: When a modal opens or a view switches, it instantly replaces the characters on screen—no slides, no fades. Clear the buffer, print the new buffer.

## 7. Advanced GUI Components

### Tabbed Navigation
Use extended box-drawing characters to create connected tabs. The active tab physically connects to the panel below it, while inactive tabs remain closed off.

```plaintext
  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ DASHBOARD│ │ VAULT OP │ │  SKILLS  │ │  SYSTEM  │
┌─┘          └─┴──────────┴─┴──────────┴─┴──────────┴────────┐
│                                                            │
│ > INITIALIZING DASHBOARD VIEW...                           │
```

### Modals & Overlays (With "Drop Shadows")
To create depth in a purely 2D terminal, use solid block characters (`█`) offset to the bottom right of a standard box to simulate a heavy drop shadow.

```plaintext
┌──────────────────────────────────────────┐
│ [!] MANUAL OVERRIDE AUTHORIZATION        │
├──────────────────────────────────────────┤
│ WARNING: Triggering an early harvest     │
│ bypasses the 2H minimum interval guard.  │
│                                          │
│ Target: BONZO_VAULT_0.0.1234567          │
│ Action: HARVEST_AND_SWAP                 │
│                                          │
│         [ CANCEL ]      >[ EXECUTE ]<    │
└──────────────────────────────────────────┘██
  ████████████████████████████████████████████
```
*Color Coding*: The modal border is Critical Magenta, the text is System White, and the drop shadow (`█`) is Dimmed Violet to fade into the background.

### Toggles, Radios, and Switches
Instead of standard HTML checkboxes, use bracketed structural elements to represent state.

**Binary Toggles (Switches)**:
```plaintext
SENTRY OVERRIDE : [███|   ] ON
SAFE MODE       : [   |███] OFF
AUTO-REBALANCE  : [███|   ] ON
```

**Radio Buttons (Mutually Exclusive)**:
```plaintext
RISK PROFILE:
( ) CONSERVATIVE  [ Max Vol: 0.35 ]
(x) MODERATE      [ Max Vol: 0.60 ]
( ) AGGRESSIVE    [ Max Vol: 0.90 ]
```

### Sparkline Charts (Data Visualization)
For APY history or volatility tracking, use Unicode block elements (` `, `▂`, `▃`, `▄`, `▅`, `▆`, `▇`, `█`) to create inline graphs that fit precisely within the text grid.

```plaintext
24H REALIZED VOLATILITY [SUPRA ORACLES]
1.00 ┤                                █
0.75 ┤        ▅▆▇██▇▆▅             ▅▆█
0.50 ┤  ▃▄▅▄▃          ██       ██▃██
0.25 ┤▂▃▄▃▂▃▄█           █▄▂ ▂▄█     ███
0.00 ┼─────────────────────────────────
     -24H      -18H      -12H       NOW
```
*Color Coding*: The graph bars (`█`) are Phosphor Purple. Spikes above 0.80 turn Critical Magenta.

### Scrollable List Areas
When the agent logs exceed the viewable area, include a dedicated, visual scrollbar on the right edge of the panel using shaded blocks (`▓`, `▒`, `░`).

```plaintext
┌─ [ EXECUTION LOG ] ───────────────────────┬─┐
│ 11:14:02 > SENSE: Pulling Sentry Data...  │▲│
│ 11:14:05 > SENSE: Pulling Oracle Data...  │█│
│ 11:14:08 > THINK: Evaluating context...   │█│
│ 11:14:12 > ACT  : Volatility within limits│▒│
│ 11:14:13 > ACT  : NO_OP                   │░│
│ 11:15:02 > SENSE: Pulling Sentry Data...  │░│
│                                           │▼│
└───────────────────────────────────────────┴─┘
```

### Dropdown / Select Menus
To represent an open dropdown menu, draw a sub-box that overlaps the content below it. The currently hovered item is inverted (represented here by wrapping in `> <`).

```plaintext
TARGET ASSET: [ HBAR/USDC ▼]
              ┌────────────┐
              │  HBAR/USDT │
              │ >HBAR/USDC<│
              │  USDC/USDT │
              └────────────┘
```

### Complex Status Panels (The "Cockpit")
Combining these elements creates a highly technical, dense GUI layout entirely out of text, perfectly fitting the Hedera agent execution environment.

```plaintext
╔════════════════════════════════════════════════════════════╗
║ SYS.MODE: [ACTIVE]                     NET: [MAINNET]      ║
╠════════════════════════════════════════════════════════════╣
║ ┌─[ ORACLE FEED ]──────┐ ┌─[ VAULT STATUS: 0.0.123456 ]──┐ ║
║ │ PAIR: HBAR/USDC      │ │ RANGE: 0.075 - 0.115          │ ║
║ │ PRIC: $0.084         │ │ POSIT: [██████████] IN RANGE  │ ║
║ │ VOLA: 0.82 [WARN]    │ │ APY  : 14.2%                  │ ║
║ │ TREN: ▃▅▇█▇▅▃ [HIGH] │ │ REWRD: $24.50 PENDING         │ ║
║ └──────────────────────┘ └───────────────────────────────┘ ║
║                                                            ║
║ > [ HARVEST ]    [ HARVEST+SWAP ]    [ EMERGENCY WITHDRAW] ║
╚════════════════════════════════════════════════════════════╝
```
