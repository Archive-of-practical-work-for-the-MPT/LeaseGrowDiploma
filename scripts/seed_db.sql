-- LeaseGrow: заполнение БД тестовыми данными (продакшн-подобными)
-- Админ: admin@gmail.com / adminadmin

-- Роли
INSERT INTO role (name, description, permissions, created_at) VALUES
('admin', 'Администратор системы', '["all"]', CURRENT_TIMESTAMP),
('manager', 'Менеджер лизинга', '["contracts", "companies", "equipment"]', CURRENT_TIMESTAMP),
('accountant', 'Бухгалтер', '["contracts", "payments"]', CURRENT_TIMESTAMP),
('client', 'Клиент (арендатор)', '["own_contracts"]', CURRENT_TIMESTAMP);

-- Аккаунты (admin первым)
INSERT INTO account (email, username, password_hash, role_id, is_active, created_at, updated_at) VALUES
('admin@gmail.com', 'admin', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 1, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

INSERT INTO account (email, username, password_hash, role_id, is_active, created_at, updated_at) VALUES
('ivan.petrov@agro.ru', 'ivan_manager', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('maria.sidorova@leasegrow.ru', 'maria_accountant', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 3, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client1@agrofarm.ru', 'agrofarm_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client2@zemledel.ru', 'zemledel_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('client3@harvest.ru', 'harvest_client', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 4, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('manager2@leasegrow.ru', 'manager2', 'pbkdf2_sha256$1000000$CLaK4xcz2hdbU8VwzF9x6A$sMGJTF3mgmzlGZgpXcDD0YsxhVbddGmKZ6W9iexr8Vw=', 2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Профили
INSERT INTO user_profile (account_id, first_name, last_name, phone, created_at, updated_at) VALUES
(1, 'Админ', 'Системы', '+7 (495) 111-11-11', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(2, 'Иван', 'Петров', '+7 (916) 111-22-22', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(3, 'Мария', 'Сидорова', '+7 (916) 222-33-33', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(4, 'Сергей', 'Кузнецов', '+7 (916) 333-44-44', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(5, 'Андрей', 'Морозов', '+7 (916) 444-55-55', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(6, 'Елена', 'Волкова', '+7 (916) 555-66-66', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
(7, 'Дмитрий', 'Соколов', '+7 (916) 666-77-77', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- API токен для админа (64 hex символа)
INSERT INTO account_token (key, account_id, created_at) VALUES
('a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2', 1, CURRENT_TIMESTAMP);

-- Компании
INSERT INTO company (name, inn, ogrn, address, phone, email, status, account_id, created_at) VALUES
('ООО Агроферма Юг', '7707123456', '1027700123456', 'г. Краснодар, ул. Промышленная, 1', '+7 (861) 200-11-11', 'info@agrofarm.ru', 'active', 4, CURRENT_TIMESTAMP),
('ООО Земледел', '7708234567', '1027700234567', 'г. Ростов-на-Дону, пр. Будённовский, 50', '+7 (863) 250-22-22', 'office@zemledel.ru', 'active', 5, CURRENT_TIMESTAMP),
('АО Урожай Плюс', '7709345678', '1027700345678', 'г. Ставрополь, ул. Мира, 100', '+7 (865) 230-33-33', 'contact@harvest.ru', 'active', 6, CURRENT_TIMESTAMP),
('ООО Нива Кубани', '7710456789', '1027700456789', 'Краснодарский край, г. Тихорецк, ул. Ленина, 20', '+7 (861) 510-44-44', 'niva@kuban.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ПАО ЮгАгро', '7711567890', '1027700567890', 'г. Ростов-на-Дону, ул. Большая Садовая, 1', '+7 (863) 300-55-55', 'info@yugagro.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Чернозём', '7712678901', '1027700678901', 'г. Воронеж, пр. Революции, 25', '+7 (473) 255-66-66', 'chernozem@vrn.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Поле России', '7713789012', '1027700789012', 'г. Волгоград, ул. Рабоче-Крестьянская, 10', '+7 (844) 230-77-77', 'pole@volgograd.ru', 'active', NULL, CURRENT_TIMESTAMP),
('АО Колос', '7714890123', '1027700890123', 'г. Саратов, ул. Московская, 50', '+7 (845) 220-88-88', 'kolos@saratov.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Степь', '7715901234', '1027700901234', 'г. Оренбург, ул. Советская, 30', '+7 (353) 275-99-99', 'step@orenburg.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО АгроСоюз', '7716012345', '1027701012345', 'г. Самара, ул. Куйбышева, 100', '+7 (846) 260-00-00', 'agro@samara.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Волга-Агро', '7717123456', '1027701123456', 'г. Ульяновск, ул. Гончарова, 40', '+7 (842) 240-11-11', 'volga@ulsk.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Поволжье', '7718234567', '1027701234567', 'г. Пенза, пр. Строителей, 1', '+7 (841) 250-22-22', 'povolzhye@pnz.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО РусьАгро', '7719345678', '1027701345678', 'г. Липецк, пр. Победы, 80', '+7 (474) 270-33-33', 'rus@lipetsk.ru', 'active', NULL, CURRENT_TIMESTAMP),
('АО ЦентрАгро', '7720456789', '1027701456789', 'г. Тамбов, ул. Советская, 100', '+7 (475) 250-44-44', 'centre@tambov.ru', 'active', NULL, CURRENT_TIMESTAMP),
('ООО Черноземье', '7721567890', '1027701567890', 'г. Белгород, пр. Славы, 50', '+7 (472) 260-55-55', 'chernozem@belgorod.ru', 'pending', NULL, CURRENT_TIMESTAMP);

-- Категории техники (иерархия)
INSERT INTO equipment_category (name, parent_id, description, created_at) VALUES
('Тракторы', NULL, 'Колёсные и гусеничные тракторы', CURRENT_TIMESTAMP),
('Комбайны', NULL, 'Зерноуборочные и кормоуборочные комбайны', CURRENT_TIMESTAMP),
('Посевная техника', NULL, 'Сеялки и посадочные машины', CURRENT_TIMESTAMP),
('Плуги и культиваторы', NULL, 'Орудия обработки почвы', CURRENT_TIMESTAMP);

INSERT INTO equipment_category (name, parent_id, description, created_at) VALUES
('Колёсные тракторы', 1, NULL, CURRENT_TIMESTAMP),
('Гусеничные тракторы', 1, NULL, CURRENT_TIMESTAMP),
('Зерноуборочные комбайны', 2, NULL, CURRENT_TIMESTAMP),
('Кормоуборочные комбайны', 2, NULL, CURRENT_TIMESTAMP),
('Пневматические сеялки', 3, NULL, CURRENT_TIMESTAMP),
('Дисковые сеялки', 3, NULL, CURRENT_TIMESTAMP);

-- Производители
INSERT INTO manufacturer (name, country, website, description) VALUES
('John Deere', 'США', 'https://www.deere.com', 'Крупнейший производитель сельхозтехники'),
('Case IH', 'США', 'https://www.caseih.com', 'Производитель тракторов и комбайнов'),
('CLAAS', 'Германия', 'https://www.claas.com', 'Европейский лидер в производстве комбайнов'),
('New Holland', 'Италия', 'https://www.newholland.com', 'Производитель тракторов и комбайнов'),
('AGCO (Massey Ferguson)', 'США', 'https://www.agcocorp.com', 'Производитель сельхозтехники'),
('Kubota', 'Япония', 'https://www.kubota.com', 'Японский производитель тракторов и мини-техники'),
('Ростсельмаш', 'Россия', 'https://www.rostselmash.ru', 'Отечественный производитель'),
('Кировец', 'Россия', 'https://www.kzgroup.ru', 'Тракторы Кировец'),
('Amazone', 'Германия', 'https://www.amazone.net', 'Посевная и почвообрабатывающая техника'),
('Horsch', 'Германия', 'https://www.horsch.com', 'Сеялки и опрыскиватели'),
('Бuhler', 'Германия', 'https://www.buhler.com', 'Зернообработка и техника'),
('Kverneland', 'Норвегия', 'https://www.kvernelandgroup.com', 'Плуги и почвообработка');

-- Техника (много единиц)
INSERT INTO equipment (name, model, category_id, manufacturer_id, specifications, year, vin, condition, price, residual_value, monthly_lease_rate, status, location, created_at, updated_at) VALUES
('John Deere 8R 370', '8R 370', 5, 1, 'Мощность 370 л.с., дизель', 2023, '1JDH8R370P1234567', 'new', 18500000.00, 9250000.00, 185000.00, 'available', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 9RX 640', '9RX 640', 6, 1, 'Мощность 640 л.с., дизель', 2022, '1JDH9RX640P1234568', 'new', 45000000.00, 22500000.00, 450000.00, 'leased', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere S790', 'S790', 7, 1, 'Производительность 70 т/ч, бак 12000 л', 2023, '1JDHS790P1234569', 'new', 28000000.00, 14000000.00, 280000.00, 'available', 'Ростовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere S680', 'S680', 7, 1, 'Производительность 55 т/ч, бак 10200 л', 2022, '1JDHS680P1234570', 'used', 22000000.00, 11000000.00, 220000.00, 'available', 'Ставропольский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Steiger 580 HD', 'Steiger 580 HD', 6, 2, 'Мощность 580 л.с., дизель', 2023, '2CSI580HD12345671', 'new', 42000000.00, 21000000.00, 420000.00, 'leased', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Magnum 340', 'Magnum 340', 5, 2, 'Мощность 340 л.с., дизель', 2022, '2CSIM34012345672', 'used', 16500000.00, 8250000.00, 165000.00, 'available', 'Воронежская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Case IH Axial-Flow 8250', 'Axial-Flow 8250', 7, 2, 'Производительность 65 т/ч, бак 11500 л', 2023, '2CSIAF825012345673', 'new', 26000000.00, 13000000.00, 260000.00, 'available', 'Ростовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Xerion 5000', 'Xerion 5000', 5, 3, 'Мощность 493 л.с., дизель', 2022, '3CLAX5000P12345674', 'new', 38000000.00, 19000000.00, 380000.00, 'available', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Lexion 8900', 'Lexion 8900', 7, 3, 'Производительность 75 т/ч, бак 13500 л', 2023, '3CLAL8900P12345675', 'new', 32000000.00, 16000000.00, 320000.00, 'leased', 'Ставропольский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Lexion 780', 'Lexion 780', 7, 3, 'Производительность 55 т/ч, бак 10500 л', 2021, '3CLAL780P12345676', 'used', 24000000.00, 12000000.00, 240000.00, 'available', 'Волгоградская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland T8.410', 'T8.410', 5, 4, 'Мощность 410 л.с., дизель', 2023, '4NHT8410P12345677', 'new', 21000000.00, 10500000.00, 210000.00, 'available', 'Саратовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland CR10.90', 'CR10.90', 7, 4, 'Производительность 60 т/ч, бак 12500 л', 2022, '4NHCR1090P12345678', 'new', 27000000.00, 13500000.00, 270000.00, 'leased', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Massey Ferguson 8S.305', '8S.305', 5, 5, 'Мощность 305 л.с., дизель', 2022, '5MF8S305P12345679', 'used', 15500000.00, 7750000.00, 155000.00, 'available', 'Оренбургская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш ACROS 595', 'ACROS 595', 7, 6, 'Производительность 25 т/ч, бак 6000 л', 2023, '6RSAC595P12345680', 'new', 8500000.00, 4250000.00, 85000.00, 'available', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш TORUM 785', 'TORUM 785', 7, 6, 'Производительность 40 т/ч, бак 9500 л', 2022, '6RST785P12345681', 'used', 15000000.00, 7500000.00, 150000.00, 'leased', 'Ростовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш RSM 2375', 'RSM 2375', 7, 6, 'Производительность 35 т/ч, бак 8000 л', 2021, '6RSR2375P12345682', 'used', 12000000.00, 6000000.00, 120000.00, 'available', 'Ставропольский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Кировец K-7M', 'K-7M', 6, 8, 'Мощность 428 л.с., дизель', 2022, '8KRK7MP12345683', 'new', 22000000.00, 11000000.00, 220000.00, 'available', 'Воронежская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Кировец K-744', 'K-744', 6, 8, 'Мощность 420 л.с., дизель', 2021, '8KRK744P12345684', 'used', 18500000.00, 9250000.00, 185000.00, 'leased', 'Липецкая область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Amazone Ceres 8000', 'Ceres 8000', 9, 9, 'Ширина захвата 6 м, 2 бункера', 2023, '9AMC8000P12345685', 'new', 8500000.00, 4250000.00, 85000.00, 'available', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Horsch Pronto 9 DC', 'Pronto 9 DC', 9, 10, 'Ширина захвата 9 м, 2 бункера', 2022, '10HOP9DCP12345686', 'new', 12000000.00, 6000000.00, 120000.00, 'available', 'Ростовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Kverneland Ecomat', 'Ecomat', 4, 12, 'Ширина захвата 4 м, 5 корпусов плуга', 2021, '12KVE12345687', 'used', 2500000.00, 1250000.00, 25000.00, 'available', 'Ставропольский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 6M 165', '6M 165', 5, 1, 'Мощность 165 л.с., дизель', 2022, '1JDH6M165P12345688', 'used', 7500000.00, 3750000.00, 75000.00, 'available', 'Волгоградская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('New Holland T6.180', 'T6.180', 5, 4, 'Мощность 180 л.с., дизель', 2021, '4NHT6180P12345689', 'used', 6500000.00, 3250000.00, 65000.00, 'available', 'Саратовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Jaguar 960', 'Jaguar 960', 8, 3, 'Производительность 200 т/ч, длина резки 4 мм', 2022, '3CLAJ960P12345690', 'new', 22000000.00, 11000000.00, 220000.00, 'available', 'Краснодарский край', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 8500', '8500', 8, 1, 'Производительность 180 т/ч, длина резки 6 мм', 2021, '1JDH8500P12345691', 'used', 18000000.00, 9000000.00, 180000.00, 'leased', 'Ростовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Buhler Versatile 2375', 'Versatile 2375', 5, 11, 'Мощность 375 л.с., дизель', 2020, '11BUV2375P12345692', 'refurbished', 22000000.00, 11000000.00, 220000.00, 'available', 'Самарская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Massey Ferguson 8737', '8737', 7, 5, 'Производительность 45 т/ч, бак 9000 л', 2022, '5MF8737P12345693', 'used', 16000000.00, 8000000.00, 160000.00, 'available', 'Ульяновская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('Ростсельмаш Vector 450', 'Vector 450', 7, 6, 'Производительность 20 т/ч, бак 4500 л', 2023, '6RSV450P12345694', 'new', 5500000.00, 2750000.00, 55000.00, 'maintenance', 'Пензенская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('John Deere 6145M', '6145M', 5, 1, 'Мощность 145 л.с., дизель', 2021, '1JDH6145MP12345695', 'used', 5500000.00, 2750000.00, 55000.00, 'available', 'Тамбовская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('CLAAS Arion 640', 'Arion 640', 5, 3, 'Мощность 234 л.с., дизель', 2022, '3CLAA640P12345696', 'new', 12500000.00, 6250000.00, 125000.00, 'available', 'Белгородская область', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Договоры лизинга
INSERT INTO lease_contract (contract_number, company_id, equipment_id, start_date, end_date, lease_term_months, total_amount, advance_payment, monthly_payment, payment_day, status, signed_at, signed_by_id, created_by_id, created_at) VALUES
('LG-2023-001', 1, 2, '2023-03-01', '2028-02-28', 60, 27000000.00, 5400000.00, 360000.00, 1, 'active', '2023-02-25 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-002', 1, 3, '2023-04-15', '2026-04-14', 36, 10080000.00, 2016000.00, 224000.00, 15, 'active', '2023-04-10 14:30:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-003', 2, 5, '2023-05-01', '2028-04-30', 60, 25200000.00, 5040000.00, 336000.00, 1, 'active', '2023-04-28 09:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-004', 2, 11, '2023-06-01', '2026-05-31', 36, 9720000.00, 1944000.00, 216000.00, 5, 'active', '2023-05-25 11:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-005', 3, 9, '2023-07-01', '2028-06-30', 60, 19200000.00, 3840000.00, 256000.00, 1, 'active', '2023-06-28 16:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-006', 3, 12, '2023-08-01', '2026-07-31', 36, 9720000.00, 1944000.00, 216000.00, 10, 'active', '2023-07-29 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-007', 4, 15, '2023-09-01', '2026-08-31', 36, 5400000.00, 1080000.00, 120000.00, 1, 'active', '2023-08-28 12:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-008', 5, 17, '2023-10-01', '2026-09-30', 36, 6660000.00, 1332000.00, 148000.00, 15, 'active', '2023-09-27 14:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2022-001', 1, 4, '2022-04-01', '2025-03-31', 36, 7920000.00, 1584000.00, 176000.00, 1, 'active', '2022-03-28 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2022-002', 6, 10, '2022-06-01', '2025-05-31', 36, 8640000.00, 1728000.00, 192000.00, 5, 'completed', '2022-05-28 11:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2024-001', 7, 23, '2024-01-15', '2027-01-14', 36, 6480000.00, 1296000.00, 144000.00, 15, 'active', '2024-01-10 09:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2024-002', 8, 25, '2024-02-01', '2027-01-31', 36, 5760000.00, 1152000.00, 128000.00, 1, 'active', '2024-01-28 14:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2024-003', 9, 20, '2024-03-01', '2027-02-28', 36, 3060000.00, 612000.00, 68000.00, 5, 'active', '2024-02-26 10:00:00+03', 7, 7, CURRENT_TIMESTAMP),
('LG-2024-004', 10, 1, '2024-04-01', '2029-03-31', 60, 11100000.00, 2220000.00, 148000.00, 1, 'draft', NULL, NULL, 7, CURRENT_TIMESTAMP),
('LG-2024-005', 11, 7, '2024-05-01', '2027-04-30', 36, 9360000.00, 1872000.00, 208000.00, 1, 'draft', NULL, NULL, 7, CURRENT_TIMESTAMP),
('LG-2023-009', 4, 16, '2023-11-01', '2026-10-31', 36, 4320000.00, 864000.00, 96000.00, 1, 'active', '2023-10-28 16:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2023-010', 5, 8, '2023-12-01', '2028-11-30', 60, 22800000.00, 4560000.00, 304000.00, 1, 'active', '2023-11-27 10:00:00+03', 2, 2, CURRENT_TIMESTAMP),
('LG-2022-003', 2, 24, '2022-09-01', '2025-08-31', 36, 6480000.00, 1296000.00, 144000.00, 10, 'completed', '2022-08-28 12:00:00+03', 2, 2, CURRENT_TIMESTAMP);

-- Графики платежей (примеры для нескольких договоров)
INSERT INTO payment_schedule (contract_id, payment_number, due_date, amount, status, paid_at, penalty_amount) VALUES
(1, 1, '2023-03-01', 360000.00, 'paid', '2023-03-01 10:00:00+03', 0),
(1, 2, '2023-04-01', 360000.00, 'paid', '2023-04-01 09:00:00+03', 0),
(1, 3, '2023-05-01', 360000.00, 'paid', '2023-05-01 11:00:00+03', 0),
(1, 4, '2023-06-01', 360000.00, 'paid', '2023-06-01 10:00:00+03', 0),
(1, 5, '2023-07-01', 360000.00, 'paid', '2023-07-02 14:00:00+03', 0),
(1, 6, '2023-08-01', 360000.00, 'paid', '2023-08-01 10:00:00+03', 0),
(1, 7, '2023-09-01', 360000.00, 'paid', '2023-09-01 09:30:00+03', 0),
(1, 8, '2023-10-01', 360000.00, 'paid', '2023-10-01 10:00:00+03', 0),
(1, 9, '2023-11-01', 360000.00, 'paid', '2023-11-01 11:00:00+03', 0),
(1, 10, '2023-12-01', 360000.00, 'paid', '2023-12-01 10:00:00+03', 0),
(1, 11, '2024-01-01', 360000.00, 'paid', '2024-01-02 09:00:00+03', 0),
(1, 12, '2024-02-01', 360000.00, 'paid', '2024-02-01 10:00:00+03', 0),
(1, 13, '2024-03-01', 360000.00, 'paid', '2024-03-01 11:00:00+03', 0),
(1, 14, '2024-04-01', 360000.00, 'pending', NULL, 0),
(1, 15, '2024-05-01', 360000.00, 'pending', NULL, 0),
(2, 1, '2023-04-15', 224000.00, 'paid', '2023-04-15 10:00:00+03', 0),
(2, 2, '2023-05-15', 224000.00, 'paid', '2023-05-15 09:00:00+03', 0),
(2, 3, '2023-06-15', 224000.00, 'paid', '2023-06-15 10:00:00+03', 0),
(2, 4, '2023-07-15', 224000.00, 'pending', NULL, 0),
(3, 1, '2023-05-01', 336000.00, 'paid', '2023-05-01 10:00:00+03', 0),
(3, 2, '2023-06-01', 336000.00, 'paid', '2023-06-01 11:00:00+03', 0),
(3, 3, '2023-07-01', 336000.00, 'paid', '2023-07-01 09:00:00+03', 0),
(3, 4, '2023-08-01', 336000.00, 'pending', NULL, 0);

-- Заявки на обслуживание
INSERT INTO maintenance_request (equipment_id, company_id, description, urgency, status, assigned_to_id, completed_at, created_at) VALUES
(1, 1, 'Требуется плановое ТО перед сезоном', 'normal', 'completed', 2, '2024-01-15 14:00:00+03', CURRENT_TIMESTAMP),
(3, 1, 'Замечание по работе молотилки', 'high', 'in_progress', 2, NULL, CURRENT_TIMESTAMP),
(5, 5, 'Неисправность гидравлики', 'critical', 'new', NULL, NULL, CURRENT_TIMESTAMP),
(9, 3, 'Замена ножей режущего аппарата', 'normal', 'completed', 2, '2024-02-01 10:00:00+03', CURRENT_TIMESTAMP),
(15, 4, 'Проверка выгрузного шнека', 'low', 'new', NULL, NULL, CURRENT_TIMESTAMP),
(27, 10, 'Течь масла в редукторе', 'high', 'in_progress', 7, NULL, CURRENT_TIMESTAMP),
(10, 3, 'Плановое сервисное обслуживание', 'normal', 'new', NULL, NULL, CURRENT_TIMESTAMP);

-- Журнал аудита
INSERT INTO audit_log (action, table_name, record_id, new_values, performed_by_id, performed_at) VALUES
('CREATE', 'account', 1, '{"email": "admin@gmail.com", "username": "admin"}', 1, CURRENT_TIMESTAMP),
('LOGIN', 'account', 1, '{}', 1, CURRENT_TIMESTAMP),
('CREATE', 'lease_contract', 1, '{"contract_number": "LG-2023-001"}', 2, CURRENT_TIMESTAMP),
('CREATE', 'lease_contract', 2, '{"contract_number": "LG-2023-002"}', 2, CURRENT_TIMESTAMP),
('UPDATE', 'lease_contract', 1, '{"status": "active"}', 2, CURRENT_TIMESTAMP),
('UPDATE', 'payment_schedule', 1, '{"status": "paid"}', 3, CURRENT_TIMESTAMP),
('UPDATE', 'maintenance_request', 1, '{"status": "completed"}', 2, CURRENT_TIMESTAMP);
