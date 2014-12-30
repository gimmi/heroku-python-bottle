create database prova
  with owner = postgres
       encoding = 'UTF8'
       tablespace = pg_default
       lc_collate = 'C'
       lc_ctype = 'C'
       connection limit = -1;

create table users(
   id uuid not null, 
   name character varying(50) collate pg_catalog."c" not null, 
   password character varying(50) collate pg_catalog."c", 
   constraint pk_users primary key (id)
)
