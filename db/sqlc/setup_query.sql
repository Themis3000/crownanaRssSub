create table feeds
    (
        feed_id                   serial                                   not null
            constraint feeds_pk
                primary key,
        rss_url                   varchar(2000)                            not null
            constraint rss_url_key
                unique,
        feed_name                 varchar(2000)                            not null,
        addition_date             timestamp(0) default NOW()               not null,
        interval                  interval     default interval '12 hours' not null,
        last_completed            timestamp(0) default NOW()               not null,
        consecutive_failures      integer      default 0                   not null,

        next_run                  timestamp(0) generated always as ( last_completed + interval ) stored not null
    );

create index next_run_index
    on feeds (next_run desc);

create table feed_history
    (
        history_id      serial not null            not null
            constraint feed_history_pk
                primary key,
        feed_id         integer                    not null
            references feeds(feed_id),
        title           varchar(2000)              not null,
        link            varchar(2000)              not null,
        post_date       timestamptz(0)             not null,
        collection_date timestamp(0) default NOW() not null,
        unique_id       varchar(255)               not null,
        UNIQUE (unique_id, feed_id)
);

create index feed_history_post_date_index
    on feed_history (post_date desc);

create table subscriptions
    (
        subscriber_id            serial                                     not null
            constraint subscriptions_pk
                primary key,
        feed_id                  integer                                    not null
            references feeds(feed_id),
        subscription_time        timestamp(0) default NOW()                 not null,
        confirmation_code        float        default random()              not null,
        email                    varchar(255)                               not null,
        signup_confirmed         boolean      default false                 not null,
        last_post_notify         integer                                    not null
            references feed_history(history_id),
        has_notification_pending boolean      default false                 not null,
        last_notification_time   timestamp(0) default NOW()                 not null,
        notification_interval    interval     default interval '12 hours'   not null,
        next_notification        timestamp(0) generated always as ( last_notification_time + notification_interval ) stored not null,
--         Stores if the subscriber is currently being processed by a worker
--         Together with the time field meant to work like a more different lock
        is_being_processed       boolean      default false                 not null,
        last_process_update      timestamp(0) default '2000-01-01 00:00:00' not null,
        UNIQUE (feed_id, email)
    );

create index subscriptions_feed_id_index
    on subscriptions (feed_id);

create index email_not_subbed_index
    on subscriptions (email)
    where not subscriptions.signup_confirmed;

create index subscriptions_signup_index
    on subscriptions (signup_confirmed);
