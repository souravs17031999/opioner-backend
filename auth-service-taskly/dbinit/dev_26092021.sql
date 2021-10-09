--
-- PostgreSQL database dump
--
-- Dumped from database version 12.8 (Ubuntu 12.8-0ubuntu0.20.04.1)
-- Dumped by pg_dump version 12.8 (Ubuntu 12.8-0ubuntu0.20.04.1)
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
--
-- Name: tablename_colname_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE IF NOT EXISTS public.tablename_colname_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE public.tablename_colname_seq OWNER TO postgres;
SET default_tablespace = '';
SET default_table_access_method = heap;
--
-- Name: task_list; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE IF NOT EXISTS public.task_list (
    list_id integer NOT NULL,
    user_id integer NOT NULL,
    description text NOT NULL,
    status_tag text DEFAULT 'Todo'::text,
    is_email_pushed smallint DEFAULT 0,
    is_phone_pushed smallint DEFAULT 0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE public.task_list OWNER TO postgres;
--
-- Name: task_list_list_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE IF NOT EXISTS public.task_list_list_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE public.task_list_list_id_seq OWNER TO postgres;
--
-- Name: task_list_list_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.task_list_list_id_seq OWNED BY public.task_list.list_id;
--
-- Name: user_notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE IF NOT EXISTS public.user_notifications_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE public.user_notifications_id_seq OWNER TO postgres;
--
-- Name: user_notifications; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE IF NOT EXISTS public.user_notifications (
    id integer DEFAULT nextval('public.user_notifications_id_seq'::regclass) NOT NULL,
    event_type text,
    description text NOT NULL,
    user_id integer NOT NULL,
    read_flag smallint DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE public.user_notifications OWNER TO postgres;
--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--
CREATE TABLE IF NOT EXISTS public.users (
    user_id integer NOT NULL,
    username text NOT NULL,
    password character varying(100),
    firstname text,
    lastname text,
    email text,
    phone text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE public.users OWNER TO postgres;
--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--
CREATE SEQUENCE IF NOT EXISTS public.users_user_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;
ALTER TABLE public.users_user_id_seq OWNER TO postgres;
--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--
ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;
--
-- Name: task_list list_id; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.task_list
ALTER COLUMN list_id
SET DEFAULT nextval('public.task_list_list_id_seq'::regclass);
--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.users
ALTER COLUMN user_id
SET DEFAULT nextval('public.users_user_id_seq'::regclass);
--
-- Data for Name: task_list; Type: TABLE DATA; Schema: public; Owner: postgres
--
-- COPY public.task_list (
--     list_id,
--     user_id,
--     description,
--     status_tag,
--     is_email_pushed,
--     is_phone_pushed,
--     created_at
-- )
-- FROM stdin;
-- 36 2 task Todo 0 0 2021 -09 -12 20 :31 :25.547461 + 05 :30 37 10 FIST TAS Todo 0 0 2021 -09 -12 20 :31 :25.547461 + 05 :30 38 1 first item in row Todo 0 0 2021 -09 -12 20 :31 :25.547461 + 05 :30 40 1 thid item Todo 0 0 2021 -09 -12 20 :38 :57.95314 + 05 :30 \.--
-- -- Data for Name: user_notifications; Type: TABLE DATA; Schema: public; Owner: postgres
-- --
-- COPY public.user_notifications (
--     id,
--     event_type,
--     description,
--     user_id,
--     read_flag,
--     created_at
-- )
-- FROM stdin;
-- 35 subscribe_task_email You have subscribed to timely notifications for this task,
-- check your email 1 1 2021 -09 -11 17 :31 :56.864992 + 05 :30 22 update_event Welcome to taskly ! Create your first task now,
-- it ’ s just a click away 8 0 2021 -09 -11 11 :00 :07.829202 + 05 :30 24 upload_profile_pic Profile pic updated successfully 9 1 2021 -09 -11 10 :56 :00.018019 + 05 :30 23 update_event Welcome to taskly ! Create your first task now,
-- it ’ s just a click away 9 1 2021 -09 -11 11 :00 :48.82872 + 05 :30 16 upload_profile_pic Profile pic updated successfully 1000 1 2021 -09 -10 22 :27 :07.687639 + 05 :30 17 upload_profile_pic Profile pic updated successfully 1000 1 2021 -09 -10 23 :43 :13.605847 + 05 :30 18 upload_profile_pic Profile pic updated successfully 1000 1 2021 -09 -10 23 :50 :01.490853 + 05 :30 19 subscribe_task_email You have subscribed to timely notifications for this task,
-- check your email 1000 1 2021 -09 -10 23 :59 :36.356433 + 05 :30 20 unsubscribe_task_email You have been unsubscribed
-- from timely notifications for this task.1000 1 2021 -09 -11 00 :02 :37.185692 + 05 :30 36 unsubscribe_task_email You have been unsubscribed
-- from timely notifications for this task.1 1 2021 -09 -11 18 :00 :18.28879 + 05 :30 26 upload_profile_pic Profile pic updated successfully 1 1 2021 -09 -11 11 :28 :37.478827 + 05 :30 25 upload_profile_pic Profile pic updated successfully 1000 1 2021 -09 -11 11 :28 :17.38164 + 05 :30 21 update_event Welcome to taskly ! Create your first task now,
--     it ’ s just a click away 1 1 2021 -09 -11 10 :53 :51.481269 + 05 :30 33 upload_profile_pic Profile pic updated successfully 1 1 2021 -09 -11 11 :47 :02.177807 + 05 :30 28 unsubscribe_task_email You have been unsubscribed
-- from timely notifications for this task.1 1 2021 -09 -11 11 :35 :09.897876 + 05 :30 30 upload_profile_pic Profile pic updated successfully 10 1 2021 -09 -11 11 :35 :48.810684 + 05 :30 29 update_event Welcome to taskly ! Create your first task now,
--     it ’ s just a click away 10 1 2021 -09 -11 11 :44 :00.080511 + 05 :30 31 subscribe_task_email You have subscribed to timely notifications for this task,
--     check your email 10 1 2021 -09 -11 11 :45 :58.357195 + 05 :30 32 unsubscribe_task_email You have been unsubscribed
-- from timely notifications for this task.10 1 2021 -09 -11 11 :46 :55.294158 + 05 :30 27 subscribe_task_email You have subscribed to timely notifications for this task,
--     check your email 1 1 2021 -09 -11 11 :35 :02.017747 + 05 :30 37 update_event Welcome to taskly ! Create your first task now,
--     it ’ s just a click away 11 1 2021 -09 -11 20 :48 :48.407318 + 05 :30 38 upload_profile_pic Profile pic updated successfully 1 1 2021 -09 -11 22 :21 :07.857185 + 05 :30 34 subscribe_task_email You have subscribed to timely notifications for this task,
--     check your email 1 1 2021 -09 -11 12 :30 :30.379463 + 05 :30 \.--
--     -- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--     --
--     COPY public.users (
--         user_id,
--         username,
--         password,
--         firstname,
--         lastname,
--         email,
--         phone,
--         created_at
--     )
-- FROM stdin;
-- 2 sourav1234 $2b$12$VknfW8bqf0jhMyCMQq7axesY9yJHIfLFy73RvmQ4L5L5cuDNnpUSe kjhdskj kjhkfjdhg \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 3 test12345 $2b$12$jQGS25fvDQpB3v6D9hO5j.icXHwrr1ElvYIC2jLq91XCxY05Mahqy kjkad khk \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 4 test123456 $2b$12$dLw.07oavQ9ReAfh8l3EbekLoLWiFDhXQ8yXffH.GZkeVAgMqML7q kjh kjhkfhg \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 6 elonmusk123 $2b$12$NRl6tS3IxeQlH7dPy2f1T.Zai4K3MO4LtBpZQ7q3gi01UmLYLsfvS ELON MUSK \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 7 elonmusk1234 $2b$12$i.qIqOpQ1Ns88.WI.xX4COJ.t2oM0yY.2pC.jeL7BC3nOudRIFQLi ELON MUSK \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 8 itishas12 $2b$12$NAaV5 / WhNHKN2ICJbuAlReK7Omb6l9HWLC4y836 / ebZ.Wrn2lsGL6 vyasa veda \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 9 vyasaveda $2b$12$B7X3A6JZc0LF1UjN92muuuPIfBNX8sWqQtHejGx08i.gytwFLY0ci vyasa ved \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 10 PETRA123 $2b$12$v6d3Xw / MfOs9RAEH / WsgcujTUpaf9ISyLG24fOyMUI.15KcC6ahT6 PETRA JORDAN sauravkumarsct @gmail.com 2021 -09 -12 20 :31 :09.623088 + 05 :30 1 sourav123 $2b$12$ODD4u4yRLqjKqaHcn65SgOmgyjkqlKpy.tVNpRr0me0AUhKwJpXGe sourav kumar sauravkumarsct @gmail.com 5796598646 2021 -09 -12 20 :31 :09.623088 + 05 :30 11 ithkjahk $2b$12$ByBZZBi1H / T4.87xAgZ8aeY / iDxVOJlAf5Jkj8zkRB / n7jyZ6FcWm veda vyusu \ N \ N 2021 -09 -12 20 :31 :09.623088 + 05 :30 \.--
-- -- Name: tablename_colname_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --
SELECT pg_catalog.setval('public.tablename_colname_seq', 1, false);
--
-- Name: task_list_list_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--
SELECT pg_catalog.setval('public.task_list_list_id_seq', 40, true);
--
-- Name: user_notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--
SELECT pg_catalog.setval('public.user_notifications_id_seq', 38, true);
--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--
SELECT pg_catalog.setval('public.users_user_id_seq', 11, true);
--
-- Name: task_list task_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.task_list
ADD CONSTRAINT task_list_pkey PRIMARY KEY (list_id);
--
-- Name: user_notifications user_notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.user_notifications
ADD CONSTRAINT user_notifications_pkey PRIMARY KEY (id);
--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--
ALTER TABLE ONLY public.users
ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
--
-- PostgreSQL database dump complete
--