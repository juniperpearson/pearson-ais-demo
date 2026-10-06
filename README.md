# Pearson AIS Protocol v2.0 — Minimal Runtime Demo

A lightweight Python reference implementation demonstrating selected runtime-authority semantics from the Pearson Alignment Integrity Systems (AIS) Protocol v2.0.

> **Capability is not authority.**

AIS models autonomous execution authority as conditional, revocable, bounded, and externally governed.

## What This Demo Shows

The simulation follows one intentionally simple failure-and-recovery scenario:

```text
Valid Execution Lease
        ↓
Actor requests prohibited action
        ↓
Layer B hard veto
        ↓
Logical Zero containment
        ↓
Authority Epoch advances
        ↓
Old Execution Lease rejected
        ↓
Fault condition clears
        ↓
Authority remains revoked
        ↓
Layer C restoration eligibility
        ↓
D_R post-containment revalidation
        ↓
Fresh current-epoch ELO
        ↓
Guarded LeaseCommit
        ↓
Authority restored