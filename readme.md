# Crownana rss subscription service

![coverage badge](https://github.com/Themis3000/crownanaRssSub/blob/coverage-badge/coverage.svg)

Years ago, Google took down their free service that allowed blog site operators to turn their rss feeds into easy email subscriptions via a widget.

This is my replacement solution. Made for my own personal site, but available for anyone running a small personal blog to use.

The setup is only 1 step. Just insert the following html code into your site, insert your rss feed url, and the rest handles it's self:

```html
<form action="https://rss.crownanabread.com/signup" method="post" target="_blank">
    <!-- Change the value field to your rss feed url -->
    <input type="hidden" name="rss_url" value="https://www.crownanabread.com/blog/rss.xml">
    Sign up for email notifications here:
    <br>
    <label>
        Email:
        <input type="text" name="email">
    </label>
    <br>
    Notify me up to once every:
    <br>
    <label>
        <input type="radio" name="notification_period" value="1d">
        1 day
    </label>
    <label>
        <input type="radio" name="notification_period" value="3d">
        3 days
    </label>
    <label>
        <input type="radio" name="notification_period" value="7d">
        7 days
    </label>
    <label>
        <input type="radio" name="notification_period" value="30d">
        30 days
    </label>
    <br>
    <input type="submit" value="Sign up">
</form>
```

Feel free to style it to match the theming of your website!

Complete with email confirmation on signup and a 1 click unsubscription process, users aren't able to abuse the subscription system and won't feel spammed by messages.

## Self-hosting

Self-hosting your own instance is supported, and instructions on how to do so are available on the home page here: [rss.crownanabread.com](https://rss.crownanabread.com)
