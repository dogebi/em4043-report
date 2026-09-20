# Scroll Dot Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a hidden-until-scroll, right-side section dot navigation to the EM4043 report.

**Architecture:** Extend the existing standalone HTML with one fixed navigation rail, generated from the report's existing section IDs. Use `IntersectionObserver` for active-section tracking and a scroll listener for show/hide state; no new dependency or component framework is needed.

**Tech Stack:** HTML, CSS, vanilla JavaScript, IntersectionObserver.

---

### Task 1: Add the navigation markup and styles

**Files:**
- Modify: `em4043-report/EM4043-工单管理助手汇报.html` in the existing `<style>` block and immediately after `<body>`.

- [x] Add a fixed `.section-rail` containing links for `overview`, `architecture`, `business-scenarios`, `scenarios`, `management`, `comparison`, `progress`, `challenges`, and `future`.
- [x] Style the rail as hidden by default with `opacity: 0` and `transform: translateY(10px)`, and reveal it with `.section-rail.is-visible`.
- [x] Keep the rail hidden at viewport widths below 900px so it does not reduce mobile reading width.
- [x] Add `.section-dot.is-active` styling and accessible link labels.

### Task 2: Add scroll behavior and active-section tracking

**Files:**
- Modify: `em4043-report/EM4043-工单管理助手汇报.html` in the existing `<script>` block.

- [x] On scroll, reveal the rail when `window.scrollY > 120` and hide it at the top.
- [x] Use `IntersectionObserver` with the existing section IDs to toggle the active dot.
- [x] Preserve smooth anchor scrolling and support `prefers-reduced-motion` by using instant scrolling when motion reduction is enabled.
- [x] Keep the existing TOP button behavior unchanged.

### Task 3: Verify and synchronize

**Files:**
- Modify: `D:\dev\cscAI\dogebi.github.io-sync\em4043-report\EM4043-工单管理助手汇报.html` with the same final report content.

- [x] Run `git diff --check` in both repositories.
- [x] Verify all nine section IDs have matching rail links and the rail starts hidden.
- [x] Commit and push the source repository.
- [x] Commit and push the GitHub Pages repository.
