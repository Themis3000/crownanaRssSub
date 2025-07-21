create table subscriptions
(
    subscriber_id     serial                     not null
        constraint subscriptions_pk
            primary key,
    feed_id           integer                    not null
        references feeds(feed_id),
    subscription_time timestamp(0) default NOW() not null,
    confirmation_code integer default random()   not null,
    email             varchar(255)               not null,
    signup_confirmed  boolean default false      not null
);

create index subscriptions_feed_id_index
    on subscriptions (feed_id);

create index email_not_subbed_index
    on subscriptions (email)
    where not subscriptions.signup_confirmed;
