---
name: Streamlit workflow startup
description: Environment-specific startup settings needed for unattended Streamlit previews.
---

Streamlit workflows should run with headless mode enabled and usage-stat collection disabled so first launch does not pause for the interactive onboarding email prompt.

**Why:** Without these flags, the managed workflow can wait indefinitely for terminal input instead of opening its configured web port.

**How to apply:** Include `--server.headless true --browser.gatherUsageStats false` in the workflow command for Streamlit apps.