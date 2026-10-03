# Usage Guide

Start by addressing which system you intend to work within:

1. **Developing new indicators/strategy algorithms?**
Navigate to `matsaya/` and evaluate changes in isolated Test-Driven development cycles. Run tests via `pytest`.

2. **Connecting execution engine logic?**
Access `.planning/codebase/ARCHITECTURE.md` to map `new_system/` objects. Build connections within the object-oriented abstractions.

3. **Generating ML Features / Models?**
Work extensively within `sandwich/steps/`. Always read `varaha_data.duckdb` iteratively over chronological stage execution.