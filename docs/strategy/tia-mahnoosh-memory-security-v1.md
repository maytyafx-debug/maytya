# Tia & Mahnoosh — Persistent Memory and Security Design v1

Status: design proposal only. No production database schema, authentication settings, secrets, or deployment were changed by this document.

## 1. Goal

Move beyond browser-only chat history while preserving strict separation between:
- the signed-in user who owns the data;
- Tia's persona-specific memories;
- Mahnoosh's persona-specific memories;
- future organization/workspace memories, which must not be mixed into personal memory.

The first release stores only concise, user-approved memory notes. It does not silently retain every chat transcript.

## 2. Verified current state

- Supabase project: the existing active Metatya project in eu-west-1.
- PostgreSQL 17.
- Existing public tables include leads, orders, data_bank, content_drafts, finance_ledger, monetization_opportunities and needs_offers.
- No Supabase Edge Functions are currently listed.
- Security Advisor reports RLS enabled without policies on data_bank, finance_ledger and monetization_opportunities.
- Existing policies include public insert for consented leads/orders and public read for published content. These policies must not be broadened as part of agent memory work.
- The Tia/Mahnoosh staging Worker is separate and not deployed yet.

## 3. Proposed first-release data model

Create `public.agent_memories` only after the authentication flow and ownership model have been agreed and tested.

Suggested columns:
- `id uuid primary key default gen_random_uuid()`
- `user_id uuid not null references auth.users(id) on delete cascade`
- `persona text not null check (persona in ('tia','mahnoosh'))`
- `memory_type text not null check (memory_type in ('preference','project_context','decision','workflow','other'))`
- `content text not null check (char_length(content) between 1 and 3000)`
- `source text not null default 'user_approved'`
- `consent_version text not null`
- `created_at timestamptz not null default now()`
- `updated_at timestamptz not null default now()`
- `expires_at timestamptz null`
- `is_active boolean not null default true`

Do not store raw chat transcripts in this table. Do not store passwords, API keys, payment data, government identifiers, or sensitive personal data. Sensitive categories should be excluded from agent memory unless a separately reviewed, lawful product requirement exists.

## 4. Access-control model

- Require Supabase Auth before any persistent memory is read or written.
- Frontend uses only a publishable key and the signed-in user's access token.
- Never put a Supabase secret/service-role key in HTML, JavaScript shipped to browsers, or a public GitHub repository.
- Enable RLS on `agent_memories`.
- Add SELECT, INSERT, UPDATE and DELETE policies for role `authenticated`, each scoped to `(select auth.uid()) = user_id`.
- UPDATE policy must include both USING and WITH CHECK ownership predicates.
- Do not use user-editable `user_metadata` for authorization.
- Index `(user_id, persona, is_active, updated_at desc)`.
- Keep service-only operations behind a trusted server endpoint that validates the caller's JWT and enforces ownership. Do not trust a client-supplied user_id.

## 5. Persona separation

Every memory row is tagged with exactly one persona. Tia queries only Tia memories; Mahnoosh queries only Mahnoosh memories. Duo mode may receive a deliberately selected, minimal context from both personas, but must not silently merge or rewrite either memory store.

## 6. Consent and user controls

Before memory is enabled, show a clear explanation and obtain an affirmative opt-in. Provide:
- view saved memories;
- edit a memory;
- delete one memory;
- clear all memories for one persona;
- disable persistent memory;
- export memories in a readable format.

A user request to forget must trigger deletion of the matching stored records and confirmation only after the database confirms deletion. Retention expiry should be enforced by a scheduled cleanup process only after the retention policy is finalized.

## 7. Rollout sequence

1. Review and approve the authentication method and consent text.
2. Add the database migration on an isolated development branch or other non-production environment.
3. Verify RLS using two separate test accounts: each account must be unable to read, update or delete the other's rows.
4. Run Supabase Security and Performance Advisors; fix findings relevant to the new table.
5. Implement login/session handling in the Tia/Mahnoosh UI.
6. Implement authenticated memory endpoints and persona-scoped retrieval.
7. Test memory creation, retrieval, editing, deletion, opt-out, expiry and cross-user isolation.
8. Only then enable persistent memory in staging; do not enable it on the public site until review is complete.

## 8. Separate security follow-up

The three existing tables flagged by Security Advisor need a dedicated review:
- `public.data_bank`
- `public.finance_ledger`
- `public.monetization_opportunities`

RLS is enabled but no policies are present. This currently means ordinary API roles are blocked rather than granted access. Do not add blanket policies. First identify which trusted Worker or admin workflows need access, then define least-privilege policies or keep access server-only.

## 9. Not included yet

- Voice recording storage or transcription memory.
- Avatar, animation, lip-sync or 3D movement.
- Organization/tenant memory and role-based team access.
- Vector embeddings or semantic search.
- Automatic memory extraction without user review.

These remain later milestones, not claims of current functionality.
