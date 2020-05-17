
create table category(
    user_id integer,
    name varchar(255),
    aliases text
);

create table expense(
    user_id integer,
    id integer primary key,
    amount integer,
    created datetime,
    category_name varchar(255),
    raw_text text,
    alias varchar(255)
);
