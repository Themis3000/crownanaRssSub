create table feeds
    (
        feed_id        serial                                   not null
            constraint feeds_pk
                primary key,
        rss_url        varchar(2000)                            not null
            constraint rss_url_key
                unique,
        feed_name      varchar(2000)                            not null,
        addition_date  timestamp(0) default NOW()               not null,
        interval       interval     default interval '12 hours' not null,
        last_completed timestamp(0) default NOW()               not null,
        last_update    timestamp(0) default NOW()               not null,
        last_post_id   varchar(255)                             not null,
        last_post_pub  timestamp(0)                             not null,

        next_run timestamp(0) generated always as ( last_completed + interval ) stored,
        unresolved_notification boolean default FALSE not null
    );

create index next_run_index
    on feeds (next_run desc);

create table subscriptions
    (
        subscriber_id     serial                            not null
            constraint subscriptions_pk
                primary key,
        feed_id           integer                           not null
            references feeds(feed_id),
        subscription_time timestamp(0) default NOW()        not null,
        confirmation_code float        default random()     not null,
        email             varchar(255)                      not null,
        signup_confirmed  boolean      default false        not null,
        last_post_id      varchar(255) default ''           not null,
        UNIQUE (feed_id, email)
    );

create index subscriptions_feed_id_index
    on subscriptions (feed_id);

create index email_not_subbed_index
    on subscriptions (email)
    where not subscriptions.signup_confirmed;
