-- LeaseGrow: заполнение БД тестовыми данными (продакшн-подобными)
-- Админ: admin@gmail.com / adminadmin

-- Роли
INSERT INTO role (name, permissions, created_at) VALUES
('admin', '["all"]', CURRENT_TIMESTAMP),
('manager', '["contracts", "companies", "equipment"]', CURRENT_TIMESTAMP),
('accountant', '["contracts", "payments"]', CURRENT_TIMESTAMP),
('client', '["own_contracts"]', CURRENT_TIMESTAMP);

-- Аккаунты (admin первым)
INSERT INTO account (email, username, password_hash, role_id, is_active, last_login, created_at, updated_at) VALUES
('admin@gmail.com', 'admin', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 1, TRUE, '2026-05-06 09:15:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO account (email, username, password_hash, role_id, is_active, last_login, created_at, updated_at) VALUES
('ivan.petrov@agro.ru', 'ivan_manager', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 2, TRUE, '2026-05-06 10:05:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('maria.sidorova@leasegrow.ru', 'maria_accountant', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 3, TRUE, '2026-05-05 17:20:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client1@agrofarm.ru', 'agrofarm_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 11:00:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client2@zemledel.ru', 'zemledel_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 10:48:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client3@harvest.ru', 'harvest_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 10:33:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('manager2@leasegrow.ru', 'manager2', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 2, TRUE, '2026-05-06 15:12:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client4@niva.ru', 'niva_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 09:40:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client5@yugagro.ru', 'yugagro_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 09:10:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client6@chernozem.ru', 'chernozem_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 08:55:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client7@pole-rossii.ru', 'pole_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 08:42:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client8@kolos.ru', 'kolos_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 08:30:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client9@step.ru', 'step_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 08:18:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client10@agrosoyuz.ru', 'agrosoyuz_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 08:05:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client11@volga-agro.ru', 'volga_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, '2026-05-07 07:55:00+03', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Профили
INSERT INTO user_profile (account_id, first_name, last_name, phone, passport_series, passport_number, created_at, updated_at) VALUES
(1, 'Админ', 'Системы', '+7 (495) 111-11-11', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'Иван', 'Петров', '+7 (916) 111-22-22', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'Мария', 'Сидорова', '+7 (916) 222-33-33', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'Сергей', 'Кузнецов', '+7 (916) 333-44-44', '4501', '123456', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'Андрей', 'Морозов', '+7 (916) 444-55-55', '4502', '234567', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(6, 'Елена', 'Волкова', '+7 (916) 555-66-66', '4503', '345678', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(7, 'Дмитрий', 'Соколов', '+7 (916) 666-77-77', '', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(8, 'Николай', 'Кочетов', '+7 (916) 777-88-88', '4504', '456789', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(9, 'Павел', 'Тихонов', '+7 (916) 888-99-99', '4505', '567890', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(10, 'Виктор', 'Лапин', '+7 (916) 111-22-11', '4506', '678901', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(11, 'Олег', 'Суханов', '+7 (916) 222-33-11', '4507', '789012', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(12, 'Илья', 'Меркулов', '+7 (916) 333-44-11', '4508', '890123', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(13, 'Руслан', 'Белов', '+7 (916) 444-55-11', '4509', '901234', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(14, 'Егор', 'Климов', '+7 (916) 555-66-11', '4510', '012345', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(15, 'Артем', 'Горин', '+7 (916) 666-77-11', '4511', '112233', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- API токены (64 hex символа)
INSERT INTO account_token (key, account_id, created_at) VALUES
('a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 1, CURRENT_TIMESTAMP);

-- Компании
INSERT INTO company (name, inn, address, phone, email, status, account_id, created_at) VALUES
('ООО Агроферма Юг', '7707123456', 'г. Краснодар, ул. Промышленная, 1', '+7 (861) 200-11-11', 'info@agrofarm.ru', 'active', 4, CURRENT_TIMESTAMP),
('ООО Земледел', '7708234567', 'г. Ростов-на-Дону, пр. Будённовский, 50', '+7 (863) 250-22-22', 'office@zemledel.ru', 'active', 5, CURRENT_TIMESTAMP),
('АО Урожай Плюс', '7709345678', 'г. Ставрополь, ул. Мира, 100', '+7 (865) 230-33-33', 'contact@harvest.ru', 'active', 6, CURRENT_TIMESTAMP),
('ООО Нива Кубани', '7710456789', 'Краснодарский край, г. Тихорецк, ул. Ленина, 20', '+7 (861) 510-44-44', 'niva@kuban.ru', 'active', 8, CURRENT_TIMESTAMP),
('ПАО ЮгАгро', '7711567890', 'г. Ростов-на-Дону, ул. Большая Садовая, 1', '+7 (863) 300-55-55', 'info@yugagro.ru', 'active', 9, CURRENT_TIMESTAMP),
('ООО Чернозём', '7712678901', 'г. Воронеж, пр. Революции, 25', '+7 (473) 255-66-66', 'chernozem@vrn.ru', 'active', 10, CURRENT_TIMESTAMP),
('ООО Поле России', '7713789012', 'г. Волгоград, ул. Рабоче-Крестьянская, 10', '+7 (844) 230-77-77', 'pole@volgograd.ru', 'active', 11, CURRENT_TIMESTAMP),
('АО Колос', '7714890123', 'г. Саратов, ул. Московская, 50', '+7 (845) 220-88-88', 'kolos@saratov.ru', 'active', 12, CURRENT_TIMESTAMP),
('ООО Степь', '7715901234', 'г. Оренбург, ул. Советская, 30', '+7 (353) 275-99-99', 'step@orenburg.ru', 'active', 13, CURRENT_TIMESTAMP),
('ООО АгроСоюз', '7716012345', 'г. Самара, ул. Куйбышева, 100', '+7 (846) 260-00-00', 'agro@samara.ru', 'active', 14, CURRENT_TIMESTAMP),
('ООО Волга-Агро', '7717123456', 'г. Ульяновск, ул. Гончарова, 40', '+7 (842) 240-11-11', 'volga@ulsk.ru', 'active', 15, CURRENT_TIMESTAMP);

-- Категории техники (иерархия)
INSERT INTO equipment_category (name, parent_id, created_at) VALUES
('Тракторы', NULL, CURRENT_TIMESTAMP),
('Комбайны', NULL, CURRENT_TIMESTAMP),
('Посевная техника', NULL, CURRENT_TIMESTAMP),
('Плуги и культиваторы', NULL, CURRENT_TIMESTAMP);

INSERT INTO equipment_category (name, parent_id, created_at) VALUES
('Колёсные тракторы', 1, CURRENT_TIMESTAMP),
('Гусеничные тракторы', 1, CURRENT_TIMESTAMP),
('Зерноуборочные комбайны', 2, CURRENT_TIMESTAMP),
('Кормоуборочные комбайны', 2, CURRENT_TIMESTAMP),
('Пневматические сеялки', 3, CURRENT_TIMESTAMP),
('Дисковые сеялки', 3, CURRENT_TIMESTAMP);

-- Производители
INSERT INTO manufacturer (name, country) VALUES
('John Deere', 'США'),
('Case IH', 'США'),
('CLAAS', 'Германия'),
('New Holland', 'Италия'),
('AGCO (Massey Ferguson)', 'США'),
('Kubota', 'Япония'),
('Ростсельмаш', 'Россия'),
('Кировец', 'Россия'),
('Amazone', 'Германия'),
('Horsch', 'Германия'),
('Бuhler', 'Германия'),
('Kverneland', 'Норвегия');

-- Техника (много единиц)
INSERT INTO equipment (name, model, category_id, manufacturer_id, specifications, year, vin, condition, price, residual_value, monthly_lease_rate, status, location, images_urls, created_at, updated_at) VALUES
('John Deere 8R 370', '8R 370', 5, 1, 'Мощность 370 л.с., дизель', 2023, '1JDH8R370P1234567', 'new', 18500000.00, 9250000.00, 185000.00, 'available', 'Краснодарский край', '"/media/leasing/products/john-deere-8r-370-8r-370.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 9RX 640', '9RX 640', 6, 1, 'Мощность 640 л.с., дизель', 2022, '1JDH9RX640P1234568', 'new', 45000000.00, 22500000.00, 450000.00, 'leased', 'Краснодарский край', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere S790', 'S790', 6, 1, 'Мощность 458 л.с., гусеничный ход, дизель', 2023, '1JDHS790P1234569', 'new', 28000000.00, 14000000.00, 280000.00, 'available', 'Ростовская область', '"/media/leasing/products/john-deere-s790-s790.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere S680', 'S680', 7, 1, 'Производительность 55 т/ч, бак 10200 л', 2022, '1JDHS680P1234570', 'used', 22000000.00, 11000000.00, 220000.00, 'available', 'Ставропольский край', '"/media/leasing/products/john-deere-s680-s680.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Steiger 580 HD', 'Steiger 580 HD', 6, 2, 'Мощность 580 л.с., дизель', 2023, '2CSI580HD12345671', 'new', 42000000.00, 21000000.00, 420000.00, 'leased', 'Краснодарский край', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Magnum 340', 'Magnum 340', 5, 2, 'Мощность 340 л.с., дизель', 2022, '2CSIM34012345672', 'used', 16500000.00, 8250000.00, 165000.00, 'available', 'Воронежская область', '"/media/leasing/products/case-ih-magnum-340-magnum-340.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Axial-Flow 8250', 'Axial-Flow 8250', 7, 2, 'Производительность 65 т/ч, бак 11500 л', 2023, '2CSIAF825012345673', 'new', 26000000.00, 13000000.00, 260000.00, 'available', 'Ростовская область', '"/media/leasing/products/case-ih-axial-flow-8250-axial-flow-8250.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Xerion 5000', 'Xerion 5000', 5, 3, 'Мощность 493 л.с., дизель', 2022, '3CLAX5000P12345674', 'new', 38000000.00, 19000000.00, 380000.00, 'available', 'Краснодарский край', '"/media/leasing/products/claas-xerion-5000-xerion-5000.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Lexion 8900', 'Lexion 8900', 7, 3, 'Производительность 75 т/ч, бак 13500 л', 2023, '3CLAL8900P12345675', 'new', 32000000.00, 16000000.00, 320000.00, 'leased', 'Ставропольский край', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Lexion 780', 'Lexion 780', 7, 3, 'Производительность 55 т/ч, бак 10500 л', 2021, '3CLAL780P12345676', 'used', 24000000.00, 12000000.00, 240000.00, 'available', 'Волгоградская область', '"/media/leasing/products/claas-lexion-780-lexion-780.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland T8.410', 'T8.410', 5, 4, 'Мощность 410 л.с., дизель', 2023, '4NHT8410P12345677', 'new', 21000000.00, 10500000.00, 210000.00, 'available', 'Саратовская область', '"/media/leasing/products/new-holland-t8410-t8410.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland CR10.90', 'CR10.90', 7, 4, 'Производительность 60 т/ч, бак 12500 л', 2022, '4NHCR1090P12345678', 'new', 27000000.00, 13500000.00, 270000.00, 'leased', 'Краснодарский край', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Massey Ferguson 8S.305', '8S.305', 5, 5, 'Мощность 305 л.с., дизель', 2022, '5MF8S305P12345679', 'used', 15500000.00, 7750000.00, 155000.00, 'available', 'Оренбургская область', '"/media/leasing/products/massey-ferguson-8s305-8s305.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш ACROS 595', 'ACROS 595', 7, 6, 'Производительность 25 т/ч, бак 6000 л', 2023, '6RSAC595P12345680', 'new', 8500000.00, 4250000.00, 85000.00, 'available', 'Краснодарский край', '"/media/leasing/products/rostselmash-acros-595-acros-595.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш TORUM 785', 'TORUM 785', 7, 6, 'Производительность 40 т/ч, бак 9500 л', 2022, '6RST785P12345681', 'used', 15000000.00, 7500000.00, 150000.00, 'leased', 'Ростовская область', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш RSM 2375', 'RSM 2375', 5, 6, 'Мощность 375 л.с., колёсная формула 4×4, дизель', 2021, '6RSR2375P12345682', 'used', 12000000.00, 6000000.00, 120000.00, 'available', 'Ставропольский край', '"/media/leasing/products/rostselmash-rsm-2375-rsm-2375.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Кировец K-7M', 'K-7M', 5, 8, 'Мощность 428 л.с., колёсная формула 4×4, дизель', 2022, '8KRK7MP12345683', 'new', 22000000.00, 11000000.00, 220000.00, 'available', 'Воронежская область', '"/media/leasing/products/kirovets-k-7m-k-7m.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Кировец K-744', 'K-744', 6, 8, 'Мощность 420 л.с., дизель', 2021, '8KRK744P12345684', 'used', 18500000.00, 9250000.00, 185000.00, 'leased', 'Липецкая область', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Amazone Ceres 8000', 'Ceres 8000', 9, 9, 'Ширина захвата 6 м, 2 бункера', 2023, '9AMC8000P12345685', 'new', 8500000.00, 4250000.00, 85000.00, 'available', 'Краснодарский край', '"/media/leasing/products/amazone-ceres-8000-ceres-8000.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Horsch Pronto 9 DC', 'Pronto 9 DC', 9, 10, 'Ширина захвата 9 м, 2 бункера', 2022, '10HOP9DCP12345686', 'new', 12000000.00, 6000000.00, 120000.00, 'available', 'Ростовская область', '"/media/leasing/products/horsch-pronto-9-dc-pronto-9-dc.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Kverneland Ecomat', 'Ecomat', 4, 12, 'Ширина захвата 4 м, 5 корпусов плуга', 2021, '12KVE12345687', 'used', 2500000.00, 1250000.00, 25000.00, 'available', 'Ставропольский край', '"/media/leasing/products/kverneland-ecomat-ecomat.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 6M 165', '6M 165', 5, 1, 'Мощность 165 л.с., дизель', 2022, '1JDH6M165P12345688', 'used', 7500000.00, 3750000.00, 75000.00, 'available', 'Волгоградская область', '"/media/leasing/products/john-deere-6m-165-6m-165.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland T6.180', 'T6.180', 5, 4, 'Мощность 180 л.с., дизель', 2021, '4NHT6180P12345689', 'used', 6500000.00, 3250000.00, 65000.00, 'available', 'Саратовская область', '"/media/leasing/products/new-holland-t6180-t6180.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Jaguar 960', 'Jaguar 960', 8, 3, 'Производительность 200 т/ч, длина резки 4 мм', 2022, '3CLAJ960P12345690', 'new', 22000000.00, 11000000.00, 220000.00, 'available', 'Краснодарский край', '"/media/leasing/products/claas-jaguar-960-jaguar-960.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 8500', '8500', 8, 1, 'Производительность 180 т/ч, длина резки 6 мм', 2021, '1JDH8500P12345691', 'used', 18000000.00, 9000000.00, 180000.00, 'leased', 'Ростовская область', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Buhler Versatile 2375', 'Versatile 2375', 5, 11, 'Мощность 375 л.с., дизель', 2020, '11BUV2375P12345692', 'refurbished', 22000000.00, 11000000.00, 220000.00, 'available', 'Самарская область', '"/media/leasing/products/buhler-versatile-2375-versatile-2375.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Massey Ferguson 8737', '8737', 5, 5, 'Мощность 370 л.с., колёсная формула 4×4, дизель', 2022, '5MF8737P12345693', 'used', 16000000.00, 8000000.00, 160000.00, 'available', 'Ульяновская область', '"/media/leasing/products/massey-ferguson-8737-8737.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш Vector 450', 'Vector 450', 7, 6, 'Производительность 20 т/ч, бак 4500 л', 2023, '6RSV450P12345694', 'new', 5500000.00, 2750000.00, 55000.00, 'maintenance', 'Пензенская область', '""'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 6145M', '6145M', 5, 1, 'Мощность 145 л.с., дизель', 2021, '1JDH6145MP12345695', 'used', 5500000.00, 2750000.00, 55000.00, 'available', 'Тамбовская область', '"/media/leasing/products/john-deere-6145m-6145m.jpeg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Arion 640', 'Arion 640', 5, 3, 'Мощность 234 л.с., дизель', 2022, '3CLAA640P12345696', 'new', 12500000.00, 6250000.00, 125000.00, 'available', 'Белгородская область', '"/media/leasing/products/claas-arion-640-arion-640.jpg"'::jsonb, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Договоры лизинга
INSERT INTO lease_contract (contract_number, company_id, equipment_id, start_date, end_date, lease_term_months, total_amount, advance_payment, monthly_payment, payment_day, status, signed_at, signed_by_id, created_by_id, created_at) VALUES
('LG-2026-001', 1, 2, '2026-03-01', '2026-12-31', 10, 27000000.00, 5400000.00, 360000.00, 1, 'active', '2026-03-01 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-002', 1, 3, '2026-04-15', '2026-12-15', 8, 10080000.00, 2016000.00, 224000.00, 15, 'active', '2026-04-10 14:30:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-003', 2, 5, '2026-05-01', '2026-12-31', 8, 25200000.00, 5040000.00, 336000.00, 1, 'active', '2026-05-01 09:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-004', 2, 11, '2026-03-01', '2026-11-30', 9, 9720000.00, 1944000.00, 216000.00, 5, 'active', '2026-03-05 11:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-005', 3, 9, '2026-04-01', '2026-12-31', 9, 19200000.00, 3840000.00, 256000.00, 1, 'active', '2026-04-01 16:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-006', 3, 12, '2026-05-01', '2026-12-31', 8, 9720000.00, 1944000.00, 216000.00, 10, 'active', '2026-05-01 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-007', 4, 15, '2026-03-01', '2026-11-30', 9, 5400000.00, 1080000.00, 120000.00, 1, 'active', '2026-03-02 12:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-008', 5, 17, '2026-04-01', '2026-12-31', 9, 6660000.00, 1332000.00, 148000.00, 15, 'active', '2026-04-02 14:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-009', 1, 4, '2026-05-01', '2026-12-31', 8, 7920000.00, 1584000.00, 176000.00, 1, 'active', '2026-05-02 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-010', 6, 10, '2026-03-01', '2026-11-30', 9, 8640000.00, 1728000.00, 192000.00, 5, 'completed', '2026-03-03 11:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-011', 7, 23, '2026-04-01', '2026-12-31', 9, 6480000.00, 1296000.00, 144000.00, 15, 'active', '2026-04-03 09:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2026-012', 8, 25, '2026-05-01', '2026-12-31', 8, 5760000.00, 1152000.00, 128000.00, 1, 'active', '2026-05-03 14:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2026-013', 9, 20, '2026-03-01', '2026-11-30', 9, 3060000.00, 612000.00, 68000.00, 5, 'active', '2026-03-04 10:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2026-014', 10, 1, '2026-04-01', '2026-12-31', 9, 11100000.00, 2220000.00, 148000.00, 1, 'draft', NULL, NULL, 7, CURRENT_TIMESTAMP),
('LG-2026-015', 11, 7, '2026-05-01', '2026-12-31', 8, 9360000.00, 1872000.00, 208000.00, 1, 'draft', NULL, NULL, 7, CURRENT_TIMESTAMP),
('LG-2026-016', 4, 16, '2026-03-01', '2026-11-30', 9, 4320000.00, 864000.00, 96000.00, 1, 'active', '2026-03-06 16:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-017', 5, 8, '2026-04-01', '2026-12-31', 9, 22800000.00, 4560000.00, 304000.00, 1, 'active', '2026-04-06 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2026-018', 2, 24, '2026-05-01', '2026-12-31', 8, 6480000.00, 1296000.00, 144000.00, 10, 'completed', '2026-05-06 12:00:00+03', 2, 2, CURRENT_TIMESTAMP);

-- Для графика платежей срок оплаты — конец месяца
UPDATE lease_contract SET payment_day = 31;

-- Графики платежей (примеры для нескольких договоров)
INSERT INTO payment_schedule (contract_id, payment_number, due_date, amount, status, paid_at, external_payment_id, penalty_amount) VALUES
(1, 1, '2026-03-31', 360000.00, 'paid', '2026-03-31 10:00:00+03', '318eff86-000f-5001-9000-19b0b0cc6778', 0),
(1, 2, '2026-04-30', 360000.00, 'paid', '2026-04-30 09:00:00+03', '318eff86-000f-5001-9000-19b0b0cc6779', 0),
(1, 3, '2026-05-31', 360000.00, 'pending', NULL, NULL, 0),
(2, 1, '2026-04-30', 224000.00, 'paid', '2026-04-30 10:00:00+03', '318eff86-000f-5001-9000-19b0b0cc6780', 0),
(2, 2, '2026-05-31', 224000.00, 'pending', NULL, NULL, 0),
(3, 1, '2026-05-31', 336000.00, 'pending', NULL, NULL, 0);

-- Заявки на лизинг (для тестовых чатов клиент ↔ менеджер)
INSERT INTO lease_request (equipment_id, account_id, status, message, manager_notes, confirmed_by_id, created_at, updated_at) VALUES
(1, 4, 'pending', 'Нужен трактор к началу сезона, интересует аванс 20%.', '', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(7, 5, 'confirmed', 'Планируем закупку на 3 года, можно ли сдвинуть первый платеж?', 'Согласовали индивидуальный график, ожидаем подписание.', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(15, 6, 'pending', 'Нужна техника в лизинг до конца месяца.', '', NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(20, 4, 'confirmed', 'Готовы к сделке, просим КП и проект договора.', 'Отправлены условия и расчет, клиент подтвердил интерес.', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(15, 8, 'confirmed', 'Нужна поставка и оформление договора по технике в этом месяце.', 'Подтверждено, подготовка договора начата.', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(17, 9, 'confirmed', 'Просьба зафиксировать платеж 15 числа.', 'Согласовано, передано в договор.', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(10, 10, 'confirmed', 'Готовы к подписанию и отгрузке.', 'Подтверждено менеджером.', 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(23, 11, 'confirmed', 'Ожидаем итоговый график платежей.', 'Заявка подтверждена.', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(20, 13, 'confirmed', 'Подтверждаю интерес, прошу оформить договор.', 'Согласованы условия.', 7, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Привязка договоров к заявкам (lease_request_id)
UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 7 AND account_id = 5 LIMIT 1)
WHERE contract_number = 'LG-2026-002';

UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 15 AND account_id = 8 LIMIT 1)
WHERE contract_number = 'LG-2026-007';

UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 17 AND account_id = 9 LIMIT 1)
WHERE contract_number = 'LG-2026-008';

UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 10 AND account_id = 10 LIMIT 1)
WHERE contract_number = 'LG-2026-010';

UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 23 AND account_id = 11 LIMIT 1)
WHERE contract_number = 'LG-2026-011';

UPDATE lease_contract
SET lease_request_id = (SELECT id FROM lease_request WHERE equipment_id = 20 AND account_id = 13 LIMIT 1)
WHERE contract_number = 'LG-2026-013';

-- Сообщения в чатах по заявкам на лизинг
INSERT INTO chat_message (lease_request_id, sender_id, text, created_at) VALUES
((SELECT id FROM lease_request WHERE equipment_id = 1 AND account_id = 4 LIMIT 1), 4, 'Здравствуйте! Хотим оформить John Deere 8R 370, подскажите по срокам рассмотрения.', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 1 AND account_id = 4 LIMIT 1), 2, 'Добрый день! Заявку получили, предварительное решение будет сегодня до 18:00.', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 1 AND account_id = 4 LIMIT 1), 4, 'Отлично, благодарю. Документы готовы, отправлю в течение часа.', CURRENT_TIMESTAMP),

((SELECT id FROM lease_request WHERE equipment_id = 7 AND account_id = 5 LIMIT 1), 5, 'Добрый день, можем уменьшить аванс до 15%?', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 7 AND account_id = 5 LIMIT 1), 2, 'Да, такой вариант возможен. Обновленный расчет уже прикрепили в переписке.', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 7 AND account_id = 5 LIMIT 1), 5, 'Условия подходят, готовы переходить к подписанию.', CURRENT_TIMESTAMP),

((SELECT id FROM lease_request WHERE equipment_id = 15 AND account_id = 6 LIMIT 1), 6, 'Нужна поставка в Ставрополь до 25 числа, это реально?', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 15 AND account_id = 6 LIMIT 1), 7, 'Проверили склад: можем отгрузить до 24 числа, если утвердим договор сегодня.', CURRENT_TIMESTAMP),

((SELECT id FROM lease_request WHERE equipment_id = 20 AND account_id = 4 LIMIT 1), 4, 'Подтвердите, что в графике можно платеж 5-го числа.', CURRENT_TIMESTAMP),
((SELECT id FROM lease_request WHERE equipment_id = 20 AND account_id = 4 LIMIT 1), 7, 'Да, в проекте договора уже указали 5-е число каждого месяца.', CURRENT_TIMESTAMP);

-- Заявки на обслуживание
INSERT INTO maintenance_request (equipment_id, company_id, description, urgency, status, assigned_to_id, completed_at, created_at) VALUES
(1, 1, 'Требуется плановое ТО перед сезоном', 'normal', 'completed', 2, '2026-03-15 14:00:00+03', CURRENT_TIMESTAMP),
(3, 1, 'Замечание по работе молотилки', 'high', 'in_progress', 2, NULL, CURRENT_TIMESTAMP),
(5, 5, 'Неисправность гидравлики', 'critical', 'new', NULL, NULL, CURRENT_TIMESTAMP),
(9, 3, 'Замена ножей режущего аппарата', 'normal', 'completed', 2, '2026-04-01 10:00:00+03', CURRENT_TIMESTAMP),
(15, 4, 'Проверка выгрузного шнека', 'low', 'new', NULL, NULL, CURRENT_TIMESTAMP),
(27, 10, 'Течь масла в редукторе', 'high', 'in_progress', 7, NULL, CURRENT_TIMESTAMP),
(10, 3, 'Плановое сервисное обслуживание', 'normal', 'new', NULL, NULL, CURRENT_TIMESTAMP);

-- Сообщения в чатах по заявкам на ТО
INSERT INTO maintenance_chat_message (maintenance_request_id, sender_id, text, created_at) VALUES
((SELECT id FROM maintenance_request WHERE description = 'Замечание по работе молотилки' LIMIT 1), 4, 'Добрый день. Во время уборки появился посторонний шум в барабане.', CURRENT_TIMESTAMP),
((SELECT id FROM maintenance_request WHERE description = 'Замечание по работе молотилки' LIMIT 1), 2, 'Здравствуйте! Принято. Инженер свяжется с вами сегодня и согласует выезд.', CURRENT_TIMESTAMP),
((SELECT id FROM maintenance_request WHERE description = 'Замечание по работе молотилки' LIMIT 1), 4, 'Спасибо, ожидаем звонок после 15:00.', CURRENT_TIMESTAMP),

((SELECT id FROM maintenance_request WHERE description = 'Неисправность гидравлики' LIMIT 1), 6, 'Техника не поднимает навесное оборудование, работа встала.', CURRENT_TIMESTAMP),
((SELECT id FROM maintenance_request WHERE description = 'Неисправность гидравлики' LIMIT 1), 7, 'Понял, назначаю срочный выезд сервисной бригады на завтра утром.', CURRENT_TIMESTAMP),

((SELECT id FROM maintenance_request WHERE description = 'Течь масла в редукторе' LIMIT 1), 5, 'Обнаружили подтекание масла после смены.', CURRENT_TIMESTAMP),
((SELECT id FROM maintenance_request WHERE description = 'Течь масла в редукторе' LIMIT 1), 7, 'Приняли в работу, подготовьте технику к диагностике в 10:00.', CURRENT_TIMESTAMP),

((SELECT id FROM maintenance_request WHERE description = 'Плановое сервисное обслуживание' LIMIT 1), 6, 'Можно провести сервис в пятницу после 12:00?', CURRENT_TIMESTAMP),
((SELECT id FROM maintenance_request WHERE description = 'Плановое сервисное обслуживание' LIMIT 1), 2, 'Да, записали на пятницу 13:00. Бригада приедет с расходниками.', CURRENT_TIMESTAMP);

-- Журнал аудита
INSERT INTO audit_log (action, table_name, record_id, old_values, new_values, changed_fields, performed_by_id, performed_at) VALUES
('CREATE', 'account', 1, NULL, '{"email": "admin@gmail.com", "username": "admin"}', '["email","username"]'::jsonb, 1, CURRENT_TIMESTAMP),
('LOGIN', 'account', 1, NULL, '{}'::jsonb, '[]'::jsonb, 1, CURRENT_TIMESTAMP),
('CREATE', 'lease_contract', 1, NULL, '{"contract_number": "LG-2026-001"}', '["contract_number"]'::jsonb, 2, CURRENT_TIMESTAMP),
('CREATE', 'lease_contract', 2, NULL, '{"contract_number": "LG-2026-002"}', '["contract_number"]'::jsonb, 2, CURRENT_TIMESTAMP),
('UPDATE', 'lease_contract', 1, NULL, '{"status": "active"}', '["status"]'::jsonb, 2, CURRENT_TIMESTAMP),
('UPDATE', 'payment_schedule', 1, NULL, '{"status": "paid"}', '["status"]'::jsonb, 3, CURRENT_TIMESTAMP),
('UPDATE', 'maintenance_request', 1, NULL, '{"status": "completed"}', '["status"]'::jsonb, 2, CURRENT_TIMESTAMP);
