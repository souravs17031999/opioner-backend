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
-- Data for Name: task_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.task_list (list_id, user_id, description, status_tag, is_email_pushed, is_phone_pushed, created_at) VALUES (36, 2, 'task', 'Todo', 0, 0, '2021-09-12 20:31:25.547461+05:30');
INSERT INTO public.task_list (list_id, user_id, description, status_tag, is_email_pushed, is_phone_pushed, created_at) VALUES (37, 10, 'FIST TAS', 'Todo', 0, 0, '2021-09-12 20:31:25.547461+05:30');
INSERT INTO public.task_list (list_id, user_id, description, status_tag, is_email_pushed, is_phone_pushed, created_at) VALUES (38, 1, 'first item in row', 'Todo', 0, 0, '2021-09-12 20:31:25.547461+05:30');
INSERT INTO public.task_list (list_id, user_id, description, status_tag, is_email_pushed, is_phone_pushed, created_at) VALUES (40, 1, 'thid item', 'Todo', 0, 0, '2021-09-12 20:38:57.95314+05:30');


--
-- Data for Name: user_notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (35, 'subscribe_task_email', 'You have subscribed to timely notifications for this task, check your email', 1, 1, '2021-09-11 17:31:56.864992+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (22, 'update_event', 'Welcome to taskly ! Create your first task now, it’s just a click away', 8, 0, '2021-09-11 11:00:07.829202+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (24, 'upload_profile_pic', 'Profile pic updated successfully', 9, 1, '2021-09-11 10:56:00.018019+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (23, 'update_event', 'Welcome to taskly ! Create your first task now, it’s just a click away', 9, 1, '2021-09-11 11:00:48.82872+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (16, 'upload_profile_pic', 'Profile pic updated successfully', 1000, 1, '2021-09-10 22:27:07.687639+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (17, 'upload_profile_pic', 'Profile pic updated successfully', 1000, 1, '2021-09-10 23:43:13.605847+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (18, 'upload_profile_pic', 'Profile pic updated successfully', 1000, 1, '2021-09-10 23:50:01.490853+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (19, 'subscribe_task_email', 'You have subscribed to timely notifications for this task, check your email', 1000, 1, '2021-09-10 23:59:36.356433+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (20, 'unsubscribe_task_email', 'You have been unsubscribed from timely notifications for this task.', 1000, 1, '2021-09-11 00:02:37.185692+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (36, 'unsubscribe_task_email', 'You have been unsubscribed from timely notifications for this task.', 1, 1, '2021-09-11 18:00:18.28879+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (26, 'upload_profile_pic', 'Profile pic updated successfully', 1, 1, '2021-09-11 11:28:37.478827+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (25, 'upload_profile_pic', 'Profile pic updated successfully', 1000, 1, '2021-09-11 11:28:17.38164+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (21, 'update_event', 'Welcome to taskly ! Create your first task now, it’s just a click away', 1, 1, '2021-09-11 10:53:51.481269+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (33, 'upload_profile_pic', 'Profile pic updated successfully', 1, 1, '2021-09-11 11:47:02.177807+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (28, 'unsubscribe_task_email', 'You have been unsubscribed from timely notifications for this task.', 1, 1, '2021-09-11 11:35:09.897876+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (30, 'upload_profile_pic', 'Profile pic updated successfully', 10, 1, '2021-09-11 11:35:48.810684+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (29, 'update_event', 'Welcome to taskly ! Create your first task now, it’s just a click away', 10, 1, '2021-09-11 11:44:00.080511+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (31, 'subscribe_task_email', 'You have subscribed to timely notifications for this task, check your email', 10, 1, '2021-09-11 11:45:58.357195+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (32, 'unsubscribe_task_email', 'You have been unsubscribed from timely notifications for this task.', 10, 1, '2021-09-11 11:46:55.294158+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (27, 'subscribe_task_email', 'You have subscribed to timely notifications for this task, check your email', 1, 1, '2021-09-11 11:35:02.017747+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (37, 'update_event', 'Welcome to taskly ! Create your first task now, it’s just a click away', 11, 1, '2021-09-11 20:48:48.407318+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (38, 'upload_profile_pic', 'Profile pic updated successfully', 1, 1, '2021-09-11 22:21:07.857185+05:30');
INSERT INTO public.user_notifications (id, event_type, description, user_id, read_flag, created_at) VALUES (34, 'subscribe_task_email', 'You have subscribed to timely notifications for this task, check your email', 1, 1, '2021-09-11 12:30:30.379463+05:30');


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (2, 'sourav1234', '$2b$12$VknfW8bqf0jhMyCMQq7axesY9yJHIfLFy73RvmQ4L5L5cuDNnpUSe', 'kjhdskj', 'kjhkfjdhg', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (3, 'test12345', '$2b$12$jQGS25fvDQpB3v6D9hO5j.icXHwrr1ElvYIC2jLq91XCxY05Mahqy', 'kjkad', 'khk', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (4, 'test123456', '$2b$12$dLw.07oavQ9ReAfh8l3EbekLoLWiFDhXQ8yXffH.GZkeVAgMqML7q', 'kjh', 'kjhkfhg', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (6, 'elonmusk123', '$2b$12$NRl6tS3IxeQlH7dPy2f1T.Zai4K3MO4LtBpZQ7q3gi01UmLYLsfvS', 'ELON', 'MUSK', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (7, 'elonmusk1234', '$2b$12$i.qIqOpQ1Ns88.WI.xX4COJ.t2oM0yY.2pC.jeL7BC3nOudRIFQLi', 'ELON', 'MUSK', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (8, 'itishas12', '$2b$12$NAaV5/WhNHKN2ICJbuAlReK7Omb6l9HWLC4y836/ebZ.Wrn2lsGL6', 'vyasa', 'veda', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (9, 'vyasaveda', '$2b$12$B7X3A6JZc0LF1UjN92muuuPIfBNX8sWqQtHejGx08i.gytwFLY0ci', 'vyasa', 'ved', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (10, 'PETRA123', '$2b$12$v6d3Xw/MfOs9RAEH/WsgcujTUpaf9ISyLG24fOyMUI.15KcC6ahT6', 'PETRA', 'JORDAN', 'sauravkumarsct@gmail.com', '', '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (1, 'sourav123', '$2b$12$ODD4u4yRLqjKqaHcn65SgOmgyjkqlKpy.tVNpRr0me0AUhKwJpXGe', 'sourav ', 'kumar', 'sauravkumarsct@gmail.com', '5796598646', '2021-09-12 20:31:09.623088+05:30');
INSERT INTO public.users (user_id, username, password, firstname, lastname, email, phone, created_at) VALUES (11, 'ithkjahk', '$2b$12$ByBZZBi1H/T4.87xAgZ8aeY/iDxVOJlAf5Jkj8zkRB/n7jyZ6FcWm', 'veda', 'vyusu', NULL, NULL, '2021-09-12 20:31:09.623088+05:30');


--
-- Name: tablename_colname_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

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
-- PostgreSQL database dump complete
--

