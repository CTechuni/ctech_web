-- CTech Database Dump (Standardized)
-- Created on: 2026-03-11
-- This file reflects the current architecture with 3 active roles (Admin, Leader, User)
-- and remove deprecated modules (Courses, Mentorships, etc.)

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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
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
    image character varying(255),
    status character varying(50) DEFAULT 'pending',
    visibility character varying(20) DEFAULT 'publico',
    type_event character varying(50),
    capacity integer,
    community_id integer REFERENCES public.communities(id_community),
    created_by integer REFERENCES public.users(id)
);

-- 6. NOTIFICATIONS
CREATE TABLE public.notifications (
    id SERIAL PRIMARY KEY,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    type character varying(50),
    is_read boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- 7. TOKEN BLOCKLIST
CREATE TABLE public.token_blocklist (
    id SERIAL PRIMARY KEY,
    token text NOT NULL,
    blacklisted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_reset_token ON public.users(reset_token);
CREATE INDEX idx_token_blocklist_token ON public.token_blocklist(token);

-- FOREIGN KEY FOR COMMUNITIES (Circular reference handled after tables creation)
ALTER TABLE public.communities ADD CONSTRAINT fk_communities_leader FOREIGN KEY (leader_id) REFERENCES public.users(id) ON DELETE SET NULL;
