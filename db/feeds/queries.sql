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

-- name: update_feed_post :exec
UPDATE feeds
    set last_post_id = $2,
    last_post_pub = $3,
    last_update = $4,
    last_completed = $4
WHERE feed_id = $1;

-- name: update_feed_check :exec
UPDATE feeds
    set last_update = $2
WHERE feed_id = $1;
