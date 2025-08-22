# Cumulus Coding Website

A clean, modern, and minimalist business landing page for Cumulus Coding's mobile applications.

## Features

- **Responsive Design**: Mobile-friendly layout that works on all devices
- **Modern UI**: Clean, minimalist design using Tailwind CSS
- **Scalable**: Easy to add new apps and content
- **SEO Optimized**: Proper meta tags and semantic HTML
- **Privacy-Focused**: Aligns with the company's privacy-first approach

## File Structure

```
cumuluscoding.github.io/
├── index.html              # Homepage with app listings
├── app.html                # App details page template
├── styles.css              # Additional custom styles
├── README.md               # This documentation
├── HapticVibrationTimer/   # App-specific content
│   └── privacy-policy.md   # Privacy policy document
└── CNAME                   # Custom domain configuration
```

## Adding a New App

### 1. Update the Homepage (`index.html`)

Add a new app card in the apps section:

```html
<div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow duration-300">
  <div class="p-6">
    <div class="flex items-center mb-4">
      <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-xl flex items-center justify-center mr-4">
        <!-- Custom icon SVG here -->
        <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <!-- Your app icon path -->
        </svg>
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900">Your App Name</h3>
        <p class="text-sm text-gray-500">Platform (iOS/Android)</p>
      </div>
    </div>
    <p class="text-gray-600 mb-4 text-sm leading-relaxed">
      Brief description of your app.
    </p>
    <div class="flex flex-col space-y-2">
      <a href="app.html?app=your-app-id" 
         class="inline-flex items-center justify-center px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-colors duration-200">
        Learn More
        <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
        </svg>
      </a>
    </div>
  </div>
</div>
```

### 2. Update App Data (`app.html`)

Add your app to the `apps` object in the JavaScript section:

```javascript
const apps = {
  'haptic-timer': {
    // ... existing app
  },
  'your-app-id': {
    name: 'Your App Name',
    platform: 'iOS & Android',
    description: 'Detailed description of your app and its features.',
    icon: `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="YOUR_ICON_PATH"></path>`,
    downloads: [
      {
        name: 'App Store',
        url: 'https://apps.apple.com/app/your-app',
        icon: `<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>`,
        color: 'bg-black'
      },
      {
        name: 'Google Play',
        url: 'https://play.google.com/store/apps/details?id=your.app.id',
        icon: `<path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.61 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>`,
        color: 'bg-green-600'
      }
    ],
    privacy: 'YourApp/privacy-policy.md',
    terms: 'YourApp/terms-of-use.md'
  }
};
```

### 3. Create App-Specific Content

Create a folder for your app and add the necessary documents:

```
YourApp/
├── privacy-policy.md
├── terms-of-use.md
└── app-icon.png (optional)
```

## Customization

### Colors

The website uses a blue color scheme. To change colors, update the Tailwind config in both HTML files:

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: '#YOUR_COLOR', // Main brand color
        secondary: '#YOUR_SECONDARY_COLOR',
      }
    }
  }
}
```

### Typography

The website uses Inter font from Google Fonts. To change fonts, update the font import in the `<style>` section:

```css
@import url('https://fonts.googleapis.com/css2?family=YOUR_FONT:wght@300;400;500;600;700&display=swap');
body { font-family: 'YOUR_FONT', sans-serif; }
```

### Layout

The layout is responsive and uses CSS Grid and Flexbox. Key breakpoints:
- Mobile: `< 768px`
- Tablet: `768px - 1024px`
- Desktop: `> 1024px`

## SEO Optimization

The website includes:
- Proper meta tags (title, description, keywords)
- Semantic HTML structure
- Open Graph tags (can be added for social sharing)
- Structured data (can be added for rich snippets)

## Performance

- Uses Tailwind CSS CDN for fast loading
- Minimal JavaScript
- Optimized images (when added)
- No external dependencies beyond Tailwind

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Graceful degradation for older browsers

## Deployment

This website is designed for GitHub Pages. Simply push your changes to the repository and they will be automatically deployed.

## Maintenance

### Regular Tasks
1. Update app download links when they change
2. Add new apps following the documentation above
3. Update privacy policies and terms of use
4. Check for broken links
5. Update contact information if needed

### Adding Features
- Contact forms can be added using services like Formspree or Netlify Forms
- Analytics can be added (privacy-focused options recommended)
- Blog section can be added for updates
- Newsletter signup can be integrated

## Contact

For questions about this website or to report issues, contact: hello@cumuluscoding.com