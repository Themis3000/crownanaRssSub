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
INSERT INTO feeds (rss_url, feed_name, last_post_id, last_post_pub)
VALUES ($1, $2, $3, $4)
RETURNING *;

-- name: update_post :exec
UPDATE feeds
    set last_post_id = $2,
    last_post_pub = $3,
    last_update = $4,
    last_completed = $4
WHERE feed_id = $1;

-- name: set_last_check_now :exec
UPDATE feeds
    set last_update = NOW()
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
