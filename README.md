# configtweets

Posts about Config India (Bengaluru, 15 Oct 2026) shown as conference badges you can flip through. Each badge
shows the post's text, the author's name and a link to the post on X.

## View it

Open `index.html` in a browser. Scroll (or swipe up on a phone) for the next badge: the current one slides
off the top and the next comes up from below. Scroll the other way, or use the arrow keys, to go back.

## The posts

`tweets.js` holds the 37 posts from the "Critical posts" tab of `Config_India_posts_15-19Oct2026_1.xlsx`
(Config India, 15–19 Oct 2026), with each author's display name taken from the "All posts" tab. Each post
looks like this:

```js
{
  name: "Full Name",
  handle: "theirhandle",            // without the @
  date: "2026-10-15T14:20:13+05:30",
  text: "The post text…",
  url: "https://x.com/theirhandle/status/1234567890",
  flag: "Negative",                 // the sheet's flag: Negative, Mixed or Borderline (not shown)
  why: "…",                         // the sheet's note on why it was flagged (not shown)
},
```

Long posts shrink their text until they fit the badge.

## Sharing

The site is a static page, so GitHub Pages can host it as is: **Settings → Pages → Deploy from a branch →
`claude/intelligent-fermi-mu0uz4`, folder `/ (root)`**. It then lives at <https://satz93.github.io/configtweets/> (the repo is named `configtweets`).

`index.html` carries the link-preview tags (title, description and `share.png`, 1200×630) that X, LinkedIn,
WhatsApp and Slack read. They point at that address; if the site moves, update the `og:url`, `og:image` and
`twitter:image` URLs.
