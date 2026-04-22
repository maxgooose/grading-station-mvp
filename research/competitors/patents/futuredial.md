# Patent: FutureDial — Enhanced Automatic Cosmetic Grading

**Patent:** US20200242751A1
**Title:** Enhanced automatic cosmetic grading
**Assignee:** Future Dial Inc.
**Link:** https://patents.google.com/patent/US20200242751A1/en

## Overview

87+ figures. Primarily a software/workflow patent, not a hardware teardown.

## What It Covers

### Software/Workflow (primary focus)
- QR-code identification of devices
- Data transfer and device-to-robot handoff protocols
- Grading criteria and decision logic
- Integration with inventory management systems

### Hardware (minimal detail)
- References "high-speed scanning cameras"
- References "diverse lighting"
- No detailed camera positioning, lighting type, or gripper/flip mechanism

## What It Doesn't Cover

- Camera count, model, or resolution
- Lighting specifics (LED type, polarization, diffusion)
- How the device is physically flipped or rotated
- Gripper/holder design
- Enclosure dimensions or layout

## Relevance To Our Project

Low hardware value, moderate software value:
- The workflow logic (QR identification → scan → grade → route) maps to our planned software pipeline
- Integration patterns for pushing grades to an inventory system (relevant to our WholeCellIO API integration)
- Shows that FutureDial treats the grading workflow as a software-first problem with hardware as the implementation detail

## Source

- https://patents.google.com/patent/US20200242751A1/en
