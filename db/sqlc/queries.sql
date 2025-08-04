-- name: get_feed :one
SELECT * from feeds
WHERE feed_id = $1;

-- name: get_feed_by_rss :one
SELECT * from feeds
WHERE rss_url = $1 LIMIT 1;

-- name: list_feeds :many
SELECT * from feeds
ORDER BY feed_id;

-- name: create_feed :one
INSERT INTO feeds (rss_url, feed_name)
VALUES ($1, $2)
RETURNING *;

-- name: feed_set_last_check_now :exec
UPDATE feeds
    set last_completed = NOW(),
        consecutive_failures = 0
WHERE feed_id = $1;

-- name: feed_set_last_fail_now :exec
UPDATE feeds
    set last_completed = NOW(),
        consecutive_failures = consecutive_failures + 1
WHERE feed_id = $1;

-- name: add_subscriber :one
INSERT INTO subscriptions (feed_id, email, notification_interval, last_post_notify)
VALUES ($1, $2, $3, (
        SELECT feed_history.history_id FROM feed_history
        WHERE feed_history.feed_id = $1
        ORDER BY post_date desc
        LIMIT 1
    ))
returning *;

-- name: get_subscriber :one
SELECT * from subscriptions
WHERE subscriber_id = $1 LIMIT 1;

-- name: subscriber_exists :one
SELECT exists(SELECT * FROM subscriptions WHERE subscriber_id = $1) AS sub_exists;

-- name: confirm_subscription :exec
UPDATE subscriptions
    set signup_confirmed = TRUE
WHERE subscriber_id = $1;

-- name: remove_subscription :exec
DELETE FROM subscriptions
WHERE subscriber_id = $1;

-- name: get_feed_to_run :one
SELECT feeds.feed_id, post_date, unique_id, rss_url
FROM feeds JOIN feed_history ON feeds.feed_id = feed_history.feed_id
WHERE now() > next_run
ORDER BY post_date desc
LIMIT 1
FOR NO KEY UPDATE SKIP LOCKED;

-- name: feed_update_now :exec
UPDATE feeds
    SET last_completed = NOW() - feeds.interval - interval '00:05:00'
WHERE rss_url = $1;

-- name: sub_notify_now :exec
UPDATE subscriptions
    SET last_notification_time = NOW() - subscriptions.notification_interval - interval '00:05:00'
WHERE subscriber_id = $1;

-- name: add_feed_history :exec
INSERT INTO feed_history (feed_id, title, link, post_date, unique_id)
    VALUES ($1, $2, $3, $4, $5);

-- name: mark_feed_updates :exec
UPDATE subscriptions
    SET has_notification_pending = true
WHERE feed_id = $1 AND signup_confirmed = true;

-- name: get_feed_history :many
SELECT * FROM feed_history
WHERE feed_id = $1
ORDER BY post_date desc
LIMIT $2;

-- name: get_feed_history_since_date :many
SELECT * FROM feed_history
WHERE feed_id = $1 AND post_date > $2
ORDER BY post_date desc
LIMIT $3;

-- name: get_feed_history_since_id :many
SELECT * from feed_history
WHERE feed_history.feed_id = $1 AND post_date > (
        SELECT post_date from feed_history
        WHERE feed_history.history_id = $2
    )
ORDER BY post_date desc
LIMIT $3;

-- name: find_notify_mark_updating_subs :many
UPDATE subscriptions
    SET is_being_processed = true,
        last_process_update = NOW()
FROM feeds
WHERE subscriber_id IN (
    SELECT subscriber_id
    FROM subscriptions
    WHERE has_notification_pending = true AND
          NOW() > next_notification AND
          signup_confirmed = true AND
          (not is_being_processed OR last_process_update > NOW() + interval '00:05:00')
    ORDER BY subscriptions.feed_id
    LIMIT $1
    FOR NO KEY UPDATE SKIP LOCKED
    ) AND
    subscriptions.feed_id = feeds.feed_id
RETURNING subscriber_id, subscriptions.feed_id, last_post_notify, email, confirmation_code, feed_name, last_process_update;

-- name: mark_subscriber_notified :exec
UPDATE subscriptions
    SET has_notification_pending = false,
        last_post_notify = $2,
        last_notification_time = NOW(),
        is_being_processed = false
WHERE subscriber_id = $1;

-- name: get_current_post :one
SELECT * FROM feed_history
WHERE feed_id = $1
ORDER BY post_date desc
LIMIT 1;

-- name: post_id_exists :one
SELECT EXISTS(
    SELECT FROM feed_history
    WHERE feed_id = $1 AND unique_id = $2
);
