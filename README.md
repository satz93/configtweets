# Said at Config India

Posts about Config India (Bengaluru, 15 Oct 2026) shown as conference badges you can flip through. Each badge
shows the post's text, the author's name and a link to the post on X.

## View it

Open `index.html` in a browser. The badges sit in a 3D stack: seen ones pile up on the left, upcoming ones
on the right. Scrolling (or swiping on a phone) moves the stack along with it, and when you stop it settles on
the next badge in that direction. The arrow keys step one badge at a time.

## Add the real posts

Edit `tweets.js`. Each post looks like this:

```js
{
  name: "Full Name",
  handle: "theirhandle",            // without the @
  date: "2026-10-15T10:12:00+05:30", // kept for reference, not shown
  text: "The post text…",
  url: "https://x.com/theirhandle/status/1234567890",
},
```
