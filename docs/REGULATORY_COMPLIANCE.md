# ValuAdis Regulatory Compliance (VA-120)

## Ethiopian Proclamation 1365/2025

ValuAdis implements property valuation in alignment with Ethiopian tax and valuation regulations.

### Taxable Value Calculation

- **Rule**: Taxable value = 25% of market value (Proclamation 1365/2025).
- **Implementation**: `ValuationService.calculate_taxable_value()` enforces this ratio.
- **Override**: Senior valuers may override with documented reason (audit trail).

### Verification Checklist

| Requirement | Status | Location |
|-------------|--------|----------|
| 25% taxable ratio | ✅ Enforced | `valuation_service.py` |
| Audit trail for overrides | ✅ | `audit_logs`, override_reason |
| Compliance report | ✅ | `/api/v1/audit/report/compliance` |
| Data sovereignty | ✅ Config | `DATA_SOVEREIGNTY_REQUIRED` |
| Proclamation flag | ✅ Config | `PROCLAMATION_COMPLIANCE` |

### Configuration

```env
DATA_SOVEREIGNTY_REQUIRED=true
PROCLAMATION_COMPLIANCE=true
```

Production deployment requires these to be `true` (enforced in `app/core/config.py`).

### Compliance Audit Report

The Compliance Audit report (`/api/v1/audit/report/compliance`) provides:

- Total valuations analyzed
- Compliant vs non-compliant count
- Compliance rate by municipality
- Proclamation 1365/2025 adherence summary

### Data Sovereignty

- Data must remain within Ethiopian jurisdiction as configured.
- No automatic data export to external jurisdictions.

---

## Annual Verification

1. Review Proclamation 1365/2025 for any amendments.
2. Update `calculate_taxable_value` if ratio changes.
3. Re-run compliance audit and document results.
4. Update this document with verification date.
