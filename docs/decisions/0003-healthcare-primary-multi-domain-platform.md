# ADR 0003 — Healthcare-primary multi-domain platform

Status: accepted design, implemented foundation only (Macro Milestone 1).

Decision: retain the approved South German Credit code and baseline as secondary benchmark; add UCI 296 healthcare policy under `domains/healthcare` and evolve toward shared experiment/XAI/serving use cases only where both domains prove the need. Context: the original vision named credit first, and approved phases built it; the supervised flagship now requires healthcare without discarding tested work. Alternatives: replace credit code, fork a second application, or immediately generalize every module. The chosen boundary preserves regression evidence and avoids premature abstractions. Trade-off: the older credit package path is not symmetrical; migration can be considered if a true shared interface emerges. Reconsider when both domains have working model/serving implementations. Credit changes require their own authorization.
