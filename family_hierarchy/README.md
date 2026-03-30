# Family Hierarchy Management System
**Odoo Module** | Version 16.0.1.0.0

---

## 📁 Module Structure

```
family_hierarchy/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── family_person.py        ← Core entity (people + hierarchy)
│   ├── family_relationship.py  ← Relationship types
│   └── family_event.py         ← Life events
├── views/
│   ├── family_person_views.xml      ← Form, tree, kanban, search
│   ├── family_relationship_views.xml
│   ├── family_event_views.xml
│   └── family_menus.xml             ← Menu structure
├── security/
│   ├── ir.model.access.csv    ← Access control rules
│   └── family_security.xml    ← Groups definition
└── data/
    └── family_data.xml        ← Demo/seed data (3-gen family)
```

---

## 🚀 Installation

1. **Copy module** to your Odoo addons directory:
   ```bash
   cp -r family_hierarchy /path/to/odoo/addons/
   ```

2. **Restart Odoo server**:
   ```bash
   ./odoo-bin -c odoo.conf --stop-after-init
   ./odoo-bin -c odoo.conf
   ```

3. **Update apps list** in Odoo:
   - Go to Apps → Update Apps List

4. **Install the module**:
   - Search for "Family Hierarchy" → Install

---

## 🧩 Features

### People Management
- Full CRUD with photo upload
- Fields: Name, DOB, Gender, Status (Alive/Deceased), Occupation, Education
- Auto-computed Age
- Parent → Child hierarchy with circular reference protection
- Stat buttons for quick navigation to children & events

### Relationship Management
- 15 relationship types (Father, Mother, Son, Daughter, Spouse, Sibling, etc.)
- Duplicate prevention constraint
- **"Create Inverse" button** — auto-creates the reverse relationship
- Gender-aware inverse mapping (e.g. son ↔ father/mother)

### Life Event Tracking
- Event types: Birth, Death, Marriage, Divorce, Education, Employment, Graduation, Retirement, Migration
- Date range support (start + end date)
- Partner linkage for marriage/divorce events
- Auto-syncs birth/death dates with person record

---

## 🔐 Security Groups

| Group           | Read | Write | Create | Delete |
|-----------------|------|-------|--------|--------|
| Family User     | ✅   | ✅    | ✅     | ❌     |
| Family Manager  | ✅   | ✅    | ✅     | ✅     |

Assign users via: **Settings → Users → User → Family Hierarchy**

---

## 📊 Data Model

```
family.person
  ├── parent_id  →  family.person   (self-join hierarchy)
  ├── child_ids  ←  family.person
  ├── relationship_ids → family.relationship
  └── event_ids        → family.event

family.relationship
  ├── person_id         → family.person
  └── related_person_id → family.person

family.event
  ├── person_id         → family.person
  └── partner_person_id → family.person
```

---

## 🔮 Future Enhancements (Phase 2)

- [ ] Family tree visualization (D3.js / OWL widget)
- [ ] Multi-family support
- [ ] Advanced relationship derivation (uncle, cousin via graph traversal)
- [ ] Event timeline view
- [ ] PDF family tree export
- [ ] DNA / lineage analytics

---

## ⚙️ Odoo Compatibility

- **Version**: 17.0 (adaptable to 18.0 / 19.0)
- **Dependencies**: `base`, `mail`
