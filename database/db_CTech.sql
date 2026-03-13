-- CTech Database Dump (Standardized)
-- Updated: 2026-03-12
-- 3 roles activos: Admin (1), Leader (3), User (4)
-- Módulos eliminados: courses, mentoring_sessions, specialties, technologies, content

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- 1. ROLES
CREATE TABLE public.roles (
    id_rol integer NOT NULL PRIMARY KEY,
    name_rol character varying(50) NOT NULL UNIQUE,
    description text
);

COPY public.roles (id_rol, name_rol, description) FROM stdin;
1	admin	Administrador del sistema
3	leader	Líder de comunidad
4	user	Usuario estándar
\.

-- 2. COMMUNITIES
CREATE TABLE public.communities (
    id_community SERIAL PRIMARY KEY,
    name_community character varying(150) NOT NULL,
    description_community text,
    status_community character varying(50) NOT NULL DEFAULT 'Activo',
    code character varying(50) NOT NULL UNIQUE,
    access_code character varying(50) UNIQUE,
    logo_url character varying(255),
    leader_id integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- 3. USERS
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    email character varying(150) NOT NULL UNIQUE,
    password_hash text NOT NULL,
    name_user character varying(150),
    rol_id integer REFERENCES public.roles(id_rol),
    community_id integer REFERENCES public.communities(id_community),
    status character varying(50) DEFAULT 'active',
    is_email_verified boolean DEFAULT false,
    reset_token character varying(255) UNIQUE,
    reset_token_expires timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_login timestamp without time zone
);

-- 4. PROFILES
CREATE TABLE public.profiles (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    bio text,
    phone character varying(20),
    avatar_url character varying(255),
    github_url character varying(255),
    linkedin_url character varying(255)
);

-- 5. EVENTS
CREATE TABLE public.events (
    id_event SERIAL PRIMARY KEY,
    title character varying(255) NOT NULL,
    description_event text,
    date_events date,
    time_events time without time zone,
    place character varying(255),
    image text,
    status character varying(50) DEFAULT 'pending',   -- draft | pending | approved | rejected
    visibility character varying(20) DEFAULT 'publico', -- publico | privado
    type_event character varying(50),                  -- presencial | virtual
    capacity integer,
    community_id integer REFERENCES public.communities(id_community),
    creator_id integer REFERENCES public.users(id)
);

-- 6. EVENT REGISTRATIONS
CREATE TABLE public.event_registrations (
    id SERIAL PRIMARY KEY,
    event_id integer NOT NULL REFERENCES public.events(id_event) ON DELETE CASCADE,
    user_id integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    registered_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_event_user UNIQUE (event_id, user_id)
);

-- 7. NOTIFICATIONS
CREATE TABLE public.notifications (
    id SERIAL PRIMARY KEY,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    type character varying(50),
    is_read boolean DEFAULT false,
    recipient_id integer REFERENCES public.users(id) ON DELETE CASCADE,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- 8. TOKEN BLOCKLIST
CREATE TABLE public.token_blocklist (
    id SERIAL PRIMARY KEY,
    token text NOT NULL,
    blacklisted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_reset_token ON public.users(reset_token);
CREATE INDEX idx_token_blocklist_token ON public.token_blocklist(token);
CREATE INDEX idx_event_registrations_event ON public.event_registrations(event_id);
CREATE INDEX idx_event_registrations_user ON public.event_registrations(user_id);
CREATE INDEX idx_notifications_recipient ON public.notifications(recipient_id);

-- FOREIGN KEY (referencia circular communities → users)
ALTER TABLE public.communities
    ADD CONSTRAINT fk_communities_leader
    FOREIGN KEY (leader_id) REFERENCES public.users(id) ON DELETE SET NULL;
