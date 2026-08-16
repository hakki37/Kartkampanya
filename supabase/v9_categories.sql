insert into categories (id, name) values
(1, 'Akaryakıt'),
(2, 'Market'),
(3, 'Restoran'),
(4, 'Giyim'),
(5, 'Seyahat'),
(6, 'Elektronik'),
(7, 'E-ticaret'),
(8, 'Eğlence'),
(9, 'Ev & Yaşam'),
(10, 'Sağlık')
on conflict (id) do update set name = excluded.name;
