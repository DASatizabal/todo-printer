# HTTP Shortcuts Setup (Android)

Quick-add tasks from your phone home screen using the free [HTTP Shortcuts](https://play.google.com/store/apps/details?id=ch.rmy.android.http_shortcuts) app.

## Server URL

Replace `YOUR_SERVER_IP` with your workstation's local IP (e.g. `192.168.1.100`).

```
http://YOUR_SERVER_IP:8000
```

Find your IP: open a terminal and run `ipconfig`, look for your IPv4 address under your active adapter.

## Quick Personal Task

1. Open HTTP Shortcuts, tap **+** to create a new shortcut
2. Set **Name** to `Quick Personal`
3. Set **Method** to `POST`
4. Set **URL** to `http://YOUR_SERVER_IP:8000/api/quick-add?title={title}&category=personal&priority=2&source=self`
5. Go to **Advanced** > **Input** > Add a variable:
   - Variable name: `title`
   - Type: Text Input
   - Dialog title: "What needs to be done?"
6. Save and place on home screen

## Quick Work Task

Same as above, but change:
- **Name**: `Quick Work`
- **URL**: `http://YOUR_SERVER_IP:8000/api/quick-add?title={title}&category=work&priority=1&source=self`

## Quick School Task

Same as above, but change:
- **Name**: `Quick School`
- **URL**: `http://YOUR_SERVER_IP:8000/api/quick-add?title={title}&category=school&priority=2&source=self`

## Lisa's Quick Add

For Lisa's phone, so tasks show up with the "FROM LISA" tag:
- **Name**: `Add Task for David`
- **URL**: `http://YOUR_SERVER_IP:8000/api/quick-add?title={title}&category=personal&priority=2&source=lisa`

## API Reference

The `/api/quick-add` endpoint accepts these query parameters:

| Parameter  | Required | Default    | Options                        |
|------------|----------|------------|--------------------------------|
| `title`    | Yes      |            | Any text                       |
| `category` | No       | `personal` | `work`, `school`, `personal`   |
| `priority` | No       | `2`        | `1` (high), `2` (med), `3` (low) |
| `source`   | No       | `self`     | `self`, `lisa`, `calendar`     |
| `due_date` | No       |            | ISO date, e.g. `2026-04-01`   |
| `due_time` | No       |            | 24h time, e.g. `14:30`        |

## Tips

- The shortcuts work on the same Wi-Fi network as the server
- For access outside your home network, set up port forwarding or a VPN (Tailscale works great)
- You can add an icon to each shortcut to match the category colors
