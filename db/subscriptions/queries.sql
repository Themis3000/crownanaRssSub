-- name: get_subscription :one
select * from subscriptions
where subscriber_id = $1 limit 1;
