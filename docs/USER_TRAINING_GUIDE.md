# ValuAdis User Training Guide (VA-112)

## For Property Valuers

### Getting Started

1. **Registration**: Create an account at the registration page. Your account will be pending until an administrator approves it.
2. **Login**: After approval, log in with your email and password.
3. **Dashboard**: View your valuation activity, property counts, and charts.

### Managing Properties

- **Add Property**: Click "Add Property" and enter address, municipality, property type, and area. You can draw the boundary on the map or enter coordinates.
- **Bulk Import**: Use "Bulk Import" to upload a CSV or JSON file with multiple properties. Required columns: `address`, `municipality`, `property_type`, `area_sqm`.
- **Export**: Export your properties to CSV for reporting.

### Creating Valuations

- **New Valuation**: Select a property and run a valuation. The system calculates market value and taxable value (25% per Proclamation 1365/2025).
- **Override**: Senior valuers and admins can override calculated values with professional judgment (audit trail required).
- **Export Valuations**: Download your valuations as CSV.

### Reports

- **Reports Page**: Generate system, compliance, and summary reports.
- **Export**: Download reports as JSON for records.

---

## For Administrators

### User Management

- **Users Page**: View all users, filter by role/status.
- **Approve Users**: New registrations show "Pending Approval". Click the approve button to activate accounts.
- **Deactivate**: Deactivate users who should no longer have access.

### Audit Log

- **Audit Page**: View audit logs for valuations, user actions, and system events.
- **Filters**: Filter by date, action, or module.

### Settings

- **Valuation Settings**: Default method, market adjustment factor, Proclamation 1365/2025 enforcement.
- **Notifications**: Configure email notifications for approvals and events.
- **Security**: Session timeout, password policy.

### Feedback

- Users can submit feedback via the feedback API. Review feedback to improve the platform.

---

## Quick Reference

| Action | Location |
|--------|----------|
| Register | `/register` |
| Login | `/login` |
| Dashboard | `/dashboard` |
| Properties | `/properties` |
| Valuations | `/valuations` |
| Map | `/map` |
| Reports | `/reports` |
| Users (admin) | `/users` |
| Audit (admin) | `/audit` |
| Settings (admin) | `/settings` |
