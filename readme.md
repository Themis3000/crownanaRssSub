# Work in progress!

Nearly completed, but not yet there. Will have a public instance hosted soon for small site owners & a docker image for those who want to run their own.

# Crownana rss subscription service

Years ago, Google took down their free service that allowed blog site operators to turn their rss feeds into easy email subscriptions via a widget.

This is my replacement solution. Made for my own site crownanabread.com, but available for anyone running a small personal blog to use. (made for use on the indeweb)

The setup is only 1 step. Just insert the html code into your site, and the rest handles it's self.

Complete with email confirmation on signup and a 1 click unsubscription process, users aren't able to abuse the subscription system and won't feel spammed by messages.

### A different approach to development

For this project, I decided to take an approach I haven't taken to development before. I've decided to give true test driven development a try. Usually when I work, I start with a MVP (minimum viable product), then work my way up from there with tests as an extra nice-to-have. This time around I've decided to build up something well thought out from the start and write tests for each essential piece as I go. Then, once everything is ready, I'll throw an http service in front of my already well-constructed and tested functions.