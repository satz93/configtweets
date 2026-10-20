# Said at Config India

Posts about Config India (Bengaluru, 15 Oct 2026) shown as conference badges you can flip through. Each badge
shows the post's text, the author's name and handle, and a link plus a QR code that open the post on X.

## View it

Open `index.html` in a browser. Browse one badge at a time with the arrow buttons, the ← → keys, or by
swiping on a phone.

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

Set `window.SAMPLE = false` at the top of the file to hide the "Sample posts" label.
