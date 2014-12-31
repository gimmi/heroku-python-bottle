-- run thi script with
-- psql --set ON_ERROR_STOP=on -U postgres < schema.sql

create database hrp;

\connect hrp

create table users(
   id uuid not null, 
   name varchar(50) not null, 
   password varchar(50), 
   constraint pk_users primary key (id)
);
