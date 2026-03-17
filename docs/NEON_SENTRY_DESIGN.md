# Neon Sentry Design System

This document outlines the "Neon Sentry" Design System, mapped directly to the Claw-Fi architecture.

## 🎨 1. Color Palette (The "Neon Sentry" Theme)

The visual identity relies on a void-like background punctured by highly saturated, aggressive neon accents and grounded by cold, metallic greys.

*   **Background Base (Void Black)**: `#050505`
    *   *Usage*: The absolute background of your application or terminal interface.
*   **Surface / Panels (Cyber Metal)**: `#1A1B26` to `#24283B`
    *   *Usage*: Card backgrounds for your "Agent Runtime" and "Skills Layer" modules.
*   **Primary Accent (Synthetic Purple)**: `#8A2BE2` (Hex matching the outer mechanical horns)
    *   *Usage*: Primary buttons, active states, and borders for the "Core Agent Runtime."
*   **Secondary Accent (Overdrive Magenta)**: `#FF007F` (Hex matching the inner visor and geometric lines)
    *   *Usage*: Warning states, critical alerts (like the "whale just dumped HBAR" message), and connecting lines in your architecture diagrams.
*   **Text / Typography (Terminal White)**: `#E2E8F0`
    *   *Usage*: Primary body text. Use a muted grey (`#94A3B8`) for secondary text to keep the contrast high for the neons.

## 🔤 2. Typography

To match the precision of the geometric lines and the robotic nature of the agent, avoid rounded or traditional serif fonts.

*   **Display & Headers**: Orbitron or Rajdhani (Google Fonts)
    *   *Vibe*: Squared-off, technical, and aggressive. Use this for Layer titles (e.g., `[ THE SKILLS LAYER ]`).
*   **Body & Data/Logs**: Space Mono or JetBrains Mono
    *   *Vibe*: Developer-centric, terminal-style legibility. Perfect for the APY percentages, Vault states, and the messaging-first UI text.

## 📐 3. UI Components & Geometry

The design uses a lot of intersecting lines, circles, and triangles. We translate this into the following UI elements:

*   **Borders & Cards**: No rounded corners. Use sharp, `0px` border-radius containers. Give them a `1px` solid border of Cyber Metal, which glows Synthetic Purple on hover.
*   **Data Nodes (The Circles)**: When visualizing the "Skills Layer" (Sentry, Oracle, Hedera), represent them as circular nodes connected by `1px` Overdrive Magenta lines.
*   **Glow Effects (Box Shadows)**: For active processes (like the Sentry looping every 60 seconds), use a pulsing drop-shadow in Overdrive Magenta: `box-shadow: 0 0 10px rgba(255, 0, 127, 0.5);`.

## 🏗️ 4. Applying the Design System to your Architecture

Here is how your specific architecture transforms using these visual rules:

### Layer 1: User Interface (Messaging-First)
*   **Visual Execution**: A terminal-style chat interface.
*   **Agent Messages**: Displayed in a card with a Cyber Metal background and a `2px` left-border of Overdrive Magenta.

*   **Mockup styling**:
    ```text
    [ SENTRY ALERT ] 🔴
    "Hey, a whale just dumped HBAR. I preemptively narrowed your Bonzo Vault range to minimize impermanent loss. Current APY: 14%. Reply 'withdraw' if you want out."
    ```

### Layer 2: The Core Agent Runtime
*   **Visual Execution**: The "Brain." This should be the visual center of your dashboard.
*   **Components**: Split into two sharp-edged rectangular panels.
    *   *Memory & Context*: Muted Terminal White text.
    *   *Reasoning Engine*: Framed with a glowing Synthetic Purple border to indicate active processing.

### Layer 3: The Skills Layer (Plugins)
*   **Visual Execution**: A grid of hexagonal or sharp-square cards.
*   **Sentry Skill / Oracle Skill / Hedera Skill**: Each skill acts as a "node." When the Sentry Skill detects a Twitter sentiment shift, a `1px` Overdrive Magenta line should animate, connecting it to the Hedera Skill card to visually represent the execution path.

### Layer 4: On-Chain Layer
*   **Visual Execution**: The foundation. Dark, heavy, and solid. Use deep Void Black with dark grey text to represent the immutable base layer of Hedera Mainnet, Bonzo Vaults, and SaucerSwap pools.

## 💡 The "Claw-Fi" Advantage in UI

When pitching this, your UI should reflect your competitive advantage:

1.  **Invisible Complexity**: Keep the main screen essentially empty except for the "Chat" interface. This proves your point: Nobody wants to stare at a dashboard.
2.  **The "Under the Hood" Toggle**: Add a button labeled `[ X-RAY VIEW ]` in Synthetic Purple. When clicked, it visually reveals the complex Core Agent and Skills Layers running in the background, proving the local-execution autonomy.
