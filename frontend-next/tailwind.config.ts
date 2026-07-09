import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        sidebar: {
          DEFAULT: "hsl(var(--sidebar-bg))",
          foreground: "hsl(var(--sidebar-fg))",
          accent: "hsl(var(--sidebar-accent))",
        },
        status: {
          compliant: "hsl(var(--status-compliant))",
          partial: "hsl(var(--status-partial))",
          noncompliant: "hsl(var(--status-noncompliant))",
          notfound: "hsl(var(--status-notfound))",
        },
      },
      fontFamily: {
        display: ["var(--font-quicksand)", "sans-serif"],
        body: ["var(--font-quicksand)", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "fade-in": {
          from: { opacity: "0", transform: "translateY(8px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        "slide-in-right": {
          from: { opacity: "0", transform: "translateX(16px)" },
          to: { opacity: "1", transform: "translateX(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "score-fill": {
          from: { width: "0%" },
          to: { width: "var(--score-width)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s ease-out forwards",
        "slide-in-right": "slide-in-right 0.4s ease-out forwards",
        shimmer: "shimmer 2s infinite linear",
        "score-fill": "score-fill 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards",
      },
    },
  },
  plugins: [],
};

export default config;
