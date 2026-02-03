--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 18.1

-- SET statement_timeout = 0;
-- SET lock_timeout = 0;
-- SET idle_in_transaction_session_timeout = 0;
-- SET transaction_timeout = 0;
-- SET client_encoding = 'UTF8';
-- SET standard_conforming_strings = on;
-- SELECT pg_catalog.set_config('search_path', '', false);
-- SET check_function_bodies = false;
-- SET xmloption = content;
-- SET client_min_messages = warning;
-- SET row_security = off;

--
-- Data for Name: feeds; Type: TABLE DATA; Schema: public; Owner: rssuser
--

INSERT INTO public.feeds VALUES (2, 'https://www.crownanabread.com/blog/rss.xml', 'Crownanabread Blog', '2025-08-11 02:14:08', '02:00:00', '2026-02-03 06:43:13', 0, DEFAULT);


--
-- Data for Name: feed_history; Type: TABLE DATA; Schema: public; Owner: rssuser
--

INSERT INTO public.feed_history VALUES (1, 2, 'Email updates (for all!)', 'https://crownanabread.com/blog/posts/email_updates.html', '2025-08-08 00:00:00+00', '2025-08-11 02:14:08', '59b459beecddfacf875e1016d845ebc0a9b36230');
INSERT INTO public.feed_history VALUES (2, 2, 'Creative flash photos', 'https://crownanabread.com/blog/posts/creative_flash_photography.html', '2025-07-18 00:00:00+00', '2025-08-11 02:14:08', 'fe0e966df53da64eb6a09819b82ab61640911db2');
INSERT INTO public.feed_history VALUES (3, 2, 'Blog updates', 'https://crownanabread.com/blog/posts/blog_updates.html', '2025-07-01 00:00:00+00', '2025-08-11 02:14:08', '6c87aa676f44b6cc2dffd176c775263572e523c5');
INSERT INTO public.feed_history VALUES (4, 2, 'Using photos in Freecad', 'https://crownanabread.com/blog/posts/using_photos_in_freecad.html', '2025-06-03 00:00:00+00', '2025-08-11 02:14:08', '98f0b31174cc026f9a0705df1b168d55672b7832');
INSERT INTO public.feed_history VALUES (5, 2, 'A new start!', 'https://crownanabread.com/blog/posts/a_new_start!.html', '2025-05-28 00:00:00+00', '2025-08-11 02:14:08', '80c0f3f8ff360b14b2ea9a617b290827efbb94dc');
INSERT INTO public.feed_history VALUES (6, 2, 'My (old) new setup & cd collection', 'https://crownanabread.com/blog/posts/my_new_setup.html', '2025-08-22 00:00:00+00', '2025-08-22 18:16:16', 'ab2ba0099ca87dc9559bf58af97e2383a409a5ab');
INSERT INTO public.feed_history VALUES (7, 2, 'What the flock??', 'https://crownanabread.com/blog/posts/what_the_flock.html', '2025-12-03 00:00:00+00', '2025-12-03 10:32:49', '80a4fa6246eda4d07b26c81708fcf55f9604cb27');
INSERT INTO public.feed_history VALUES (8, 2, 'I spray painted an xbox controller!', 'https://crownanabread.com/blog/posts/controller.html', '2025-12-27 00:00:00+00', '2025-12-28 00:36:44', 'd1b13f83339c6284b8cdcb7576c36df896159c73');
INSERT INTO public.feed_history VALUES (9, 2, 'OSM is the new hotness', 'https://crownanabread.com/blog/posts/OSM-pt-1.html', '2025-12-30 00:00:00+00', '2025-12-30 20:37:12', '456f25db2ff696c1a84b0cb3f811707d7e963d9e');
INSERT INTO public.feed_history VALUES (10, 2, '1/19/26', 'https://crownanabread.com/blog/posts/1.19.26_micro_post.html', '2026-01-19 00:00:00+00', '2026-01-20 10:40:36', '050df47e954ba82acd82610b238a0fb92c515fce');
INSERT INTO public.feed_history VALUES (11, 2, '1/24/26 The Vigil (micro post)', 'https://crownanabread.com/blog/posts/1.25.26_vigil_micro_post.html', '2026-01-24 00:00:00+00', '2026-01-25 10:41:24', '48269f1ba2826e46c159874d9559b7203da726e3');
INSERT INTO public.feed_history VALUES (12, 2, '1/26/26 The Vigil (micro post)', 'https://crownanabread.com/blog/posts/1.26.26_new_cd_mix.html', '2026-01-26 00:00:00+00', '2026-01-27 10:41:44', '51d662d5fcd078f50df7f31c2e9a544569b5a5b5');
INSERT INTO public.feed_history VALUES (13, 2, '1/26/26 New CD mix (micro post)', 'https://crownanabread.com/blog/posts/1.26.26_new_cd_mix.html', '2026-01-26 00:00:00+00', '2026-01-27 18:41:48', '41d6b571e2df0a6299024336bb63f8d7b4c0cf10');
INSERT INTO public.feed_history VALUES (14, 2, '2/2/26 OSM Mappin (micro post)', 'https://crownanabread.com/blog/posts/2.2.26_osm_mappin.html', '2026-02-02 00:00:00+00', '2026-02-03 00:43:11', '8682e430f0473e4dcd50f3130e7fbd8ecd3ffae7');


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: rssuser
--

-- Changed all 2026 dates to 2025 in this column, to make sure it's all in the past for testing purposes.
INSERT INTO public.subscriptions VALUES (3, 2, '2025-08-25 00:47:32', 0.6959305354745251, 'user1@gmail.com', true, 11, true, '2025-01-27 10:40:44', '7 days', DEFAULT, false, '2025-01-27 10:40:44');
INSERT INTO public.subscriptions VALUES (5, 2, '2025-10-19 22:56:29', 0.4456253721561241, 'user2@gmail.com', true, 8, true, '2025-01-27 10:40:44', '7 days', DEFAULT, false, '2025-01-27 10:40:44');
INSERT INTO public.subscriptions VALUES (2, 2, '2025-08-23 05:25:53', 0.24224009482332942, 'user3@gmail.com', true, 12, true, '2025-02-02 10:42:35', '1 day', DEFAULT, false, '2025-02-02 10:42:35');
INSERT INTO public.subscriptions VALUES (4, 2, '2025-09-26 09:13:15', 0.5947338748356923, 'user4@gmail.com', true, 12, true, '2025-02-02 10:42:35', '1 day', DEFAULT, false, '2025-02-02 10:42:35');
INSERT INTO public.subscriptions VALUES (1, 2, '2025-08-11 02:14:08', 0.34895677608980713, 'user5@gmail.com', true, 12, true, '2025-02-02 10:42:35', '1 day', DEFAULT, false, '2025-02-02 10:42:35');


--
-- Name: feed_history_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rssuser
--

SELECT pg_catalog.setval('public.feed_history_history_id_seq', 14, true);


--
-- Name: feeds_feed_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rssuser
--

SELECT pg_catalog.setval('public.feeds_feed_id_seq', 2, true);


--
-- Name: subscriptions_subscriber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: rssuser
--

SELECT pg_catalog.setval('public.subscriptions_subscriber_id_seq', 5, true);


--
-- PostgreSQL database dump complete
--
