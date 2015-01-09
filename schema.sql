-- run thi script with
-- psql --set ON_ERROR_STOP=on -U postgres < schema.sql

create database hrp;

\connect hrp

create table users(
   id uuid not null, 
   name varchar(50) not null unique,
   password varchar(50), 
   constraint pk_users primary key (id)
);

insert into users(id, name, password) values('2e6f03e0-910c-11e4-b4a9-0800200c9a66', 'gimmi', 'secret');
INSERT INTO users (id, name, password) VALUES ('2e6f03e1-910c-11e4-b4a9-0800200c9a66', 'elena', 'secret');

create table expense_categories(
   id uuid not null,
   name varchar(50) not null unique,
   constraint pk_expense_categories primary key (id)
);

insert into expense_categories(id, name) values('432574c0-983e-11e4-bd06-0800200c9a66', 'casa');
insert into expense_categories(id, name) values('432574c1-983e-11e4-bd06-0800200c9a66', 'tasse');

create table expenses(
   id uuid not null,
   date date not null,
   gimmi_amount decimal(13,2) not null,
   elena_amount decimal(13,2) not null,
   gimmi_debt decimal(13,2) not null,
   elena_debt decimal(13,2) not null,
   description varchar(255) null,
   category_id uuid not null references expense_categories(id),
   constraint pk_expenses primary key (id)
);
