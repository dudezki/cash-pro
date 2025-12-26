# Navigation Structure Documentation

## Overview
The navigation system supports hierarchical navigation with main nav items and sub-navigation. The navigation structure differs based on user type (Super Admin vs Regular User) and is filtered by subscription tier and user role/permissions.

## Super Admin Navigation

```
📊 Dashboard
⚙️ Administration
  ├─ 👥 User Management
  ├─ 🏢 Company Management
  ├─ 💳 Subscriptions
  └─ 🔧 System Settings
📈 Monitoring
  ├─ 📋 System Logs
  ├─ 📊 Metrics
  └─ 🏥 Health Check
🔐 Settings
  ├─ 👤 Roles
  └─ 🔑 Permissions
```

## Regular User Navigation

Navigation is dynamically generated based on:
- **Subscription Tier**: trial, starter, professional, enterprise
- **User Role**: owner, admin, member, viewer
- **Permissions**: Resource-level permissions (e.g., `invoice:read`, `customer:write`)

### Base Navigation (All Users)
```
📊 Dashboard
```

### Financial Management (All Tiers)
```
💼 Financial
  ├─ 📄 Invoices (requires: invoice:read)
  ├─ 👥 Customers (requires: customer:read)
  └─ 💵 Payments (requires: payment:read)
```

### Reports & Analytics
- **Starter+**: Reports
- **Professional+**: Reports, Analytics

```
📊 Reports (Starter+)
  ├─ 📊 Reports
  └─ 📈 Analytics (Professional+)
```

### Advanced Features
- **Professional+**: Projects, Expenses
- **Enterprise**: Projects, Expenses, Inventory

```
⚡ Advanced (Professional+)
  ├─ 📁 Projects
  ├─ 💰 Expenses
  └─ 📦 Inventory (Enterprise only)
```

### Enterprise Features
- **Enterprise Only**: Integrations, API Keys

```
🚀 Enterprise (Enterprise only)
  ├─ 🔌 Integrations
  └─ 🔑 API Keys (Owner/Admin only)
```

### Settings
- **All Users**: Profile
- **Owner/Admin**: Company, Billing, Roles & Permissions

```
⚙️ Settings
  ├─ 👤 Profile (All)
  ├─ 🏢 Company (Owner/Admin)
  ├─ 💳 Billing (Owner/Admin)
  └─ 🔐 Roles & Permissions (Owner/Admin)
```

## Navigation Filtering Rules

1. **Subscription-based**: Items with `requiresSubscription` are only shown if user's subscription tier matches
2. **Role-based**: Items with `requiresRole` are only shown if user's role matches
3. **Permission-based**: Items with `requiresPermission` are only shown if user has the permission
4. **Parent hiding**: If all children of a parent item are filtered out, the parent is also hidden

## Example Navigation by Scenario

### Scenario 1: Starter Plan, Admin Role
```
📊 Dashboard
💼 Financial
  ├─ 📄 Invoices
  ├─ 👥 Customers
  └─ 💵 Payments
📊 Reports
  └─ 📊 Reports
⚙️ Settings
  ├─ 👤 Profile
  ├─ 🏢 Company
  ├─ 💳 Billing
  └─ 🔐 Roles & Permissions
```

### Scenario 2: Professional Plan, Member Role
```
📊 Dashboard
💼 Financial
  ├─ 📄 Invoices
  ├─ 👥 Customers
  └─ 💵 Payments
📊 Reports
  ├─ 📊 Reports
  └─ 📈 Analytics
⚡ Advanced
  ├─ 📁 Projects
  └─ 💰 Expenses
⚙️ Settings
  └─ 👤 Profile
```

### Scenario 3: Enterprise Plan, Owner Role
```
📊 Dashboard
💼 Financial
  ├─ 📄 Invoices
  ├─ 👥 Customers
  └─ 💵 Payments
📊 Reports
  ├─ 📊 Reports
  └─ 📈 Analytics
⚡ Advanced
  ├─ 📁 Projects
  ├─ 💰 Expenses
  └─ 📦 Inventory
🚀 Enterprise
  ├─ 🔌 Integrations
  └─ 🔑 API Keys
⚙️ Settings
  ├─ 👤 Profile
  ├─ 🏢 Company
  ├─ 💳 Billing
  └─ 🔐 Roles & Permissions
```

### Scenario 4: Trial Plan, Viewer Role
```
📊 Dashboard
💼 Financial
  ├─ 📄 Invoices
  ├─ 👥 Customers
  └─ 💵 Payments
⚙️ Settings
  └─ 👤 Profile
```

## Implementation Notes

- Navigation is generated client-side using `getUserNavigation()` or `getSuperAdminNavigation()`
- Items are filtered using `filterNavigationByAccess()` based on user context
- User context (subscription, role, permissions) is loaded in `AuthenticatedLayout`
- Currently uses mock data - needs to be replaced with actual API calls:
  - Subscription tier from `/api/subscriptions/current`
  - User role from `/api/auth/me` (needs to be added)
  - Permissions from `/api/rbac/user-permissions` (needs to be created)

