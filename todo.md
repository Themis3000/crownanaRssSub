Major:
Make tests that fail, due to multiple posts having the same publish date.

Known bugs:
- If a user signs up and waits until after a new post has been made to confirm their email, they'll be notified of all posts made since signup *only after* a new post has been made after email confirmation. Example: user signs up on the 8th, 3 new posts are made, then the user confirms their email on the 15th. On the 25th a new post is made. The user now receives and email with all 4 posts at once. (rare edge-case)
- Trouble with two posts having the same publish time. Not sure what exactly the issue is yet, or the impact. But stuff breaks.

Other:
- Make youtube video about how to do it.
- Find some way to remove feeds with no subs (rare edge-case)
- Unsubscribe without notification on bounce (is this needed? does my email provider do this for me?)
