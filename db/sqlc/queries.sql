-- name: get_feed :one
SELECT * from feeds
WHERE feed_id = $1 LIMIT 1;

-- name: get_feed_by_rss :one
SELECT * from feeds
WHERE rss_url = $1 LIMIT 1;

-- name: list_feeds :many
SELECT * from feeds
ORDER BY feed_id;

-- name: create_feed :one
INSERT INTO feeds (rss_url, feed_name, last_post_id, last_notification_post_id, last_post_pub)
VALUES ($1, $2, $3, $3, $4)
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

-- name: set_feed_update :one
UPDATE feeds
    set last_update = now(),
        last_completed = now(),
        last_notification_post_id = last_post_id,
        last_notification_pub = last_post_pub,
        last_post_id = $2,
        last_post_pub = $3,
        unresolved_notification = true
WHERE feed_id = $1
RETURNING *;

-- name: add_subscriber :one
INSERT INTO subscriptions (feed_id, email)
VALUES ($1, $2)
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
SELECT * from feeds
WHERE next_run > now() AND not unresolved_notification
LIMIT 1
FOR NO KEY UPDATE SKIP LOCKED;

-- name: get_unresolved_feed :one
SELECT * from feeds
WHERE unresolved_notification
LIMIT 1;

-- name: resolve_feed_notifications :exec
UPDATE feeds
    set unresolved_notification = false
WHERE feed_id = $1;

-- name: fetch_and_update_uncurrent_sub :one
UPDATE subscriptions
    set last_post_id = $1
WHERE last_post_id != $1 AND feed_id = $2
RETURNING *;

-- name: feed_update_now :exec
UPDATE feeds
    SET last_completed = NOW() - feeds.interval - interval '00:00:01'
WHERE rss_url = $1;
