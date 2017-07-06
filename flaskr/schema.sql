drop table if exists posts;
create table posts (
  id integer primary key autoincrement,
	title text not null,
	slug text not null,
	'text' text not null,
	published integer not null,
	publish_date text,
	constraint c unique(slug)
);

drop table if exists tags;
create table tags (
	id integer primary key autoincrement,
	label text unique not null
);

drop table if exists tagmap;
create table tagmap (
	post_id integer,
	tag_id integer,
	foreign key(post_id) references posts(id),
	foreign key(tag_id) references tags(id),
	constraint c unique(post_id, tag_id)
);

drop table if exists media;
create table media (
	id integer primary key autoincrement,
	filename text not null,
	filetype text not null,
	title text,
	description text
);
