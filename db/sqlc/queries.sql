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
WHERE now() > next_run
LIMIT 1
FOR NO KEY UPDATE SKIP LOCKED;

-- name: feed_update_now :exec
UPDATE feeds
    SET last_completed = NOW() - feeds.interval - interval '00:05:00'
WHERE rss_url = $1;

-- name: add_feed_history :exec
INSERT INTO feed_history (feed_id, title, link, post_date, unique_id)
    VALUES ($1, $2, $3, $4, $5);

-- name: mark_feed_updates :exec
UPDATE subscriptions
    SET has_notification_pending = true
WHERE feed_id = $1 AND signup_confirmed = false;
