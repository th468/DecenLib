# Project Instructions: Library

## 1. Project Overview & Objectives
- **Goal:** Career portfolio. Prototype of a distributed library application for a hypothetical company.
- **Challenge:** Manage 15,000 volumes across 20 floors in a "virtual bookshelf" without physical relocation.
- **UX Constraint:** Location details **MUST ONLY** be revealed after checkout or reservation confirmation to prevent unrecorded removal and ensure data integrity.

## 2. Directory Architecture
- `library/`: Django project root.
  - `core/`: Abstract foundation (BaseModel, Mixins, Tags). Global conventions for all apps.
  - `accounts/`: Authentication, department management, and permissions.
  - `catalog/`: Static data (Biblios, Books, Locations, Favorites).
  - `transactions/`: Dynamic lifecycle (Lending and Reservation logic). **Mission-critical.**
  - `dashboard/`: Integrated portal UI. Cross-app data visualization.

## 3. Tech Stack
- **Framework:** Django 6.0.2 / Python 3.14
- **Tools:** django-widget-tweaks, Factory Boy, Faker
- **Quality:** Ruff (Lint/Format), mypy (Type Check)
- **Database:** SQLite3

## 4. Engineering Standards
### Models & Logic
- **BaseModel Inheritance:** All models **MUST** inherit from `core.models.BaseModel` for standardized logical deletion via `is_active`.
- **Logic Placement:** Prioritize 1. Model (Fat Model) > 2. Form > 3. Service. **DO NOT** implement business logic in Views (Thin View).
- **Data Reset:** In maintenance scripts (e.g., seed data), use `all_objects.hard_delete()` for physical removal of records. Standard `.delete()` only marks them as inactive, which causes `IntegrityError` on re-entry of unique fields.
- **Type Safety:** Always import `timedelta` from `datetime`. When accessing `request.user` in Views, use explicit `is_authenticated` checks even if `LoginRequiredMixin` is present to ensure type safety for mypy.
- **Views:** Prioritize Class-Based Views (CBV).
- **Naming:** STRICT PEP8 compliance (Class: PascalCase, Var/Func: snake_case).

### Testing
- **Factories:** `factories.py` is **MANDATORY**. Use `BaseModelTestMixin` to strictly verify logical deletion and `__str__` formats.
- **ManyToMany in Factories:** Use `@factory.post_generation` for models with `ManyToManyField` to allow seamless relation creation during data seeding.
- **Coverage:** Include happy path, edge cases (max length, date chronology), and error handling.

### Templates
- Inherit from `common/base.html`. Modularize UI components into `common/includes/` to ensure DRY principles.

## 5. Operational Protocols
- **TODO Management:** Any technical debt or future enhancements identified during implementation **MUST** be recorded in `docs/TODO.md`.
- **Architectural Documentation:** Major design decisions, performance optimizations, and technical rationales (e.g., Mixin hierarchies, N+1 solutions) **MUST** be documented in `docs/ARCH_DESIGN.md` to ensure design transparency and knowledge transfer.
- **Architecture First:** Prioritize fixing structural or data model issues over local surgical fixes.

## 6. Primary Commands
- Test: `python library/manage.py test library`
- Quality: `ruff check .` / `mypy .`
- Database: `python library/manage.py makemigrations` / `migrate`

## 7. Session Wrap-up Protocol
- **Summary Format:** When explicitly instructed by the user, provide a concise summary of the achievements.
    - **Top-line Summary:** A single sentence of max 30 characters summarizing the core achievement.
    - **Detailed Items:** 3-5 bullet points describing specific technical milestones and outcomes.

---

