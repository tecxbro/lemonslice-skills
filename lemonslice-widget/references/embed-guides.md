# Widget Embed Guides

## Contents
- Basic HTML
- Next.js App Router
- TypeScript custom element declaration
- Shopify
- Squarespace
- Wix
- Common mistakes

## Basic HTML
```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

The LemonSlice agent must already exist in the LemonSlice web app. Platform embed guides assume the agent is available on the required LemonSlice plan.

* replace `AGENT_ID_HERE`
* `agent-id` is required
* script should be loaded once
* place near end of `<body>` for plain HTML
* do not expose API keys
* do not duplicate script/widget unless intentional

## Next.js App Router
For App Router:
* put widget in `app/layout.tsx`
* place inside `<body>` after `{children}`
* load script once
* do not put on every page
* add TypeScript custom-element declaration if needed

```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
        <lemon-slice-widget agent-id="AGENT_ID_HERE" />
        <script
          type="module"
          src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"
        />
      </body>
    </html>
  );
}
```

```ts
declare global {
  namespace JSX {
    interface IntrinsicElements {
      "lemon-slice-widget": {
        "agent-id": string;
        "initial-state"?: "minimized" | "active" | "hidden";
        "controlled-widget-state"?: "minimized" | "active" | "hidden";
        "custom-active-width"?: string;
        "custom-active-height"?: string;
        "custom-minimized-width"?: string;
        "custom-minimized-height"?: string;
        inline?: boolean;
        "hide-ui"?: boolean;
        "controlled-show-minimize-button"?: "true" | "false";
        "show-minimize-button"?: "true" | "false";
        "video-button-color-hex"?: string;
        "video-button-color-opacity"?: string;
      };
    }
  }
}

export {};
```

## Shopify
Shopify admin → Online Store → Themes → active theme → Edit code → layout/theme.liquid

Add the embed inside the `<body>` tag in `layout/theme.liquid`, before the first existing `<script>` tag.

```liquid
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

* do not paste in multiple snippets
* do not expose API keys
* use `theme.liquid` for site-wide widget
* use page/product template only if intentionally page-specific

## Squarespace
* use Code Injection
* site-wide injection for whole site
* page-level injection for one page
* Use Page Settings → Advanced → Page header code injection for the page-level embed. Verify on the live site because the widget may not display in editor preview.
* do not inject duplicate script
* do not expose API keys

```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```

## Wix
Wix Dashboard → Settings → Custom Code / Advanced Custom Code

* add the widget tag and script
* Recommended: select All pages and Load code once so the widget persists across pages. Avoid selecting only certain pages unless intentional, because the agent may restart when users navigate.
* publish the site
* verify live site
* avoid duplicate per-page embeds
* do not expose API keys

```html
<lemon-slice-widget agent-id="AGENT_ID_HERE"></lemon-slice-widget>
<script type="module" src="https://unpkg.com/@lemonsliceai/lemon-slice-widget"></script>
```
