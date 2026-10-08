--
-- PostgreSQL database dump
--

\restrict TW8o7kyWDstph8aweYup8VGRhO3HhIHx6fHTcc5IFA5H9r3tGEJsXIYEGwLmd8f

-- Dumped from database version 18.6 (Debian 18.6-1.pgdg13+2)
-- Dumped by pg_dump version 18.6 (Debian 18.6-1.pgdg13+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: yoshis; Type: TABLE; Schema: public; Owner: yoshi
--

CREATE TABLE public.yoshis (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    color character varying(50) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.yoshis OWNER TO yoshi;

--
-- Name: yoshis_id_seq; Type: SEQUENCE; Schema: public; Owner: yoshi
--

CREATE SEQUENCE public.yoshis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.yoshis_id_seq OWNER TO yoshi;

--
-- Name: yoshis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: yoshi
--

ALTER SEQUENCE public.yoshis_id_seq OWNED BY public.yoshis.id;


--
-- Name: yoshis id; Type: DEFAULT; Schema: public; Owner: yoshi
--

ALTER TABLE ONLY public.yoshis ALTER COLUMN id SET DEFAULT nextval('public.yoshis_id_seq'::regclass);


--
-- Data for Name: yoshis; Type: TABLE DATA; Schema: public; Owner: yoshi
--

COPY public.yoshis (id, name, color, created_at) FROM stdin;
1	Yoshi	green	2026-10-07 17:25:11.264731
2	Red Yoshi	red	2026-10-07 17:25:11.264731
3	Blue Yoshi	blue	2026-10-07 17:25:11.264731
\.


--
-- Name: yoshis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: yoshi
--

SELECT pg_catalog.setval('public.yoshis_id_seq', 3, true);


--
-- Name: yoshis yoshis_pkey; Type: CONSTRAINT; Schema: public; Owner: yoshi
--

ALTER TABLE ONLY public.yoshis
    ADD CONSTRAINT yoshis_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict TW8o7kyWDstph8aweYup8VGRhO3HhIHx6fHTcc5IFA5H9r3tGEJsXIYEGwLmd8f

