// Shared Tailwind configuration for all pages
// This ensures consistent styling across index.html, app.html, and policy.html

if (typeof tailwind !== 'undefined') {
  tailwind.config = {
    theme: {
      extend: {
        colors: {
          primary: '#007AFF', // Apple blue
          secondary: '#8E8E93', // Apple gray
        },
        fontFamily: {
          sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        },
        letterSpacing: {
          tighter: '-0.02em',
        }
      }
    }
  };
}

