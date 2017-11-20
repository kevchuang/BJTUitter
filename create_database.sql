CREATE DATABASE "BJTUTwitter"
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'fr_FR.UTF-8'
       LC_CTYPE = 'fr_FR.UTF-8'
       CONNECTION LIMIT = -1;

CREATE TABLE public."USER"
(
  lastname text NOT NULL,
  firstname text NOT NULL,
  nickname text,
  gender smallint NOT NULL,
  age smallint,
  mail text NOT NULL,
  login_username text NOT NULL,
  password text NOT NULL,
  user_id SERIAL NOT NULL,
  nb_follow bigint NOT NULL DEFAULT 0,
  CONSTRAINT user_id PRIMARY KEY (user_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."USER"
  OWNER TO postgres;

CREATE TABLE public."POSTS"
(
  post_id SERIAL NOT NULL,
  content text NOT NULL,
  date timestamp without time zone NOT NULL,
  nb_of_likes bigint NOT NULL DEFAULT 0,
  ans_to_post bigint,
  user_id bigint NOT NULL,
  CONSTRAINT post_id PRIMARY KEY (post_id),
  CONSTRAINT ans_to_post_id FOREIGN KEY (post_id)
      REFERENCES public."POSTS" (post_id) MATCH FULL
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT user_id FOREIGN KEY (user_id)
      REFERENCES public."USER" (user_id) MATCH FULL
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."POSTS"
  OWNER TO postgres;

CREATE INDEX fki_user_id
  ON public."POSTS"
  USING btree
  (user_id);


CREATE TABLE public."LIKES"
(
  user_id bigint NOT NULL,
  post_id bigint NOT NULL,
  CONSTRAINT post_id FOREIGN KEY (post_id)
      REFERENCES public."POSTS" (post_id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE CASCADE,
  CONSTRAINT user_id FOREIGN KEY (user_id)
      REFERENCES public."USER" (user_id) MATCH FULL
      ON UPDATE NO ACTION ON DELETE CASCADE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."LIKES"
  OWNER TO postgres;
CREATE INDEX fki_post_id
  ON public."LIKES"
  USING btree
  (post_id);
CREATE INDEX fki_user_id_likes
  ON public."LIKES"
  USING btree
  (user_id);

CREATE TABLE public."FRIENDS"
(
  user_id bigint NOT NULL,
  id_followed bigint NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE public."FRIENDS"
  OWNER TO postgres;
