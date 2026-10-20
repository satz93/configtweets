# Said at Config India

Posts about Config India (Bengaluru, 15 Oct 2026) shown as conference badges you can flip through. Each badge
shows the post's text, who posted it and when, plus a QR code and link to the post on X.

## View it

Open `index.html` in a browser. Browse with the arrow buttons, the ← → keys, by swiping on a phone, or by
tapping the badge peeking out at either side.

## Add the real posts

Edit `tweets.js`. Each post looks like this:

```js
{
  name: "Full Name",
  handle: "theirhandle",            // without the @
  role: "Product Designer",         // optional
  date: "2026-10-15T10:12:00+05:30",
  text: "The post text…",
  url: "https://x.com/theirhandle/status/1234567890",
},
```

Set `window.SAMPLE = false` at the top of the file to hide the "Sample posts" label.
