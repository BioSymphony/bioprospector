---
date: 2026-05-26
slug: example-doctor-warnings-vs-failures
applies-to: any-campaign
---

# Example: doctor WARN rows are not blockers

This file is a template. Copy its shape when you write a real memory note
under `.bioprospector-memory/YYYY-MM-DD-<slug>.md`. Do not include secrets,
private paths, campaign-specific data, raw sequences, provider identifiers,
or signed URLs in a memory note.

## What happened

A new operator ran `bioprospector_doctor.py` on a fresh checkout and read
the `WARN optional tool not found` lines as build failures. They asked the
agent to install BLAST, HMMER, and DIAMOND before any planning work could
start.

## What was tried

The agent attempted system installs through homebrew, hit a permissions
prompt, and burned roughly ten minutes before stopping.

## What worked

Re-reading the doctor output more carefully. Only `FAIL` rows block local
work. `WARN optional` rows are informational: those tools are only needed
when a provider lane is approved, not for local-first planning. The agent
restored progress by skipping the installs and going to preflight.

## When this applies

Any first agent run on a new machine. Surface the WARN-vs-FAIL distinction
when summarizing the doctor output so the operator does not request
unneeded installs.

## What to skip

This is an agent-process lesson. It does not validate biology, does not
change the heavy-data policy, and is not a substitute for provider
preflight when a lane is actually approved for live execution.
