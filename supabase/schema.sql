create table if not exists banks (
  id bigint generated always as identity primary key,
  name text not null unique,
  official_campaign_url text
);
create table if not exists categories (
  id bigint generated always as identity primary key,
  name text not null unique
);
create table if not exists campaigns (
  id bigint generated always as identity primary key,
  bank_id bigint not null references banks(id),
  title text not null,
  description text,
  category_id bigint references categories(id),
  merchant text,
  reward_type text,
  reward_amount numeric,
  reward_percent numeric,
  min_spend numeric,
  max_reward numeric,
  required_transactions integer,
  requires_join boolean default false,
  start_date date,
  end_date date,
  source_url text not null,
  source_checked_at timestamptz default now(),
  is_active boolean default true
);
create or replace view active_campaigns as
select * from campaigns
where is_active = true
and (start_date is null or start_date <= current_date)
and (end_date is null or end_date >= current_date);
insert into categories(name) values
('Akaryakıt'),('Market'),('Restoran'),('Giyim'),('Seyahat'),('Elektronik')
on conflict (name) do nothing;
