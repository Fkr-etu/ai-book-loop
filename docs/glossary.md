# Glossary

## Author intent

The author's theme, inspiration, idea, lore, and explicit constraints that generation must preserve.

## Canonical

Information accepted as authoritative for continuity. Rejected or transient generated material is not canonical.

## Canonical context

The focused context assembled from authoritative book information and prior accepted material for a generation step.

## Draft

Generated chapter content that has not yet become accepted/canonical content.

## Use case

An explicit application-level business action, such as `GenerateOutline` or `GenerateChapter`.

## Agent

A focused capability that interacts with an LLM, such as writing, reviewing, or summarizing. An agent is not itself a business use case.

## Workflow

The orchestration of multiple steps needed to complete a generation process, particularly the chapter write/review/retry loop.

## Provider

An implementation of the LLM capability used by the application. Gemini is the MVP provider but is intentionally replaceable.

## ADR

Architecture Decision Record: a short, immutable historical record of a significant architecture decision and its consequences.
